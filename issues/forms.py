from django import forms
from django.core.exceptions import ValidationError

from issues.services.create_issue_service import IssueToBeCreated, InvalidGithubUrlException


class GithubUrlField(forms.Field):
    def to_python(self, value):
        if not value:
            return
        try:
            return IssueToBeCreated(value)
        except InvalidGithubUrlException as e:
            raise ValidationError(f"It must be a Github issue URL. Found: {e.url}")


class CreateIssueForm(forms.Form):
    url = GithubUrlField(required=True, label="Github Issue URL")
