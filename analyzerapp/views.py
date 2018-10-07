from django.shortcuts import render
from django.http import HttpResponse
import os
# https://docs.python.org/2/library/os.html
import json
import requests
from analyzerapp.models import Repository
from django.template.loader import get_template
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import pylint
# Create your views here.

@csrf_exempt
def main(request):
    if request.method == "GET":
        template = get_template("main.html")
        c = RequestContext(request)
        response = template.render(c)
    elif request.method == "POST":
        form_name = request.body.decode('utf-8').split("=")[0]
        if form_name == "load":
            github_search()
        elif form_name == "update":
            update()
        elif form_name == "add":
            print("Añadir repositorio único")
        elif form_name == "clone":
            github_clone()
        elif form_name == "pylint":
            # read_files()
            run_pylint()
        template = get_template("main.html")
        c = RequestContext(request)
        response = template.render(c)
    else:
        template = get_template("error.html")
        c = RequestContext(request, {'error_message': '405: Method not allowed'})
        response = template.render(c)
    return HttpResponse(response)

def list(request):
    template = get_template("list.html")
    c = RequestContext(request, {'datos': print_data()})
    response = template.render(c)
    return HttpResponse(response)

def print_data():
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

def store_data(json_data):
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

def github_clone():
    datos = Repository.objects.all()
    #datos = Repository.objects.all().filter(corrected=0)
    for item in datos:
        url = item.html_url + ".git"
        name = item.full_name
        os.system('git clone ' + url + " /tmp/projects/" + name)

def token():
    # https://developer.github.com/v3/#rate-limiting
    filename = "token"
    if os.path.isfile(filename):
        s = open(filename, 'r').read()
        token = '?access_token=' + s.rstrip()
    else:
        token = ""
    return token


def github_search(request):
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
    store_data(json_data)
    json_pretty = json.dumps(json_data, sort_keys=True, indent=4)
    return HttpResponse(json_pretty,content_type="text/json")

def run_pylint():
    fichero = 'analyzerapp/views.py'
    print(os.path.exists(fichero))
    # pylint.run_pylint
    os.system('pylint ' + fichero + " --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' | grep -e '[[]C' -e '[[]E' -e '[[]F' -e '[[]I' -e '[[]R' -e '[[]W'")
    # https://docs.pylint.org/en/1.6.0/output.html
    # pylint analyzerapp/views.py --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' | grep -e C0103 -e C0111

def read_files():
    for root, dirs, files in os.walk("/tmp/projects/", topdown=False):
        for name in files:
            ext = os.path.splitext(name)[-1].lower()
            # print(ext)
            if ext == ".py":
                print(os.path.join(root, name))
        # for name in dirs:
        #     print(os.path.join(root, name))
