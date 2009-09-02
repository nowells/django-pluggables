import os
import glob
from fabric import local

LOCAL_PACKAGES = (
    'examples',
    '',
)

PROJECT_ROOT = os.path.abspath(os.path.curdir)

def bootstrap():
    # Create new virtual environment in a new location. We will atomically swap the current virtualenv with the new once at the end of this process.
    local("rm -Rf .ve~/")

    local('virtualenv .ve~')

    # hack activate so it uses project directory instead of ve in prompt
    local('sed \'s/(`basename \\\\"\\$VIRTUAL_ENV\\\\\"`)/(`basename \\\\`dirname \\\\"$VIRTUAL_ENV\\\\"\\\\``)/g\' .ve~/bin/activate > .ve~/bin/activate.tmp')
    local('mv .ve~/bin/activate.tmp .ve~/bin/activate')

    # PIP install requirements
    local("pip install -I --source=.ve~/src/ --environment=.ve~/ -r REQUIREMENTS")

    # Cleanup pip install process
    local("rm -Rf build/")

    # Add local src folders to python path.
    local("echo '%s' >> .ve~/lib/python2.5/site-packages/easy-install.pth" % '\n'.join([ os.path.join(PROJECT_ROOT, x) for x in LOCAL_PACKAGES ]))

    # Apply patches.
    for patch in glob.glob(os.path.join(PROJECT_ROOT, 'dist', 'patches', '*.patch')):
        dirname, filename = os.path.split(patch)
        application_name = filename.split('.patch')[0]
        application_path = os.path.join(PROJECT_ROOT, '.ve~', 'src', application_name)
        if os.path.exists(application_path):
            print 'Patching %s...' % application_name
            local("cd %s; patch -p0 < %s" % (application_path, patch))

    # Cleanup and .pyc files that got generated so that we do not have any corrupt pyc files hanging out with the .ve~ path.
    local("find .ve~/ -type f -name '*.pyc' -print0 | xargs -0 rm -f")
    # Prepare the temporary virtualenv to take the place of the primary virtualenv by replacing the paths
    local("find .ve~/ -type f -print0 | xargs -0 sed -i 's/\.ve~/ve/g'")
    # Atomically move the new virtualenv into place, and move the old virtualenv into a backup location.
    local("mv ve/ .ve.old~/ 2> /dev/null; mv .ve~/ ve/")

def documentation():
    local("rm -Rf docs/modules/")
    local("rm -Rf docs/_build/html/")
    print "View the documentation here: file://%s" % os.path.join(PROJECT_ROOT, 'docs', '_build', 'html', 'index.html')
