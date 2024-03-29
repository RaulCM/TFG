from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
# https://docs.python.org/2/library/os.html
import json
import requests
from analyzerapp.models import Repository, Errors, Fixed_errors_repo, Fixed_errors_count, All_errors_repo, All_errors_count
from django.template.loader import get_template
# from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import pylint
from urllib.parse import unquote
import subprocess
from analyzerapp import pylint_errors
import after_response
import time
from django.utils.translation import LANGUAGE_SESSION_KEY

pull_body_header = ('Your code has been analyzed by [PEP-Analyzer]' +
            '(https://pep-analyzer.herokuapp.com/) using Pylint tool' +
            ' to adapt it to [PEP8, the Python style guide]' +
            '(https://www.python.org/dev/peps/pep-0008/).  \n' +
            'These are the pylint errors fixed in your code:  \n')
pull_body = ''

@csrf_exempt
def main(request):
    language = request.session.get(LANGUAGE_SESSION_KEY)
    if request.method == 'GET':
        update()
        if language == 'en':
            return render(request, 'en/main.html')
        else:
            return render(request, 'main.html')
    elif request.method == 'POST':
        form_name = request.body.decode('utf-8').split('=')[0]
        if form_name == 'add':
            url = unquote(request.body.decode('utf-8').split('=')[1])
            if len(url) == 0:
                if language == 'en':
                    return render(request, 'en/error.html', {'error_message': 'No data has been entered in the form.'})
                else:
                    return render(request, 'error.html', {'error_message': 'No se ha introducido ningún dato en el formulario'})
            if url[-1] == '/':
                url = url[:-1]
            if 'github' in url:
                api_url = url.replace('://github.com/', '://api.github.com/repos/')
                r = requests.get(api_url)
                repo_data = r.json()
                try:
                    repository = Repository.objects.filter(pull_url_status='open').get(identifier=repo_data['id'])
                    if language == 'en':
                        return render(request, 'en/request_exists.html', {'repository': repository})
                    else:
                        return render(request, 'request_exists.html', {'repository': repository})
                except Repository.DoesNotExist:
                    try:
                        store_individual_data(repo_data)
                    except KeyError:
                        if language == 'en':
                            return render(request, 'en/error_repo.html', {'url': url})
                        else:
                            return render(request, 'error_repo.html', {'url': url})
            elif 'gitlab.etsit.urjc.es' in url:
                api_url = 'https://gitlab.etsit.urjc.es/api/v4/projects/' + url.split('gitlab.etsit.urjc.es/')[-1].rstrip('/').replace('/', '%2F')
                r = requests.get(api_url, headers={"PRIVATE-TOKEN": os.environ['tokengitlab']})
                repo_data = r.json()
                try:
                    repository = Repository.objects.filter(pull_url_status='opened').get(identifier=repo_data['id'])
                    if language == 'en':
                        return render(request, 'en/request_exists.html', {'repository': repository})
                    else:
                        return render(request, 'request_exists.html', {'repository': repository})
                except Repository.DoesNotExist:
                    try:
                        store_individual_data_gitlab(repo_data)
                    except KeyError:
                        if language == 'en':
                            return render(request, 'en/error_repo.html', {'url': url})
                        else:
                            return render(request, 'error_repo.html', {'url': url})
            else:
                if language == 'en':
                    return render(request, 'en/error_repo.html', {'url': url})
                else:
                    return render(request, 'error_repo.html', {'url': url})
            return redirect('/repo/' + str(repo_data['id']))
        if language == 'en':
            return render(request, 'en/main.html')
        else:
            return render(request, 'main.html')
    else:
        if language == 'en':
            return render(request, 'en/error.html', {'error_message': '405: Method not allowed'})
        else:
            return render(request, 'error.html', {'error_message': '405: Método no permitido'})

@csrf_exempt
def repo(request, resource):
    language = request.session.get(LANGUAGE_SESSION_KEY)
    repository = Repository.objects.filter(pull_url_status='Null').get(identifier=resource)
    if request.method == 'GET':
        if language == 'en':
            return render(request, 'en/repo_data.html', {'repository': repository})
        else:
            return render(request, 'repo_data.html', {'repository': repository})
    elif request.method == 'POST':
        form_name = request.body.decode('utf-8').split('=')[0]
        form_value = request.body.decode('utf-8').split('=')[1]
        if form_name == 'pylint':
            async_pylint_output.after_response(request, repository)
            if language == 'en':
                return render(request, 'en/running_pylint.html', {'repository': repository})
            else:
                return render(request, 'running_pylint.html', {'repository': repository})
        elif form_name == 'running':
            time.sleep(20)
            file_path = '/tmp/projects/pylint_output' + repository.owner + '_' + repository.name
            if os.path.isfile(file_path):
                output_file = open(file_path, 'r')
                pylint_output = output_file.read()
                output_file.close()
                # pylint_output = pylint_output.split('\n')
                pylint_output = pylint_output.replace('/tmp/projects/', '/').split('\n')
                pylint_output_fixables = [x for x in pylint_output if ('C0303' in x or 'C0304' in x or 'C0321' in x or 'C0326' in x or 'W0404' in x or 'C0410' in x or 'C0411' in x or 'C0413' in x or 'W0611' in x)]
                pylint_output_level1 = [x for x in pylint_output if ('C0303' in x or 'C0304' in x or 'C0321' in x or 'C0326' in x or 'W0404' in x or 'C0410' in x or 'C0411' in x or 'C0413' in x or 'W0611' in x)]
                pylint_output_level2 = [x for x in pylint_output if ('C0303' in x or 'C0304' in x or 'C0321' in x or 'C0326' in x or 'W0404' in x or 'C0410' in x or 'C0411' in x or 'C0413' in x or 'W0611' in x)]
                if language == 'en':
                    return render(request, 'en/repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'pylint_output_fixables': pylint_output_fixables, 'pylint_output_level1': pylint_output_level1, 'pylint_output_level2': pylint_output_level2})
                else:
                    return render(request, 'repo_data_pylint.html', {'repository': repository, 'pylint_output': pylint_output, 'pylint_output_fixables': pylint_output_fixables, 'pylint_output_level1': pylint_output_level1, 'pylint_output_level2': pylint_output_level2})
            else:
                if language == 'en':
                    return render(request, 'en/running_pylint.html', {'repository': repository})
                else:
                    return render(request, 'running_pylint.html', {'repository': repository})
        elif form_name == 'fix_errors':
            async_fixing_errors.after_response(form_value, repository)
            if language == 'en':
                return render(request, 'en/fixing_errors.html', {'repository': repository})
            else:
                return render(request, 'fixing_errors.html', {'repository': repository})
        elif form_name == 'fixing':
            time.sleep(20)
            file_path = '/tmp/projects/pylint_output' + repository.owner + '_' + repository.name
            if os.path.isfile(file_path):
                if language == 'en':
                    return render(request, 'en/fixing_errors.html', {'repository': repository})
                else:
                    return render(request, 'fixing_errors.html', {'repository': repository})
            else:
                if 'github' in repository.html_url:
                    repository = Repository.objects.filter(pull_url_status='open').get(identifier=resource)
                elif 'gitlab.etsit.urjc.es' in repository.html_url:
                    repository = Repository.objects.filter(pull_url_status='opened').get(identifier=resource)
                if language == 'en':
                    return render(request, 'en/repo_data_success.html', {'repository': repository})
                else:
                    return render(request, 'repo_data_success.html', {'repository': repository})
        else:
            if language == 'en':
                return render(request, 'en/error.html', {'error_message': 'ERROR'})
            else:
                return render(request, 'error.html', {'error_message': 'ERROR'})
    else:
        if language == 'en':
            return render(request, 'en/error.html', {'error_message': '405: Method not allowed'})
        else:
            return render(request, 'error.html', {'error_message': '405: Method not allowed'})

def es(request):
    request.session[LANGUAGE_SESSION_KEY] = 'es'
    return redirect('/')

def en(request):
    request.session[LANGUAGE_SESSION_KEY] = 'en'
    return redirect('/')

@after_response.enable
def async_pylint_output(request, repository):
    github_clone_individual(repository)
    pylint_output = analyze_repo(repository)
    pylint_output = pylint_output.split('\n')
    if os.path.isfile('/tmp/projects/pylint_output' + repository.owner + '_' + repository.name):
        os.system('rm -rfv /tmp/projects/pylint_output' + repository.owner + '_' + repository.name)
    file_path = '/tmp/projects/pylint_output' + repository.owner + '_' + repository.name
    output_file = open(file_path, 'w+')
    for line in pylint_output:
        output_file.write(line + '\n')
    output_file.seek(0)
    output_file.close()

@after_response.enable
def async_fixing_errors(form_value, repository):
    make_fork(repository)
    github_clone_fork(repository)
    if form_value == '1':
        level = 1
    elif form_value == '2':
        level = 2
    else:
        level = 0
    fix_errors(repository, level)
    commit(repository)
    push(repository)
    pull_url = create_pull(repository)
    repository.pull_url = pull_url
    if 'github' in repository.html_url:
        pull_api_url = pull_url.replace('://github.com/', '://api.github.com/repos/')
        pull_api_url = pull_api_url.replace('/pull/', '/pulls/')
        repository.pull_api_url = pull_api_url
        repository.pull_url_status = 'open'
    elif 'gitlab.etsit.urjc.es' in repository.html_url:
        pull_api_url = 'https://gitlab.etsit.urjc.es/api/v4/projects/' + pull_url.split('gitlab.etsit.urjc.es/')[-1].rstrip('/').replace('/', '%2F')
        pull_api_url = pull_api_url.replace('%2F-%2Fmerge_requests%2F', '/merge_requests/')
        repository.pull_api_url = pull_api_url
        repository.pull_url_status = 'opened'
    repository.save()
    os.system('rm -rfv /tmp/projects/pylint_output' + repository.owner + '_' + repository.name)

def list(request):
    language = request.session.get(LANGUAGE_SESSION_KEY)
    update()
    repositories_all = Repository.objects.filter(pull_url_status__in=['open', 'opened', 'accepted', 'closed'])
    repositories_open = Repository.objects.filter(pull_url_status__in=['open', 'opened'])
    repositories_accepted = Repository.objects.filter(pull_url_status='accepted')
    repositories_closed = Repository.objects.filter(pull_url_status='closed')
    if language == 'en':
        return render(request, 'en/list.html', {'data_all': repositories_all, 'data_open': repositories_open, 'data_accepted': repositories_accepted, 'data_closed': repositories_closed})
    else:
        return render(request, 'list.html', {'data_all': repositories_all, 'data_open': repositories_open, 'data_accepted': repositories_accepted, 'data_closed': repositories_closed})

def error_list(request):
    # https://www.chartjs.org/docs/latest
    language = request.session.get(LANGUAGE_SESSION_KEY)
    errors_labels = []
    errors_data = []
    pull_status_labels = ['Open', 'Closed', 'Accepted']
    pull_status_data = [0, 0, 0]

    update()

    errors_dataset = Fixed_errors_count.objects.all().order_by('-count')
    for error in errors_dataset:
        errors_label = error.error_id.error_id + '-' + error.error_id.name
        errors_labels.append(errors_label)
        errors_data.append(error.count)

    repositories = Repository.objects.all()
    for repository in repositories:
        if repository.pull_url_status == 'open':
            pull_status_data[0] = pull_status_data[0] + 1
        elif repository.pull_url_status == 'opened':
            pull_status_data[0] = pull_status_data[0] + 1
        elif repository.pull_url_status == 'closed':
            pull_status_data[1] = pull_status_data[1] + 1
        elif repository.pull_url_status == 'accepted':
            pull_status_data[2] = pull_status_data[2] + 1
    if language == 'en':
        return render(request, 'en/error_list.html', {'errors_labels': errors_labels, 'errors_data': errors_data, 'pull_status_labels': pull_status_labels, 'pull_status_data': pull_status_data})
    else:
        return render(request, 'error_list.html', {'errors_labels': errors_labels, 'errors_data': errors_data, 'pull_status_labels': pull_status_labels, 'pull_status_data': pull_status_data})

def guide(request):
    language = request.session.get(LANGUAGE_SESSION_KEY)
    update()
    errors = Errors.objects.filter(fixable=True)
    if language == 'en':
        return render(request, 'en/guide.html', {'errors': errors})
    else:
        return render(request, 'guide.html', {'errors': errors})

def contact(request):
    language = request.session.get(LANGUAGE_SESSION_KEY)
    update()
    if language == 'en':
        return render(request, 'en/contact.html')
    else:
        return render(request, 'contact.html')

def update():
    repositories = Repository.objects.filter(pull_url_status__in=['open', 'opened'])
    for repo in repositories:
        pull_api_url = repo.pull_api_url
        if 'github' in pull_api_url:
            r = requests.get(pull_api_url)
            repo_data = r.json()
            if r.json()['state'] != 'open':
                delete_fork(repo)
        elif 'gitlab.etsit.urjc.es' in pull_api_url:
            r = requests.get(pull_api_url, headers={"PRIVATE-TOKEN": os.environ['tokengitlab']})
            repo_data = r.json()
            if r.json()['state'] != 'opened':
                delete_fork(repo)
        if r.json()['merged'] == True:
            repo.pull_url_status = 'accepted'
        else:
            repo.pull_url_status = r.json()['state']
        repo.save()

def store_individual_data(item):
    try:
        repository = Repository.objects.filter(pull_url_status='Null').get(identifier=item['id'])
    except Repository.DoesNotExist:
        repository = Repository()
        repository.identifier = item['id']
        repository.full_name = item['full_name']
        repository.owner = item['owner']['login']
        repository.name = item['name']
        if item['description'] is not None:
            repository.description = item['description']
        repository.html_url = item['html_url']
        repository.api_url = item['url']
        repository.save()

def store_individual_data_gitlab(item):
    try:
        repository = Repository.objects.filter(pull_url_status='Null').get(identifier=item['id'])
    except Repository.DoesNotExist:
        repository = Repository()
        repository.identifier = item['id']
        repository.full_name = item['path_with_namespace']
        repository.owner = item['namespace']['path']
        # repository.owner = item['namespace']['name']
        repository.name = item['name']
        if item['description'] is not None:
            repository.description = item['description']
        repository.html_url = item['web_url']
        api_url = 'https://gitlab.etsit.urjc.es/api/v4/projects/' + item['web_url'].split('gitlab.etsit.urjc.es/')[-1].rstrip('/').replace('/', '%2F')
        repository.api_url = api_url
        repository.save()

def github_clone_individual(item):
    url = item.html_url + '.git'
    name = item.full_name
    if os.path.isdir('/tmp/projects/' + name):
        os.system('rm -rfv /tmp/projects/' + name)
    if 'github' in url:
        os.system('git clone ' + url + ' /tmp/projects/' + name)
    elif 'gitlab.etsit.urjc.es' in url:
        url = url.split('https://')[1]
        os.system('git clone https://gitlab-ci-token:' + os.environ['tokengitlab'] +'@' + url + ' /tmp/projects/' + name)

def github_clone_fork(item):
    url = item.fork_url + '.git'
    name = item.full_name
    current_dir = os.getcwd()
    os.system('rm -rfv ' + '/tmp/projects/' + name)
    if 'github' in url:
        url = url.split('https://')[1]
        print(url)
        os.system('git clone https://' + os.environ['token'] +'@' + url + ' /tmp/projects/' + name)
        # os.system('git clone ' + url + ' /tmp/projects/' + name)
        if os.path.isdir('/tmp/projects/' + name):
            os.chdir('/tmp/projects/' + name)
        else:
            if language == 'en':
                return render(request, 'en/error.html', {'error_message': 'Repository could not be donwloaded'})
            else:
                return render(request, 'error.html', {'error_message': 'El repositorio no ha podido ser descargado'})
        os.system('git checkout -b pylint_errors')
    elif 'gitlab.etsit.urjc.es' in url:
        url = url.split('https://')[1]
        os.system('git clone https://gitlab-ci-token:' + os.environ['tokengitlab'] +'@' + url + ' /tmp/projects/' + name)
        os.chdir('/tmp/projects/' + name)
    os.chdir(current_dir)

def fix_errors(repository, level):
    global pull_body
    pull_body = pull_body_header
    # pylint_output = analyze_repo(repository)

    file_path = '/tmp/projects/pylint_output' + repository.owner + '_' + repository.name
    output_file = open(file_path, 'r')
    pylint_output = output_file.read()
    output_file.close()

    pylint_output = pylint_output.split('\n')
    pylint_output = pylint_output[:-1]
    for line in pylint_output:
        if len(line) > 0:
            if line[0] == '/':
                tokens = line.split(';')
                error = pylint_errors.Error(tokens)
                if level == 0:
                    fixable = pylint_errors.check(error)
                    add_error(error, repository)
                    count_error(error)
                    if fixable:
                        error_string = line.replace('/tmp/projects', '')
                        add_fixed_error(error, repository)
                        count_fixed_error(error)
                        pull_body = pull_body + error_string + '  \n'
                elif level == 1:
                    fixable = pylint_errors.check1(error)
                    add_error(error, repository)
                    count_error(error)
                    if fixable:
                        error_string = line.replace('/tmp/projects', '')
                        add_fixed_error(error, repository)
                        count_fixed_error(error)
                        pull_body = pull_body + error_string + '  \n'
                elif level == 2:
                    fixable = pylint_errors.check2(error)
                    add_error(error, repository)
                    count_error(error)
                    if fixable:
                        error_string = line.replace('/tmp/projects', '')
                        add_fixed_error(error, repository)
                        count_fixed_error(error)
                        pull_body = pull_body + error_string + '  \n'
    files = []
    for line in pylint_output:
        if len(line) > 0:
            if line[0] == '/':
                filename = line.split(';')[0]
                if filename not in files:
                    files.append(filename)
    for file in files:
        pylint_errors.check_placeholders(file)

def add_fixed_error(error, repository):
    try:
        error_count = Fixed_errors_repo()
        error_count.error_id = Errors.objects.get(error_id=error.code)
        error_count.identifier = Repository.objects.filter(pull_url_status='Null').get(identifier=repository.identifier)
        error_count.save()
    except Errors.DoesNotExist:
        pass

def add_error(error, repository):
    try:
        error_count = All_errors_repo()
        error_count.error_id = Errors.objects.get(error_id=error.code)
        error_count.identifier = Repository.objects.filter(pull_url_status='Null').get(identifier=repository.identifier)
        error_count.save()
    except Errors.DoesNotExist:
        pass

def count_fixed_error(error):
    try:
        error_count = Fixed_errors_count.objects.get(error_id=Errors.objects.get(error_id=error.code))
        error_count.count = error_count.count + 1
        error_count.save()
    except (Fixed_errors_count.DoesNotExist, TypeError):
        error_count = Fixed_errors_count()
        error_count.error_id = Errors.objects.get(error_id=error.code)
        error_count.count = 1
        error_count.save()
    except Errors.DoesNotExist:
        pass

def count_error(error):
    try:
        error_count = All_errors_count.objects.get(error_id=Errors.objects.get(error_id=error.code))
        error_count.count = error_count.count + 1
        error_count.save()
    except (All_errors_count.DoesNotExist, TypeError):
        error_count = All_errors_count()
        error_count.error_id = Errors.objects.get(error_id=error.code)
        error_count.count = 1
        error_count.save()
    except Errors.DoesNotExist:
        pass

def commit(repository):
    name = repository.full_name
    current_dir = os.getcwd()
    os.chdir('/tmp/projects/' + name)
    os.system('git config user.email "raulcanomontero@hotmail.com"')
    os.system('git config user.name "Raul Cano"')
    os.system('git add .')
    os.system('git commit -m "Fix Pylint Errors"')
    os.chdir(current_dir)

def push(repository):
    name = repository.full_name
    url = repository.fork_url + '.git'
    url = url.replace('https://', '@')
    url = url.replace('http://', '@')
    current_dir = os.getcwd()
    if 'github' in url:
        push_cmd = 'git push https://' + os.environ['username'] + ':' + os.environ['token'] + url
    elif 'gitlab.etsit.urjc.es' in url:
        push_cmd = 'git push https://' + os.environ['usernamegitlab'] + ':' + os.environ['passwordgitlab'] + url
    os.chdir('/tmp/projects/' + name)
    os.system(push_cmd)
    os.chdir(current_dir)

def analyze_repo(item):
    # https://docs.pylint.org/en/1.6.0/output.html
    # https://docs.python.org/2/library/subprocess.html
    # https://docs.pylint.org/en/1.6.0/run.html#command-line-options
    path = '/tmp/projects/' + item.full_name
    pylintrc_path = path + '/pylintrc'
    if os.path.isfile(pylintrc_path):
        os.environ['PYLINTRC'] = pylintrc_path
    pylint_output = ''
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            ext = os.path.splitext(name)[-1].lower()
            if ext == '.py':
                try:
                    output = subprocess.check_output(['pylint', os.path.join(root, name), "--msg-template='{abspath};{line};{column};{msg_id};{msg}'", "--reports=n"])
                except subprocess.CalledProcessError as e:
                    pylint_output = pylint_output + e.output.decode('utf-8')
    if os.environ.get('PYLINTRC') is not None:
        os.environ.pop('PYLINTRC')
    return pylint_output

def make_fork(repository):
    # https://developer.github.com/v3/repos/forks/
    # https://docs.gitlab.com/ee/api/projects.html#fork-project
    url = repository.api_url
    if 'github' in url:
        url += '/forks'
        s = requests.Session()
        r = s.post(url, headers={'Authorization': 'token ' + os.environ['token']})
        repository.fork_url = r.json()['html_url']
        repository.fork_api_url = r.json()['url']
        repository.default_branch = r.json()['source']['default_branch']
        repository.save()
    elif 'gitlab.etsit.urjc.es' in url:
        url += '/fork'
        s = requests.Session()
        r = s.post(url, headers={'PRIVATE-TOKEN': os.environ['tokengitlab']})
        repository.fork_url = r.json()['web_url']
        api_url = 'https://gitlab.etsit.urjc.es/api/v4/projects/' + r.json()['web_url'].split('gitlab.etsit.urjc.es/')[-1].rstrip('/').replace('/', '%2F')
        repository.fork_api_url = api_url
        repository.default_branch = r.json()['forked_from_project']['default_branch']
        repository.save()

def create_pull(repository):
    # https://developer.github.com/v3/pulls/
    # https://docs.gitlab.com/ee/api/merge_requests.html#create-mr
    url = repository.api_url
    if 'github' in url:
        url += '/pulls'
        s = requests.Session()
        data = {"title": "Pylint errors",
                "body": pull_body,
                "head": "RaulCM:pylint_errors",
                "base": repository.default_branch}
        data = json.dumps(data)
        r = s.post(url, data, headers={'Authorization': 'token ' + os.environ['token']})
        os.system('git config user.email "raulcanomontero@hotmail.com"')
        os.system('git config user.name "Raul Cano"')
        pull_url = r.json()['html_url']
    elif 'gitlab.etsit.urjc.es' in url:
        url = repository.fork_api_url
        url += '/merge_requests'
        s = requests.Session()
        data = {"title": "testmerge",
                'description': pull_body,
                "source_branch": repository.default_branch,
                "target_branch": repository.default_branch,
                "target_project_id": repository.identifier}
        r = s.post(url, data, headers={'PRIVATE-TOKEN': os.environ['tokengitlab']})
        pull_url = r.json()['web_url']
    return pull_url

def delete_fork(repository):
    url = repository.fork_api_url
    if 'github' in url:
        s = requests.Session()
        r = s.delete(url, headers={'Authorization': 'token ' + os.environ['token']})
    elif 'gitlab.etsit.urjc.es' in url:
        s = requests.Session()
        r = s.delete(url, headers={'PRIVATE-TOKEN': os.environ['tokengitlab']})
