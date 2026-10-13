import os
from pathlib import Path


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-moviehub-local-development-key"
)


DEBUG = os.environ.get(
    "DJANGO_DEBUG",
    "True"
).lower() == "true"


ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [

    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Our apps
    "accounts",
    "movies",
    "bookings",
    "storages",

]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# =========================================================
# URL CONFIG
# =========================================================

ROOT_URLCONF = "config.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {

        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

        "APP_DIRS":
            True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.debug",

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

            ],

        },

    },

]


# =========================================================
# WSGI
# =========================================================

WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# DATABASE
#
# LOCAL:
# localhost + root user
#
# AWS:
# RDS endpoint + admin user
#
# Values will come from environment variables.
# =========================================================

DATABASES = {

    "default": {

        "ENGINE":
            "django.db.backends.mysql",

        "NAME":
            os.environ.get(
                "MOVIE_DB_NAME",
                "movie_booking_db"
            ),

        "USER":
            os.environ.get(
                "MOVIE_DB_USER",
                "root"
            ),

        "PASSWORD":
            os.environ.get(
                "MOVIE_DB_PASSWORD",
                ""
            ),

        "HOST":
            os.environ.get(
                "MOVIE_DB_HOST",
                "localhost"
            ),

        "PORT":
            os.environ.get(
                "MOVIE_DB_PORT",
                "3306"
            ),

        "OPTIONS": {

            "charset":
                "utf8mb4",

        },

    }

}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },

]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"


TIME_ZONE = "Asia/Kolkata"


USE_I18N = True


USE_TZ = True


# =========================================================
# STATIC FILES
#
# CSS / JS / Bootstrap related local static files
# =========================================================

STATIC_URL = "/static/"


STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_DIRS = []


# =========================================================
# MEDIA FILES
#
# For now posters stay locally.
#
# Later in Phase 2 we will move MEDIA to S3.
# =========================================================

# =========================================================
# MEDIA STORAGE
#
# Local     -> local media/ folder
# AWS EC2   -> private S3 bucket using IAM Role
# ==================================================== AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_STORAGE_BUCKET_NAME = "moviehub-media-2026-2003"
AWS_S3_REGION_NAME = "ap-south-1"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "endpoint_url": "https://s3.ap-south-1.amazonaws.com",
            "addressing_style": "virtual",
            "signature_version": "s3v4",
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": 3600,
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}



# =========================================================
# EMAIL / GMAIL SMTP
#
# Password MUST NOT be written here.
# Environment variables only.
# =========================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)


EMAIL_HOST = "smtp.gmail.com"


EMAIL_PORT = 587


EMAIL_USE_TLS = True


EMAIL_HOST_USER = os.environ.get(
    "MOVIE_EMAIL_USER"
)


EMAIL_HOST_PASSWORD = os.environ.get(
    "MOVIE_EMAIL_PASSWORD"
)


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


EMAIL_TIMEOUT = 15


# =========================================================
# LOGIN SETTINGS
# =========================================================

LOGIN_URL = "/accounts/login/"


# =========================================================
# SECURITY HEADERS
# =========================================================

X_FRAME_OPTIONS = "DENY"


SECURE_CONTENT_TYPE_NOSNIFF = True


# =========================================================
# CSRF TRUSTED ORIGINS
#
# Example later:
#
# DJANGO_CSRF_TRUSTED_ORIGINS=
# http://3.110.xx.xx,https://example.com
# =========================================================

CSRF_TRUSTED_ORIGINS = [

    origin.strip()

    for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")

    if origin.strip()

]


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
