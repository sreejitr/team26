"""
Django settings for team26 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    

#os.environ['DJANGO_SETTINGS_MODULE'] = 'team26.settings'

from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w(%%$f&gy4g66ox^yhzix5laqw6c^qu!&vo(0bzj!x#=&rcng2'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'budgie',
)


LOGIN_URL = '/budgie/login'

# Default URL to redirect to after a user logs in.
LOGIN_REDIRECT_URL = '/budgie/'


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

X_FRAME_OPTIONS = 'DENY'

ROOT_URLCONF = 'team26.urls'

WSGI_APPLICATION = 'team26.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


#For Heroku
#DATABASES = {
#    'default': dj_database_url.config(
#        default='sqlite:////{0}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
#    )
#}


# we only need the engine name, as heroku takes care of the rest
#DATABASES = {
#"default": {
#   "ENGINE": "django.db.backends.postgresql_psycopg2",
#}
#}

#DATABASES = {  
#    'default': {  
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',  
#        'NAME': 'budgie',  
#        'USER': 'susana',  
#        'PASSWORD': 'susana',  
#        'HOST': '',  
#        'PORT': '',  # leave blank  
#    }  
#}  

<<<<<<< HEAD
# DATABASES = {
# 'default': {
# 'ENGINE': 'django.db.backends.mysql',
# 'NAME': 'budgie',
# 'USER': '',
# 'PASSWORD': '',
# 'HOST': '',
# 'PORT': '',
# }
# }
=======
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.mysql',
'NAME': 'budgie',
'USER': '',
'PASSWORD': '',
'HOST': '',
'PORT': '',
}
}
>>>>>>> c4a7f3e6d64febbfc3597ad45d94d111bbd5f246


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

#Changed to false due to errors in naive date format
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#Email Configurations
EMAIL_BACKEND= 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.srv.cs.cmu.edu'
EMAIL_HOST_USER = 'susanal@andrew.cmu.edu'
EMAIL_USE_TLS=True

#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'susanalauhou@gmail.com'
#EMAIL_HOST_PASSWORD = '*'
#EMAIL_USE_TLS=True
#EMAIL_PORT=587
#DEFAULT_FROM_EMAIL = 'susanalauhou@gmail.com'
#SERVER_EMAIL = 'susanalauhou@gmail.com'


CATEGORY_CHOICES = (
        ('HOU', 'Housing'),
        ('TRA', 'Transportation'),
        ('FOO', 'Food'),
        ('EDU', 'Education'),
        ('HEA', 'Health'),
        ('ENT', 'Entertainment'),
        ('SAL', 'Salary'),
        ('GFT', 'Gift'),
        )

MONTH_CHOICES = (
        ('JAN', 'January'),
        ('FEB', 'February'),
        ('MAR', 'March'),
        ('APR', 'April'),
        ('MAY', 'May'),
        ('JUN', 'June'),
        ('JUL', 'July'),
        ('AUG', 'August'),
        ('SEP', 'September'),
        ('OCT', 'October'),
        ('NOV', 'November'),
        ('DEC', 'December'),
        )

YEAR_CHOICES = (
        ('2013', '2013'),
        ('2014', '2014'),
        ('2015', '2015'),
        ('2016', '2016'),
        ('2017', '2017'),
        ('2018', '2018'),
        ('2019', '2019'),
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
)

TYPE_TRANSACTION_CHOICES = (
        ('CR', 'Income'),
        ('DR', 'Expense'),
        ('TR', 'Transfer Funds'),
        )

ACCOUNT_CHOICES = (
        ('1', ' '),
        ('2', '123'),
        ('3', '234'),
        )

ACCOUNT_TYPE_CHOICES = (
        ('CC', 'Credit Card Acct'),
        ('CHK', 'Checking Acct'),
        ('SAV', 'Savings Acct'),
    )

VIEW_TRANSACTION_TIME_CHOICES = (
        ('7 days', 'Last 7 days'),
        ('This month', 'This month'),
    )

VIEW_TRANSACTION_ACCOUNT_CHOICES = (
        ('All', 'All Accounts'),
        ('CC', 'Credit Card Accounts'),
        ('CHK', 'Checking Accounts'),
        ('SAV', 'Saving Accounts'),
    )


#For Heroku
#import dj_database_url
# Parse database configuration from $DATABASE_URL
#DATABASES['default'] =  dj_database_url.config()
#DATABASES = { 'default' : dj_database_url.config()}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
#ALLOWED_HOSTS = ['*']

# Static asset configuration
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#STATIC_ROOT = 'staticfiles'
#STATIC_URL = '/static/'
#STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, 'static'),
#)
