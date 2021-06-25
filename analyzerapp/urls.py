from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.main),
	url(r'^es$', views.es),
	url(r'^en$', views.en),
	url(r'^list$', views.list),
	url(r'^error-list$', views.error_list),
	url(r'^guide$', views.guide),
	url(r'^contact$', views.contact),
	url(r'^search$', views.github_search),
	url(r'^repo/(\d+)$', views.repo),
    #url(r'^pylint$', views.runPylint),
]
