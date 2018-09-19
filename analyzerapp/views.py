from django.shortcuts import render
from django.http import HttpResponse
from analyzerapp.models import Repository
import requests, json
import os
# Create your views here.

def holamundo(request):
    return HttpResponse("Hola Mundo")

def storeData(json_data):
    for item in json_data:
        try:
            Repository.objects.get(identifier=item["id"])
        except Repository.DoesNotExist:
            repository = Repository()
            repository.identifier = item["id"]
            repository.full_name = item["full_name"]
            if item["description"] is not None:
                repository.description = item["description"]
            repository.html_url = item["html_url"]
            repository.save()

def githubSearch(request):

    url = 'https://api.github.com/search/repositories'
    #https://developer.github.com/v3/search/#search-repositories
    #https://help.github.com/articles/understanding-the-search-syntax/
    queries = '?q=python3'      #Que contengan el string "python3"
    queries += '+language:python'    #Solo lenguaje Python
    queries += '+archived:false'    #Repositorios no archivados
    queries += '+created:>2018-06-01'    #Fecha posterior a YYYY:MM:DD
    queries += '+topics:>3'            #Numero de topics mayor a X
    queries += '&sort=updated'        #Ordenados por fecha de actualizacion

    url = url + queries
    r = requests.get(url)

    json_data = r.json()
    json_data = json_data["items"]
    storeData(json_data)

    json_pretty = json.dumps(json_data, sort_keys=True, indent=4)


    #pprint.pprint(r.json())
    #return HttpResponse(json_pretty,content_type="application/json")

    return HttpResponse(json_pretty,content_type="text/json")
