from django.db import models

# Create your models here.
#https://docs.djangoproject.com/en/2.1/topics/db/models/

class Repository(models.Model):
    identifier = models.CharField(max_length=150, default="Null")
    full_name = models.TextField(default="Null")
    owner = models.TextField(default="Null")
    name = models.TextField(default="Null")
    description = models.TextField(default="Null")
    html_url = models.URLField(max_length=350, default="Null")
    api_url = models.URLField(max_length=350, default="Null")
    fork_url = models.URLField(max_length=350, default="Null")
    fork_api_url = models.URLField(max_length=350, default="Null")
    default_branch = models.TextField(default="Null")
    pull_url = models.URLField(max_length=350, default="Null")
    pull_api_url = models.URLField(max_length=350, default="Null")
    pull_url_status = models.TextField(default="Null")

class Errors(models.Model):
    error_id = models.CharField(max_length=150, default="Null", primary_key=True)
    name = models.TextField(default="Null")
    message = models.TextField(default="Null")
    fixable = models.BooleanField(default=False)

class Fixed_errors_repo(models.Model):
    error_id = models.ForeignKey(Errors, on_delete=models.CASCADE)
    identifier = models.ForeignKey(Repository, on_delete=models.CASCADE)

class Fixed_errors_count(models.Model):
    error_id = models.ForeignKey(Errors, on_delete=models.CASCADE, primary_key=True)
    count = models.IntegerField(default=0)

class All_errors_repo(models.Model):
    error_id = models.ForeignKey(Errors, on_delete=models.CASCADE)
    identifier = models.ForeignKey(Repository, on_delete=models.CASCADE)

class All_errors_count(models.Model):
    error_id = models.ForeignKey(Errors, on_delete=models.CASCADE, primary_key=True)
    count = models.IntegerField(default=0)
