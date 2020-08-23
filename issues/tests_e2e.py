from selenium.common.exceptions import NoSuchElementException

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
        return self.webdriver.find_element_by_id('rate_label').text

    def rate(self, level: str):
        self.webdriver.find_element_by_css_selector(f'button[title="Rate as {level}"]').click()


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
        self.assertTrue(issue_page.issue_title, 'Test Issue')
        self.assertEquals(issue_page.issue_body, 'This issue is used at project integration tests.')
        self.assertEquals(issue_page.main_language, 'Python')
        self.assertEquals(issue_page.rate_level, 'Not rated yet')


class RatingIssueE2E(E2ETesting):
    def setUp(self) -> None:
        self.fetch('/issues/create')
        create_issue_page_object = CreateIssuePageObject(self.webdriver)
        create_issue_page_object.fill_url(
            "https://github.com/carlosmaniero/iwannacontrib-issues-test-integration-test/issues/1"
        )
        create_issue_page_object.submit()

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

    def assert_level(self, level):
        self.issue_page.rate(level)
        self.assertEquals(self.issue_page.rate_level, level)
