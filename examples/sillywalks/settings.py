DEBUG = True
ROOT_URLCONF = 'sillywalks.urls'
INSTALLED_APPS = (
    'complaints',
    'pluggables',
    'sillywalks',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'uni_form',
)

import os
import shutil
db_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db'))
DATABASE_NAME = os.path.join(db_root, '.database.db')
if not os.path.exists(DATABASE_NAME) and os.path.exists(os.path.join(db_root, 'database.db')):
    shutil.copyfile(os.path.join(db_root, 'database.db'), DATABASE_NAME)
DATABASE_ENGINE = 'sqlite3'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
DATABASE_OPTIONS = {}

ADMIN_MEDIA_PREFIX = '/django-admin-media/'
MEDIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
SITE_SERVER_URL = 'http://127.0.0.1:8000'
MEDIA_SERVER_URL = SITE_SERVER_URL
SITE_RELATIVE_URL = '/'
MEDIA_RELATIVE_URL = '%smedia/' % SITE_RELATIVE_URL
SITE_URL = '%s%s' % (SITE_SERVER_URL, SITE_RELATIVE_URL)
MEDIA_URL = '%s%s' % (MEDIA_SERVER_URL, MEDIA_RELATIVE_URL)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'pluggables.pluggable_context_processor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)
