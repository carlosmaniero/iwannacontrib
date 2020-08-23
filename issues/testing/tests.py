import unittest

from django.test import TestCase
from github import Github

from issues.forms import CreateIssueForm
from issues.models import Issue, Repository, Owner
from issues.services.create_issue_service import IssueToBeCreated, InvalidGithubUrlException, CreateIssueService, \
    IssueNotFoundException, IssueAlreadyExists
from triage.models import ProgrammingLanguage


class IssueToBeCreatedTestCase(unittest.TestCase):
    def test_it_throws_an_exception_given_an_non_github_url(self):
        bitbucket_url = "http://bitbucket.com/carlosmaniero/issue/1"

        with self.assertRaises(InvalidGithubUrlException) as context:
            IssueToBeCreated(bitbucket_url)

        self.assertEquals(context.exception.url, bitbucket_url)

    def test_it_throws_an_exception_given_a_url_without_owner(self):
        github_url = "https://github.com/"

        with self.assertRaises(InvalidGithubUrlException) as context:
            IssueToBeCreated(github_url)

        self.assertEquals(context.exception.url, github_url)

    def test_it_throws_an_exception_given_a_url_without_a_repository(self):
        github_url = "https://github.com/carlosmaniero/jigjs/"

        with self.assertRaises(InvalidGithubUrlException) as context:
            IssueToBeCreated(github_url)

        self.assertEquals(context.exception.url, github_url)

    def test_it_throws_an_exception_given_a_url_without_an_issue_number(self):
        github_url = "https://github.com/carlosmaniero/jigjs/issues/"

        with self.assertRaises(InvalidGithubUrlException) as context:
            IssueToBeCreated(github_url)

        self.assertEquals(context.exception.url, github_url)

    def test_it_throws_an_exception_given_a_url_with_a_string_issue_number(self):
        github_url = "https://github.com/carlosmaniero/jigjs/issues/la"

        with self.assertRaises(InvalidGithubUrlException) as context:
            IssueToBeCreated(github_url)

        self.assertEquals(context.exception.url, github_url)

    def test_parses_the_url(self):
        github_url = "https://github.com/carlosmaniero/jigjs/issues/19"

        issue = IssueToBeCreated(github_url)
        self.assertEquals(issue.number, 19, 'issue id must be right')
        self.assertEquals(issue.repository, 'jigjs', 'repository must be right')
        self.assertEquals(issue.owner, 'carlosmaniero', 'owner must be right')


class CreateIssueServiceIntegrationTest(TestCase):
    def setUp(self) -> None:
        self.github = Github()

    def test_it_creates_an_issue(self) -> None:
        issue_to_be_created = IssueToBeCreated("https://github.com/carlosmaniero/iwannacontrib-issues-test"
                                               "-integration-test/issues/1")
        service = CreateIssueService()

        issue = service.create_issue(self.github, issue_to_be_created)

        self.assertEquals(issue.id, 1)
        self.assertEquals(issue.name, "Test Issue")
        self.assertEquals(issue.body, "This issue is used at project integration tests.")
        self.assertEquals(issue.repository.name, "iwannacontrib-issues-test-integration-test")
        self.assertEquals(issue.repository.owner.owner, "carlosmaniero")
        self.assertEquals(issue.main_language.name, "Python")

    def test_is_saves_the_issue(self) -> None:
        issue_to_be_created = IssueToBeCreated("https://github.com/carlosmaniero/iwannacontrib-issues-test"
                                               "-integration-test/issues/1")
        service = CreateIssueService()

        issue = service.create_issue(self.github, issue_to_be_created)
        self.assertEquals(Issue.objects.get(id=issue.id), issue)

    def test_it_throws_an_exception_given_a_not_found_issue(self) -> None:
        issues_url = "https://github.com/carlosmaniero/iwannacontrib-issues-test-integration-test/issues/666"
        issue_to_be_created = IssueToBeCreated(issues_url)
        service = CreateIssueService()

        with self.assertRaises(IssueNotFoundException) as context:
            service.create_issue(self.github, issue_to_be_created)

        self.assertEquals(context.exception.url, issues_url)

    def test_it_throws_an_exception_given_issue_already_exists(self) -> None:
        issue = Issue(
            number=1,
            name='any title',
            body='any body',
            main_language=ProgrammingLanguage.get_other_default_language(),
            repository=Repository.objects.create(
                name='iwannacontrib-issues-test-integration-test',
                owner=Owner.objects.create(owner='carlosmaniero')
            )
        )
        issue.save()

        issues_url = "https://github.com/carlosmaniero/iwannacontrib-issues-test-integration-test/issues/1"
        issue_to_be_created = IssueToBeCreated(issues_url)
        service = CreateIssueService()

        with self.assertRaises(IssueAlreadyExists) as context:
            service.create_issue(self.github, issue_to_be_created)

        self.assertEquals(context.exception.url, issues_url)


class FormIntegrationTest(TestCase):
    def test_it_is_invalid_given_an_non_issue_url(self):
        bitbucket_url = "http://bitbucket.com/carlosmaniero/lala"

        form = CreateIssueForm({
            "url": bitbucket_url
        })

        self.assertFalse(form.is_valid(), "Form must not be valid")
        self.assertEquals(
            form.errors['url'][0],
            "It must be a Github issue URL. Found: http://bitbucket.com/carlosmaniero/lala"
        )

    def test_it_is_invalid_given_no_url(self):
        form = CreateIssueForm({
            "url": None
        })

        self.assertFalse(form.is_valid(), "url is required")

    def test_it_is_invalid_given_empty_url(self):
        form = CreateIssueForm({
            "url": ""
        })

        self.assertFalse(form.is_valid(), "url is required")


class IssueModel(TestCase):
    def setUp(self) -> None:
        self.issue = Issue(
            number=1,
            name='any title',
            body='any body',
            main_language=ProgrammingLanguage.get_other_default_language(),
            repository=Repository.objects.create(
                name='iwannacontrib-issues-test-integration-test',
                owner=Owner.objects.create(owner='carlosmaniero')
            )
        )
        self.issue.save()

    def test_by_default_the_rate_level_is_not_rated(self):
        self.assertEquals(self.issue.rate_label, 'Not rated yet')

    def test_it_rates_the_issue_as_very_easy(self):
        self.issue.rate(1)
        self.assertEquals(self.issue.rate_label, 'Very Easy')

    def test_it_rates_the_issue_as_easy(self):
        self.issue.rate(2)
        self.assertEquals(self.issue.rate_label, 'Easy')

    def test_it_rates_the_issue_as_medium(self):
        self.issue.rate(3)
        self.assertEquals(self.issue.rate_label, 'Medium')

    def test_it_rates_the_issue_as_hard(self):
        self.issue.rate(4)
        self.assertEquals(self.issue.rate_label, 'Hard')

    def test_it_rates_the_issue_as_very_hard(self):
        self.issue.rate(5)
        self.assertEquals(self.issue.rate_label, 'Very Hard')

    def test_it_defines_the_current_rate_as_the_rate_avg(self):
        self.issue.rate(5)
        self.issue.rate(1)
        self.assertEquals(self.issue.rate_label, 'Medium')

    def test_it_rounds_the_avg(self):
        self.issue.rate(5)
        self.issue.rate(5)
        self.issue.rate(4)
        self.assertEquals(self.issue.rate_label, 'Very Hard')
