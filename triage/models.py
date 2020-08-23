from django.db import models


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_other_default_language():
        return ProgrammingLanguage.objects.get_or_create(name='Other')[0]


COMPLEXITY_LEVEL = [
    (1, 'Very Easy'),
    (2, 'Easy'),
    (3, 'Medium'),
    (4, 'Hard'),
    (5, 'Very Hard'),
]


class IssueRate(models.Model):
    rate = models.IntegerField(choices=COMPLEXITY_LEVEL)
