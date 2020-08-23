from issues.models import Issue, Repository, Owner
from triage.models import ProgrammingLanguage


class IssueFixture:
    def __init__(self):
        self.issue_number = 0

    def add(self, language_name='Python', **rewrite):
        self.issue_number += 1

        data = dict(
            number=self.issue_number,
            name=f'any title {self.issue_number}',
            body='any body',
            main_language=ProgrammingLanguage.objects.get_or_create(name=language_name)[0],
            repository=Repository.objects.get_or_create(
                name='iwannacontrib-issues-test-integration-test',
                owner=Owner.objects.get_or_create(owner='carlosmaniero')[0]
            )[0]
        )

        data.update(**rewrite)

        issue = Issue(
            **data
        )

        issue.save()

        return issue
