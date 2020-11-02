from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
# https://docs.python.org/2/library/os.html
import json
import requests
from analyzerapp.models import Repository, Errors
from django.template.loader import get_template
# from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import pylint
from urllib.parse import unquote
import subprocess
from analyzerapp import pylint_errors
# Create your views here.

@csrf_exempt
def main(request):
    if request.method == "GET":
        return render(request, 'main.html')
    elif request.method == "POST":
        form_name = request.body.decode('utf-8').split("=")[0]
        if form_name == "add":
            url = unquote(request.body.decode('utf-8').split("=")[1])
            api_url = url.replace('://github.com/', '://api.github.com/repos/')
            r = requests.get(api_url)
            repo_data = r.json()
            store_individual_data(repo_data)
            return redirect('/repo/' + str(repo_data['id']))
        # elif form_name == "load":
        #     github_search()
        # elif form_name == "update":
        #     update()
        # elif form_name == "clone":
        #     github_clone()
        # elif form_name == "pylint":
            # read_files()
            # run_pylint()
        #     read_errors()
        # elif form_name == "fork":
        #     make_fork('https://api.github.com/repos/RaulPruebasTFG/helloworld')
        # elif form_name == "delete_fork":
        #     delete_fork('https://api.github.com/repos/RaulCM/helloworld')
        # elif form_name == "pull":
        #     create_pull('https://api.github.com/repos/RaulPruebasTFG/helloworld')
        return render(request, 'main.html')
    else:
        return render(request, 'error.html', {'error_message': '405: Method not allowed'})
    # return HttpResponse(response)

@csrf_exempt
def repo(request, resource):
    repository = Repository.objects.get(identifier=resource)
    if request.method == "GET":
        return render(request, 'repo_data.html', {'repository': repository})
    elif request.method == "POST":
        fixables = 0
        form_name = request.body.decode('utf-8').split("=")[0]
        if form_name == "pylint":
            github_clone_individual(repository)
            pylint_output = analyze_repo(repository)
            pylint_output = pylint_output.replace('/tmp/projects/', '/').split('\n')
            return render(request, 'repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'fixables': fixables})
        elif form_name == "fixables":
            fixables = 1
            pylint_output = analyze_repo(repository)
            pylint_output = pylint_output.replace('/tmp/projects/', '/').split('\n')
            pylint_output[:] = [x for x in pylint_output if ("C0303" in x or "C0304" in x or "C0321" in x or "C0326" in x or "W0404" in x or "C0410" in x or "C0411" in x or "C0413" in x or "W0611" in x)]
            return render(request, 'repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'fixables': fixables})
        elif form_name == "all":
            pylint_output = analyze_repo(repository)
            pylint_output = pylint_output.replace('/tmp/projects/', '/').split('\n')
            return render(request, 'repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'fixables': fixables})
        elif form_name == "fix":
        # TODO Proceso pull-request:
            # 1. Fork del repo -> Hay que sacar la URL para clonar
            make_fork(repository)
            # 2. Clone del fork
            # 3. Crear branch (git checkout -b new_branch)
            github_clone_fork(repository)
            # 4. Hacer cambios
            pylint_output = analyze_repo(repository)
            pylint_output = pylint_output.split('\n')
            pylint_output = pylint_output[:-1]
            for line in pylint_output:
                if line[0] == "/":
                    tokens = line.split(';')
                    error = pylint_errors.Error(tokens)
                    pylint_errors.check(error)
            files = []
            for line in pylint_output:
                if line[0] == "/":
                    filename = line.split(';')[0]
                    if filename not in files:
                        files.append(filename)
            for file in files:
                pylint_errors.check_placeholders(file)
            # 5. Commit
            # 6. Push
            # 7. Crear Pull-Request
            return render(request, 'repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'fixables': fixables})
    else:
        return render(request, 'error.html', {'error_message': '405: Method not allowed'})

def list(request):
    return render(request, 'list.html', {'datos': print_data()})

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
        store_individual_data(item)

def store_individual_data(item):
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
        repository.api_url = item["url"]
        repository.save()

def github_clone():
    datos = Repository.objects.all()
    #datos = Repository.objects.all().filter(corrected=0)
    for item in datos:
        github_clone_individual(item)

def github_clone_individual(item):
    url = item.html_url + ".git"
    name = item.full_name
    os.system('git clone ' + url + " /tmp/projects/" + name)

def github_clone_fork(item):
    url = item.fork_url + ".git"
    name = item.full_name
    current_dir = os.getcwd()
    os.system('rm -rfv ' + "/tmp/projects/" + name)
    os.system('git clone ' + url + " /tmp/projects/" + name)
    os.chdir("/tmp/projects/" + name)
    os.system('git checkout -b pylint_errors')
    os.chdir(current_dir)

def analyze_repo(item):
    # https://docs.pylint.org/en/1.6.0/output.html
    # https://docs.python.org/2/library/subprocess.html
    path = "/tmp/projects/" + item.full_name
    pylint_output = ""
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            ext = os.path.splitext(name)[-1].lower()
            if ext == ".py":
                try:
                    output = subprocess.check_output(['pylint', os.path.join(root, name), "--msg-template='{abspath};{line};{column};{msg_id};{msg}'", "--reports=n"])
                except subprocess.CalledProcessError as e:
                    pylint_output = pylint_output + e.output.decode("utf-8")
    return pylint_output

def read_file(filename):
    # https://developer.github.com/v3/#rate-limiting
    if os.path.isfile(filename):
        s = open(filename, 'r').read()
        string = s.rstrip()
    else:
        string = ""
    return string

def make_fork(repository):
    url = repository.api_url
    url += '/forks'
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    r = s.post(url)
    repository.fork_url = r.json()["html_url"]
    repository.fork_api_url = r.json()["url"]
    repository.save()

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
    # --msg-template='{abspath}:{line}:{msg_id}' --reports=n
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

def delete_fork(url):
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    r = s.delete(url)
    print(r)

def create_pull(url):
    # https://developer.github.com/v3/pulls/
    url += '/pulls'
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    data = {"title": "Amazing new feature",
            "body": "Please pull this in!",
            "head": "RaulCM:pylint",
            "base": "master"}
    data = json.dumps(data)
    r = s.post(url, data)
    print(r.json())

def get_pulls(url):
    url += '/pulls?state=all'
    s = requests.Session()
    s.auth = (read_file("username"), read_file("password"))
    r = s.get(url)
    return r.json()

def pull_state(url):
    json_data = get_pulls(url)
    state = ""
    for item in json_data:
        label = item['head']['label']
        print(label)
        if label == 'RaulCM:pylint':
            state = item['state']
    return state
