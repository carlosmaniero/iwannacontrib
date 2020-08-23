import unittest

from django.test import TestCase, LiveServerTestCase
from github import Github
from prompt_toolkit.keys import Keys
from selenium import webdriver

from issues.forms import CreateIssueForm
from issues.models import Issue, Repository, Owner
from issues.services.create_issue_service import IssueToBeCreated, InvalidGithubUrlException, CreateIssueService, \
    IssueNotFoundException, IssueAlreadyExists
from testing.e2e import E2ETesting


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


class CreateIssueE2E(E2ETesting):
    def testInitialForm(self):
        self.webdriver.get('http://127.0.0.1:8000/issues/create')

        input_label = self.webdriver.find_element_by_css_selector('[for=id_url]')

        self.assertEquals(input_label.text, 'Github Issue URL:')
