from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.main),
	url(r'^list$', views.list),
	url(r'^search$', views.github_search),
    #url(r'^pylint$', views.runPylint),
]
