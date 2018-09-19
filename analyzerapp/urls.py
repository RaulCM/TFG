from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.holamundo),
    url(r'^search$', views.githubSearch),
    #url(r'^pylint$', views.runPylint),
]
