"""Tests for s3upload package."""
from os import environ

DEBUG = True
SECRET_KEY = 'foo'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 's3upload.urls'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    's3upload',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
            ]
        }
    },
]

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME', 'test-bucket')

S3UPLOAD_REGION = 'us-east-1'
S3UPLOAD_DESTINATIONS = {
    'misc': {
        'key': lambda original_filename: 'images/unique.jpg',
    },
    'files': {
        'key': 'uploads/files',
        'auth': lambda u: u.is_staff,
    },
    'imgs': {
        'key': 'uploads/imgs',
        'auth': lambda u: True,
        'allowed': ['image/jpeg', 'image/png'],
        'content_length_range': (5000, 20000000),  # 5kb - 20mb
    },
    'vids': {
        'key': 'uploads/vids',
        'auth': lambda u: u.is_authenticated(),
        'allowed': ['video/mp4'],
    },
    'cached': {
        'key': 'uploads/vids',
        'auth': lambda u: True,
        'allowed': '*',
        'acl': 'authenticated-read',
        'bucket': 'astoragebucketname',
        'cache_control': 'max-age=2592000',
        'content_disposition': 'attachment',
        'server_side_encryption': 'AES256',
    }
}
