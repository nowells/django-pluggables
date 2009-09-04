DEBUG = True
ROOT_URLCONF = 'funnywalks.urls'
INSTALLED_APPS = (
    'complaints',
    'funnywalks',
)

import os
DB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db'))
DATABASE_NAME = os.path.join(DB_ROOT, 'database.db')
DATABASE_ENGINE = 'sqlite3'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
DATABASE_OPTIONS = {}
