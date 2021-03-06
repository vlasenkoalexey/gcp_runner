# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['get_notebook_path', 'read_colab_nb', 'find_default_export_for_notebook', 'get_module_name',
           'get_package_name', 'reload_package_modules', 'export_and_reload_all', 'run_process', 'get_run_args',
           'get_run_python_args', 'build_and_push_docker_image', 'format_job_dir', 'print_tensorboard_command']

# Cell
import IPython.core
import json
import os.path
import re
import ipykernel
import requests

# Alternative that works for both Python 2 and 3:
from requests.compat import urljoin

try:  # Python 3 (see Edit2 below for why this may not work in Python 2)
    from notebook.notebookapp import list_running_servers
except ImportError:  # Python 2
    import warnings
    from IPython.utils.shimmodule import ShimWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ShimWarning)
        from IPython.html.notebookapp import list_running_servers


def get_notebook_path():
    """
    Return the full path of the jupyter notebook.
    !!! Doesn't work from VS code.
    """
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    servers = list_running_servers()
    for ss in servers:
        try:
            response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                    params={'token': ss.get('token', '')}, timeout=1)
            for nn in json.loads(response.text):
                if nn['kernel']['id'] == kernel_id:
                    relative_path = nn['notebook']['path']
                    return os.path.join(ss['notebook_dir'], relative_path)
        except Exception as e:
            pass


# Cell
import nbdev.export
import nbdev.imports
import nbformat

from .core import get_notebook_path

if nbdev.imports.in_colab():
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials

def read_colab_nb(notebook_path):
    gdrive_file_id = re.search('/fileId=(.+)', notebook_path)[1]
    # Authenticate and create the PyDrive client.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    gdrive = GoogleDrive(gauth)
    downloaded = gdrive.CreateFile({'id': gdrive_file_id})
    downloaded_string = downloaded.GetContentString()
    return nbformat.reads(downloaded_string, as_version=4)

def find_default_export_for_notebook(notebook_path):
    nb = read_colab_nb(notebook_path) \
        if nbdev.imports.in_colab() else nbdev.export.read_nb(notebook_path)
    default = nbdev.export.find_default_export(nb['cells'])
    return default

def get_module_name():
    return find_default_export_for_notebook(get_notebook_path())

# Cell

import pkgutil
import importlib
import time
import nbdev.imports
from nbdev.export import *

def get_package_name():
    "Returns name of the current package"
    # see logic in https://github.com/fastai/nbdev/blob/master/nbdev/export.py
    return str(nbdev.imports.Config().lib_path).split('/')[-1]

def reload_package_modules(package_name):
    "Dynamically reloads package `package_name`."
    # Reload order matters. First we need to reload all modules except
    # the current one, and then reload current one. Otherwise reload might
    # fail if current module refers to other module that has new functions added.
    current_module_name = get_module_name()
    current_module = None
    for _, module_name, _ in (pkgutil.iter_modules([package_name])):
        if current_module_name == module_name:
            current_module
        else:
            module = importlib.import_module(package_name + '.' + module_name)
            importlib.reload(module)
    if current_module is not None:
        importlib.reload(current_module)

def export_and_reload_all(silent=False, ignore_errors=False):
    "Converts all notebooks to modules, and reloads all modules"
    if nbdev.imports.in_ipython():
        notebook2script(silent=silent)
        # Need to reload packages in order
        # Looks like when it is called with to_dict, it doesn't actually update files.
        module_name_dict = notebook2script(silent=True, to_dict=True)
        time.sleep(1)
        #reload_package_modules(get_package_name())
        module_name_to_notebook_path = \
            list ((key,str(value[0][1])) for key, value in module_name_dict.items())
        sorted_list = sorted(module_name_to_notebook_path, key=lambda pair:pair[1])
        package_name = get_package_name()
        for (module_name, _) in sorted_list:
            if ignore_errors:
                try:
                    module = importlib.import_module(package_name + '.' + module_name)
                    importlib.reload(module)
                except Error as e:
                    print (e)
            else:
                module = importlib.import_module(package_name + '.' + module_name)
                importlib.reload(module)


# Cell

import os
import subprocess
import io

from threading import Thread
from queue import Queue

def _reader(pipe, queue, pipe_name):
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                queue.put((pipe_name, line))
    finally:
        queue.put(None)

def run_process(args, **kwargs):
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        encoding='utf-8')

    q = Queue()
    Thread(target=_reader, args=[proc.stdout, q, 'stdout']).start()
    Thread(target=_reader, args=[proc.stderr, q, 'stderr']).start()
    for source, line in iter(q.get, None):
        line = line.rstrip('\n').rstrip('\r')
        if line != '':
            if source == 'stderr':
                print("\x1b[31m{}\x1b[0m".format(line))
            else:
                print(line)

    return proc.poll()

# Cell

def get_run_args(func, **kwargs):
    package_name = get_package_name()
    module_name = get_module_name()
    function_name = func.__name__
    args = ['--module-name=%s' % package_name + '.' + module_name,
         '--function-name=%s' % function_name]
    if kwargs is not None:
        for key,value in kwargs.items():
            args.append('--%s=%s' % (key.replace('_', '-'), str(value)))

    return args

def get_run_python_args(func, python_binary='python', **kwargs):
    args = [python_binary,
         '-u',
         '-m',
         'gcp_runner.entry_point']

    args.extend(get_run_args(func, **kwargs))
    return args

# Cell
def build_and_push_docker_image(docker_file_path, image_uri, push_docker=True, dry_run=False):
    build_docker_args = ['docker', 'build', '-f', docker_file_path, '-t', image_uri, './']
    print('Building Docker image:')
    print(' '.join(build_docker_args))
    if not dry_run:
        result = run_process(build_docker_args)
        if result:
            return result
    if push_docker:
        push_docker_args = ['docker', 'push', image_uri]
        print('Pushing Docker image:')
        print(' '.join(push_docker_args))
        if not dry_run:
            result = run_process(push_docker_args)
            if result:
                return result
    return 0

# Cell
import datetime
import getpass

def format_job_dir(job_dir, date_time:datetime.datetime=None):
    if date_time is None:
        date_time = datetime.datetime.now()
    return job_dir.format(**{'datetime':datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), 'username': getpass.getuser()})

format_job_dir('model_{datetime}_{username}')

# Cell

def print_tensorboard_command(job_dir):
    print('To see job output in tensorboard, run following command:')
    print('tensorboard --logdir=%s' % job_dir)
