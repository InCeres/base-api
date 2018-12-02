
from distutils import version

from fabric.api import local, env, cd, run, lcd, sudo
from fabric import utils
from fabric.contrib import console


def __build_env(environ='prod'):
    env_vars = open('.env.deploy').read().split('\n')
    for variable in env_vars:
        if variable != '':
            pair = variable.split('=')
            setattr(env, pair[0], pair[1])
    env.host_string = '{}-{}'.format(environ, env.PROJECT_NAME)
    env.key_filename = getattr(env, '{}_KEY_FILENAME'.format(environ.upper()))
    env.user = "inceres"
    env.shell = "/bin/bash -l -i -c"


def __next_tag(tags):
    tags.sort(key=version.StrictVersion)
    last_tag = tags[-1]
    utils.puts('LAST TAG: {}'.format(last_tag))
    next_tag = [int(number) for number in last_tag.split('.')]
    if env.increment == 'rev':
        next_tag[2] = next_tag[2] + 1
    if env.increment == 'min':
        next_tag[1] = next_tag[1] + 1
        next_tag[2] = 0
    if env.increment == 'maj':
        next_tag[0] = next_tag[0] + 1
        next_tag[1] = 0
        next_tag[2] = 0
    return '.'.join([str(number) for number in next_tag])


def __list_tags():
    branch = local('git rev-parse --abbrev-ref HEAD', capture=True)
    local('git pull origin {}'.format(branch))
    tags = [tag for tag in local('git tag', capture=True).split('\n') if tag != '']
    return tags


def __generate_next_tag():
    tags = __list_tags()
    if len(tags) > 0:
        next_tag = __next_tag(tags)
        utils.puts('WILL INCREASE {} AND NEXT TAG WILL BE: {}'.format(env.increment, next_tag))
    else:
        next_tag = '0.0.1'
        utils.puts('NO TAGS FOUND. WILL CREATE NEW TAG 0.0.1')
    return next_tag


def __create_tag(next_tag):
    local('git tag {}'.format(next_tag))
    local('git push --tags'.format(next_tag))


def __create_tag_api():
    with lcd(env.LOCAL_API_FOLDER):
        next_api_tag = __generate_next_tag()
        if not console.confirm('CONFIRM NEXT API TAG?'):
            utils.abort('FINISHING WITHOUT DEPLOY')
        __create_tag(next_tag=next_api_tag)
        return next_api_tag


def __create_tag_app():
    with lcd(env.LOCAL_APP_FOLDER):
        next_app_tag = __generate_next_tag()
        if not console.confirm('CONFIRM NEXT APP TAG?'):
            utils.abort('FINISHING WITHOUT DEPLOY')
        __create_tag(next_tag=next_app_tag)
        return next_app_tag


def prod(increment='rev', project='both'):
    __build_env()
    env.increment = increment
    if project in ['api', 'both']:
        next_api_tag = __create_tag_api()
        utils.puts('CONNECTING TO {} FOR RUNNING API DEPLOY'.format(env.host_string))
        with cd(env.REMOTE_API_FOLDER):
            run('load-env')
            run('git fetch --tags')
            run('git checkout tags/{}'.format(next_api_tag))
            run('{}/pip install -r requirements.txt'.format(env.REMOTE_VENV))
            run('{}/python manage.py db upgrade'.format(env.REMOTE_VENV))
            sudo('systemctl restart {}-api.service'.format(env.PROJECT_NAME))
    if project in ['app', 'both']:
        utils.puts('CONNECTING TO {} FOR RUNNING APP DEPLOY'.format(env.host_string))
        next_app_tag = __create_tag_app()
        with cd(env.REMOTE_APP_FOLDER):
            run('load-env')
            run('git fetch --tags')
            run('git checkout tags/{}'.format(next_app_tag))
            run('bower install')
            run('grunt production')


def stag(branch='staging'):
    __build_env('stag')
    utils.puts('CONNECTING TO {} FOR RUNNING DEPLOY'.format(env.host_string))
    with cd(env.REMOTE_API_FOLDER):
        run('load-env')
        run('git pull origin {}'.format(branch))
        run('{}/pip install -r requirements.txt'.format(env.REMOTE_VENV))
        run('{}/python manage.py db upgrade'.format(env.REMOTE_VENV))
        sudo('systemctl restart {}-api.service'.format(env.PROJECT_NAME))
    with cd(env.REMOTE_APP_FOLDER):
        run('load-env')
        run('git pull origin {}'.format(branch))
        run('bower install')
        run('grunt staging')
