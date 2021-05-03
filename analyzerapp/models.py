from django.db import models

# Create your models here.
#https://docs.djangoproject.com/en/2.1/topics/db/models/

class Repository(models.Model):
    identifier = models.CharField(max_length=150, default="Null", primary_key=True)
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

    # "clone_url": "https://github.com/MUSSLES/sspipeline.git",
    # "created_at": "2018-08-17T20:35:11Z",
    # "language": "Python",
    # "node_id": "MDEwOlJlcG9zaXRvcnkxNDUxNjQzMTc=",
    # "pulls_url": "https://api.github.com/repos/MUSSLES/sspipeline/pulls{/number}",
    # "releases_url": "https://api.github.com/repos/MUSSLES/sspipeline/releases{/id}",

class Errors(models.Model):
    error_id = models.CharField(max_length=150, default="Null", primary_key=True)
    count = models.IntegerField(default=0)
