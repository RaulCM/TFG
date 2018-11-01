from django.shortcuts import render
from django.http import HttpResponse
import os
# https://docs.python.org/2/library/os.html
import json
import requests
from analyzerapp.models import Repository, Errors
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
            # run_pylint()
            read_errors()
        elif form_name == "fork":
            make_fork('https://api.github.com/repos/RaulPruebasTFG/helloworld')
        elif form_name == "delete_fork":
            delete_fork('https://api.github.com/repos/RaulCM/helloworld')
        elif form_name == "pull":
            create_pull('https://api.github.com/repos/RaulPruebasTFG/helloworld')
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
        r = requests.get(url + full_name + '?access_token=' + read_file("token"))
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

def read_file(filename):
    # https://developer.github.com/v3/#rate-limiting
    if os.path.isfile(filename):
        s = open(filename, 'r').read()
        string = s.rstrip()
    else:
        string = ""
    return string


def github_search(request):
    url = 'https://api.github.com/search/repositories'
    #https://developer.github.com/v3/search/#search-repositories
    #https://help.github.com/articles/understanding-the-search-syntax/
    queries = '?access_token=' + read_file("token")
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
    # https://docs.pylint.org/en/1.6.0/output.html
    fichero = 'analyzerapp/views.py'
    print(os.path.exists(fichero))
    # os.system('pylint ' + fichero + " --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' | grep -e '[[]C' -e '[[]E' -e '[[]F' -e '[[]I' -e '[[]R' -e '[[]W'")
    os.system('pylint ' + fichero + " --msg-template='{msg_id}' --reports=n >> /tmp/pylint_output")

def read_files():
    for root, dirs, files in os.walk("/tmp/projects/", topdown=False):
        for name in files:
            ext = os.path.splitext(name)[-1].lower()
            if ext == ".py":
                os.system('pylint ' + os.path.join(root, name) + " --msg-template='{msg_id}' --reports=n >> /tmp/pylint_output")

def read_errors():
    for line in open('/tmp/pylint_output'):
        if line[0] != "*":
            error_id = line[:-1]
            try:
                error = Errors.objects.get(error_id=error_id)
                error.count = error.count + 1
                error.save()
            except Errors.DoesNotExist:
                error = Errors()
                error.error_id = error_id
                error.count = 0
                error.save()

def make_fork(url):
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    r = s.post(url + '/forks')
    print(r)

def delete_fork(url):
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    r = s.delete(url)
    print(r)

def create_pull(url):
    url += '/pulls'
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    data = {"title": "Amazing new feature",
            "body": "Please pull this in!",
            "head": "RaulCM:pylint",
            "base": "master"}
    data = json.dumps(data)
    r = s.post(url = url, data = data)
    print(r.json())
