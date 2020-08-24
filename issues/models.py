import markdown
from django.db import models
from django.urls import reverse

from triage.models import ProgrammingLanguage, IssueRate, COMPLEXITY_LEVEL


class Owner(models.Model):
    owner = models.CharField(max_length=200, primary_key=True, null=False)


class Repository(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null=False)

    class Meta:
        unique_together = (("owner", "name"),)


class Issue(models.Model):
    repository = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE)
    number = models.IntegerField(null=False)
    name = models.CharField(max_length=200)
    body = models.TextField()
    state = models.CharField(max_length=60)
    main_language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
    )
    current_rate = models.ForeignKey(IssueRate, null=True, default=None, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("repository", "number"),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_url(self) -> str:
        return reverse("issues:show", kwargs={
            "owner": self.repository.owner.owner,
            "repository": self.repository.name,
            "number": self.number
        })

    def get_rate_url(self) -> str:
        return reverse("issues:rate", kwargs={
            "owner": self.repository.owner.owner,
            "repository": self.repository.name,
            "number": self.number
        })

    def get_repository_name(self) -> str:
        return f'{self.repository.owner.owner}/{self.repository.name}'

    def get_owner_avatar(self):
        return f'https://github.com/{self.repository.owner.owner}.png?size=24'

    @property
    def rate_label(self):
        if self.current_rate is None:
            return 'Not rated yet'

        return self.current_rate.get_rate_display()

    @property
    def html(self):
        return markdown.markdown(self.body, extensions=['fenced_code'])

    @property
    def external_url(self):
        return f'https://github.com/{self.repository.owner.owner}/{self.repository.name}/issues/{self.number}'

    def rate(self, rate_number: int):
        rate = IssueRate.objects.get_or_create(rate=rate_number)[0]
        issue_rate = IssueRateRel.objects.create(issue=self, rate=rate)
        self.rates.add(issue_rate)

        self.current_rate = IssueRate.objects.get_or_create(
            rate=round(self._calculate_rate_sum() / self._total_rates())
        )[0]

    def _calculate_rate_sum(self) -> int:
        total = 0

        for rate in self.rates.all():
            total += rate.rate.rate

        return total

    def _total_rates(self) -> int:
        return len(self.rates.all())


class IssueRateRel(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='rates')
    rate = models.ForeignKey(IssueRate, on_delete=models.CASCADE)
