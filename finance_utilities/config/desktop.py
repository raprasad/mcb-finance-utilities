import os, sys

# Add expense_code_definitions app
sys.path.append('/Users/some-user/mcb-git/hu-expense-code-definitions')

CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
FILES_TO_SERVE_ROOT = os.path.join(CURRENT_DIR, 'files_to_serve')
#print 'CURRENT_DIR', CURRENT_DIR
#print 'FILES_TO_SERVE_ROOT', FILES_TO_SERVE_ROOT

# '/Users/some-user/mcb-finance-utilities/finance_utilities/files_to_serve' 
FILES_TO_SERVE_URL_BASE = 'http://127.0.0.1:8000/' #'mcbweb.rc.fas.harvard.edu/mcb/'
# some-user/123

DEBUG = True

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
     'NAME': os.path.join(CURRENT_DIR, 'test_db/fin1.db3'),     
     #'NAME': '/Users/some-user/projects/mcb-git/mcb-finance-utilities/test_db/fin1.db3',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SECRET_KEY = '%ng($chdz4o!cxyu4*1$5y@q278wz_u(dj5y5k8$lhxz5*08!*'

ROOT_URLCONF = 'finance_utilities.urls'

SESSION_COOKIE_NAME = 'mcbfin_desktop'

SMTP_CONNECTION_STRING = 'mail.fas.harvard.edu'
EMAIL_HOST = 'mail.fas.harvard.edu'

EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'admin@harvard.edu' # from address for server error emails
SERVER_EMAIL = DEFAULT_FROM_EMAIL # used as the from address for django.core.mail.mail_admins()

# media files
MEDIA_ROOT = os.path.join(FILES_TO_SERVE_ROOT, 'media' )
MEDIA_URL = FILES_TO_SERVE_URL_BASE + 'media/'

# static files
STATICFILES_DIRS = (os.path.join(CURRENT_DIR, 'static_site_files'),)
STATIC_ROOT = os.path.join(FILES_TO_SERVE_ROOT, 'static')
STATIC_URL = FILES_TO_SERVE_URL_BASE + 'dfiles/static/'

TEMPLATE_DIRS = (
    os.path.join(CURRENT_DIR, 'templates'), 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

COA_VALIDATOR_URL_TEST = 'https://-some-server-34-cadm:8852/GLValidate/ValidateGLAccount'
COA_VALIDATOR_URL_PROD = 'https://-some-server-36-cadm:8052/GLValidate/ValidateGLAccount'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     'django.contrib.admin',
    # 'django.contrib.admindocs',
    
    'hcom_training',
    'coa_validate',
    'expense_code_definitions', 
    #'hcom_reconcile', 
)

POORMANS_DB_BACKUP_DIR = 'for mysql dumps'
COA_CREDS_FILE = '/Users/some-user/mcb-git/mcb-finance-utilities/finance_utilities/config/coa_creds'
