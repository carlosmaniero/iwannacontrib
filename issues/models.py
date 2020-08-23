from django.db import models


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

    class Meta:
        unique_together = (("repository", "number"),)
