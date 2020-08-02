from .base import *

DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS += [
    'debug_toolbar'
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

# DEBUG TOOLBAR SETTINGS

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STRIPE_PUBLIC_KEY = 'pk_test_51H0TKPKyUb1TiCEJfVuue0NK0v5jmsLeKsYhYtVcS7Wmy13OIJfP1WTzNk0IYXsLZu1cH7yhxenLV5wOzl5RzUlB002P8ev68y'
STRIPE_SECRET_KEY = 'sk_test_51H0TKPKyUb1TiCEJoF5aBq4djpMWX4CQzdgE7NND4vIP2NCUYjC7yWnIln5xro6CzUMQnWeLCt2IzNZV7CmdJ2EP00IUKhvBUm'

