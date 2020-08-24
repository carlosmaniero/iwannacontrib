from django.test import TestCase

from issues.testing.test_fixture import IssueFixture
from triage.forms import SearchForm


class SearchFormTesting(TestCase):
    def test_it_filter_the_right_language(self):
        fixture = IssueFixture()

        python_issue = fixture.add(language_name='Python')
        fixture.add(language_name='Java')

        form = SearchForm({
            "language": python_issue.main_language,
        })

        self.assertEquals(list(form.results), [python_issue])

    def test_it_filter_the_right_rate(self):
        fixture = IssueFixture()

        easy_issue = fixture.add(language_name='Python')
        easy_issue.rate(1)
        easy_issue.save()

        fixture.add(language_name='Python')

        form = SearchForm({
            "language": easy_issue.main_language,
            "rate": 1
        })

        self.assertEquals(list(form.results), [easy_issue])

    def test_it_filter_all_rates(self):
        fixture = IssueFixture()

        easy_issue = fixture.add(language_name='Python')
        easy_issue.rate(1)
        easy_issue.save()

        not_rated_issue = fixture.add(language_name='Python')

        form = SearchForm({
            "language": easy_issue.main_language,
            "rate": 'all'
        })

        self.assertEquals(list(form.results), [not_rated_issue, easy_issue])

    def test_it_returns_the_20_latest_added_by_default(self):
        fixture = IssueFixture()

        all_issues = [fixture.add() for i in range(30)]

        form = SearchForm()

        self.assertEquals(len(form.results), 20)
        self.assertEquals(list(form.results), list(reversed(all_issues))[0:20])
