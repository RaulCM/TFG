from django.shortcuts import render
from django.http import HttpResponse
from analyzerapp.models import Repository
from django.template.loader import get_template
from django.template import RequestContext
import requests, json
import os
# Create your views here.

def main(request):
    #githubClone()
    update()
    template = get_template("main.html")
    c = RequestContext(request, {'datos': printData()})
    response = template.render(c)
    return HttpResponse(response)

def printData():
    datos = Repository.objects.all()
    return(datos)

def update():
    url = 'https://api.github.com/repos/'
    datos = Repository.objects.all()
    for item in datos:
        full_name = item.full_name
        r = requests.get(url + full_name + token())
        json_data = r.json()
        try:
            modified = False
            if item.name == "Null":
                item.name = json_data["owner"]["login"]
                modified = True
            if item.owner == "Null":
                item.owner = json_data["name"]
                modified = True
            if modified is True:
                item.save()
        except KeyError as e:
            pass



def storeData(json_data):
    for item in json_data:
        try:
            Repository.objects.get(identifier=item["id"])
        except Repository.DoesNotExist:
            repository = Repository()
            repository.identifier = item["id"]
            repository.full_name = item["full_name"]
            repository.owner = item["owner"]["login"]
            repository.name = item["name"]
            if item["description"] is not None:
                repository.description = item["description"]
            repository.html_url = item["html_url"]
            repository.save()


def githubClone():
    datos = Repository.objects.all()
    #datos = Repository.objects.all().filter(corrected=0)
    for item in datos:
        url = item.html_url + ".git"
        name = item.full_name
        os.system('git clone ' + url + " /var/tmp/" + name)

def token():
    # https://developer.github.com/v3/#rate-limiting
    filename = "token"
    if os.path.isfile(filename):
        s = open(filename, 'r').read()
        token = '?access_token=' + s.rstrip()
    else:
        token = ""
    return token


def githubSearch(request):

    url = 'https://api.github.com/search/repositories'
    #https://developer.github.com/v3/search/#search-repositories
    #https://help.github.com/articles/understanding-the-search-syntax/
    queries = token()
    queries += '+q=python3'      #Que contengan el string "python3"
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
