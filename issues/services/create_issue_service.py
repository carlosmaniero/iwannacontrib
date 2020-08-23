import re

from github import Github

from issues.models import Issue, Repository, Owner


class InvalidGithubUrlException(Exception):
    def __init__(self, url: str):
        self.url = url
        super()


class IssueNotFoundException(Exception):
    def __init__(self, url: str):
        self.url = url
        super()


class IssueAlreadyExists(Exception):
    def __init__(self, url: str):
        self.url = url
        super()


class IssueToBeCreated:
    def __init__(self, url: str):
        self.url = url
        self._parse_url()

    def _parse_url(self):
        paths = self._path_for()

        match = re.search("^(.+)/(.+)/issues/(\\d+)", paths, re.IGNORECASE)

        if not match:
            raise InvalidGithubUrlException(self.url)

        self.number = int(match.group(3))
        self.repository = match.group(2)
        self.owner = match.group(1)

    def _path_for(self):
        url_without_protocol = self.url.replace('https://', '').replace('http://', '')
        if not url_without_protocol.startswith('github.com'):
            raise InvalidGithubUrlException(self.url)
        paths = url_without_protocol.replace('github.com/', '')
        return paths

    def get_repo_path(self) -> str:
        return f"{self.owner}/{self.repository}"


class CreateIssueService:
    def create_issue(self, github: Github, issue_to_be_created: IssueToBeCreated) -> Issue:
        github_issue = self._get_github_issue(github, issue_to_be_created)

        repository = Repository.objects.get_or_create(
            name=issue_to_be_created.repository,
            owner=Owner.objects.get_or_create(owner=issue_to_be_created.owner)[0]
        )[0]

        if len(repository.issue_set.filter(number=issue_to_be_created.number)) != 0:
            raise IssueAlreadyExists(issue_to_be_created.url)

        issue = Issue(
            number=issue_to_be_created.number,
            name=github_issue.title,
            body=github_issue.body,
            repository=repository
        )
        issue.save()
        return issue

    def _get_github_issue(self, github: Github, issue_to_be_created: IssueToBeCreated):
        try:
            repo = github.get_repo(issue_to_be_created.get_repo_path(), lazy=True)
            return repo.get_issue(issue_to_be_created.number)
        except Exception:
            raise IssueNotFoundException(issue_to_be_created.url)
