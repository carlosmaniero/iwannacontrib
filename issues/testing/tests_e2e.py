from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from issues.testing.test_fixture import IssueFixture
from testing.e2e import E2ETesting, BasePageObject


class CreateIssuePageObject(BasePageObject):
    def fill_url(self, url) -> None:
        input_label = self.webdriver.find_element_by_css_selector('[for=id_url]')
        input_label.click()
        self.webdriver.switch_to.active_element.send_keys(url)

    def submit(self) -> None:
        self.webdriver.find_element_by_css_selector('input[type=submit]').click()

    def has_error(self) -> bool:
        try:
            self.webdriver.find_element_by_css_selector('.errorlist')
        except NoSuchElementException:
            return False
        return True


class IssuePageObject(BasePageObject):
    @property
    def issue_title(self) -> str:
        return self.webdriver.find_element_by_tag_name('h1').text

    @property
    def issue_body(self) -> str:
        return self.webdriver.find_element_by_id('issue-body').text

    @property
    def main_language(self) -> str:
        return self.webdriver.find_element_by_id('main_language').text

    @property
    def rate_level(self) -> str:
        return self.webdriver.find_element_by_css_selector('.issue-rate').text

    def rate(self, level: str):
        self.webdriver.find_element_by_css_selector(f'button[title="Rate as {level}"]').click()


class SearchPageObject(BasePageObject):
    @property
    def all_languages(self):
        language_select = self.webdriver.find_element_by_name('language')
        return [option.get_attribute("value") for option in language_select.find_elements_by_tag_name("option")]

    @property
    def all_rates(self):
        language_select = self.webdriver.find_element_by_name('rate')
        return [option.get_attribute("value") for option in language_select.find_elements_by_tag_name("option")]

    @property
    def results(self):
        results = self.webdriver.find_elements_by_css_selector('#result h1')
        return [result.text for result in results]

    def select_language(self, language):
        select = Select(self.webdriver.find_element_by_name('language'))
        select.select_by_visible_text(language)

    def select_rate(self, rate):
        select = Select(self.webdriver.find_element_by_name('rate'))
        select.select_by_visible_text(rate)

    def do_search(self):
        self.webdriver.find_element_by_tag_name('button').click()

    def click_at_result(self, link_text):
        self.webdriver.find_element_by_link_text(link_text).click()


class CreateIssueE2E(E2ETesting):
    def test_it_shows_an_error_given_an_invalid_input(self):
        self.fetch('/issues/create')
        create_issue_page_object = CreateIssuePageObject(self.webdriver)
        create_issue_page_object.fill_url("lala")
        create_issue_page_object.submit()
        self.assertTrue(create_issue_page_object.has_error())

    def test_renders_the_created_issue(self):
        self.fetch('/issues/create')
        create_issue_page_object = CreateIssuePageObject(self.webdriver)
        create_issue_page_object.fill_url(
            "https://github.com/carlosmaniero/iwannacontrib-issues-test-integration-test/issues/1"
        )
        create_issue_page_object.submit()

        issue_page = IssuePageObject(self.webdriver)
        self.assertEquals(issue_page.issue_title, 'Python Not rated yet #1 Test Issue')
        self.assertEquals(issue_page.issue_body, 'This issue is used at project integration tests.')
        self.assertEquals(issue_page.main_language, 'Python')
        self.assertEquals(issue_page.rate_level, 'Not rated yet')


class RatingIssueE2E(E2ETesting):
    def setUp(self) -> None:
        issue = IssueFixture().add()
        self.fetch(issue.get_url())
        self.issue_page = IssuePageObject(self.webdriver)

    def test_rates_issues_as_very_easy(self):
        self.assert_level('Very Easy')

    def test_rates_issues_as_easy(self):
        self.assert_level('Easy')

    def test_rates_issues_as_medium(self):
        self.assert_level('Medium')

    def test_rates_issues_as_hard(self):
        self.assert_level('Hard')

    def test_rates_issues_as_very_hard(self):
        self.assert_level('Very Hard')

    def test_it_shows_a_message_saying_that_the_vote_was_registered(self):
        self.issue_page.rate('Easy')
        self.assertEquals(self.issue_page.messages, ['You vote has been registered. Thank you for voting.'])

    def assert_level(self, level):
        self.issue_page.rate(level)
        self.assertEquals(self.issue_page.rate_level, level)


class SearchIssueE2E(E2ETesting):
    def setUp(self) -> None:
        IssueFixture().add()
        self.fetch('/')
        self.issue_page = IssuePageObject(self.webdriver)
        self.search_page = SearchPageObject(self.webdriver)

    def test_has_all_filters(self):
        self.assertEquals(self.search_page.all_languages, ['', 'Python'])
        self.assertEquals(self.search_page.all_rates, ['', 'all', '1', '2', '3', '4', '5'])

    def test_default_seo_information(self):
        self.assertEquals(self.search_page.page_title, 'Be a contributor to open source | Contrib World')
        self.assertEquals(
            self.search_page.meta_description,
            'Find an issue that is perfect with your skills and contribute to open source projects.'
        )

    def test_search_seo_information(self):
        self.search_page.select_language('Python')
        self.search_page.select_rate('Not Rated')
        self.search_page.do_search()

        self.assertEquals(self.search_page.page_title, 'Let me contrib with Python to Open Source | Contrib World')

        self.assertEquals(
            self.search_page.meta_description,
            'Find an Python issue that is perfect with your skills and contribute to open source projects.'
        )

    def test_search_journey(self):
        self.search_page.select_language('Python')
        self.search_page.select_rate('Not Rated')

        self.search_page.do_search()
        self.assertEquals(self.search_page.results, ['Python Not rated yet #1 any title 1'])

        self.search_page.click_at_result('Python Not rated yet #1 any title 1')

        self.assertEquals(self.issue_page.page_title, 'Contrib to a Python issue: any title 1 | Contrib World')
        self.assertEquals(
            self.issue_page.meta_description,
            'The Python repository iwannacontrib-issues-test-integration-test needs your help. Contribute to any '
            'title 1.'
        )
        self.assertEquals(self.issue_page.issue_title, 'Python Not rated yet #1 any title 1')
        self.assertEquals(self.issue_page.issue_body, 'any body')
        self.assertEquals(self.issue_page.main_language, 'Python')
