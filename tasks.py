from shutil import copy
import sys

from invoke import (
    task,
    run
)

# define projects directories
app_dir = 'azdashboard'
config_dir = app_dir + '/config'
test_dir = app_dir + '/test'
func_test_dir = test_dir + '/functional'
unit_test_dir = test_dir + '/unit'


@task
def set_settings(ctx, environment='production', nosetests=''):
    if environment not in ['production', 'development', 'test']:
        print('Error: ' + environment + ' is not a valid parameter',
              file=sys.stderr)
        exit(1)

    src = config_dir + '/settings-' + environment + '.py.sample'
    dst = config_dir + '/settings.py'
    print('Copying ' + src + ' to ' + dst)
    copy(src, dst)
    print('Done')


@task(set_settings)
def test_func(ctx, environment='test', nosetests='nosetests'):
    run_cmd(nosetests + ' -w ' + func_test_dir)


@task(set_settings)
def test_unit(ctx, environment='test', nosetests='nosetests'):
    run_cmd(nosetests + ' -w ' + unit_test_dir)


@task(set_settings, test_func, test_unit)
def test(ctx, environment='test', nosetests='nosetests'):
    pass


@task(set_settings)
def setup(ctx, ):
    src = 'alembic.ini.sample'
    dst = 'alembic.ini'
    print('Copying ' + src + ' to ' + dst)
    copy(src, dst)
    print('Done')


@task
def pep8(ctx, ):
    # ignore versions folder since migration scripts are auto-generated
    cmd = 'pep8 --exclude=app/db/versions/* run.py tasks.py ' + app_dir
    run_cmd(ctx, cmd)


@task
def pyflakes(ctx, ):
    cmd = 'pyflakes run.py tasks.py ' + app_dir
    run_cmd(ctx, cmd)


@task(pep8, pyflakes)
def check(ctx, ):
    pass


@task
def clean(ctx, ):
    run_cmd(ctx, "find . -name '__pycache__' -exec rm -rf {} +")
    run_cmd(ctx, "find . -name '*.pyc' -exec rm -f {} +")
    run_cmd(ctx, "find . -name '*.pyo' -exec rm -f {} +")
    run_cmd(ctx, "find . -name '*~' -exec rm -f {} +")
    run_cmd(ctx, "find . -name '._*' -exec rm -f {} +")


@task(clean)
def clean_env(ctx, ):
    run_cmd(ctx, 'rm -r ./env && mkdir env && touch env/.keep')


@task
def rename(ctx, name=None):
    if name is None:
        print('Please, provide a name for your application. '
              'Example: invoke rename --name=\'my awesome app\'')
    else:
        app_name = name.lower().replace(' ', '')
        class_name = name.title().replace(' ', '')

        rename_app_name = "sed -i 's/azdashboard/" + app_name + "/g'"
        rename_class_name = "sed -i 's/AzDashboard/" + class_name + "/g'"

        pyfiles = "find azdashboard -type f -name '*.py' | xargs "
        run_cmd(ctx, pyfiles + rename_app_name)
        run_cmd(ctx, pyfiles + rename_class_name)

        run_cmd(ctx, rename_app_name + " run.py tasks.py alembic.ini.sample")
        run_cmd(ctx, rename_class_name + " run.py tasks.py")

        run_cmd(ctx, 'mv -v azdashboard ' + app_name)


def run_cmd(ctx, cmd):
    print('Running \'' + cmd + '\'...')
    run(cmd)
    print('Done')
