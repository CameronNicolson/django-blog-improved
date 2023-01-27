from pathlib import Path

TEST_ROOT = Path(__file__).parent

SECRET_KEY = "django-blog-improved"

ALLOWED_HOSTS = ["*"]

SITE_ID = 1

TIME_ZONE="UTC"

LANGUAGE_CODE = 'en-us'

USE_TZ = True

FIXTURE_DIRS = [
    TEST_ROOT / "fixtures",
] 

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "redirects",
    "crispy_forms",
    "crispy_forms_gds",
    "phonenumber_field",
    "taggit",
    "blog_improved", 
]


MIDDLEWARE = [
    "redirects.middleware.RedirectMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

try:
    from blog_improved.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
