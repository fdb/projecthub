# Site configuration.
SITE_NAME = 'ProjectHub'
SITE_DOMAIN = 'example.com'
SITE_URL = 'http://www.%s/' % SITE_DOMAIN
SITE_TAGLINE = 'Witty tagline here'
SITE_DESCRIPTION = 'A generic ProjectHub site.'

# Email settings
DEFAULT_FROM_EMAIL = 'webmaster@%s' % SITE_DOMAIN

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Database settings
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'projecthub'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

PRIMARY_LINKS = (
    ('Home', '/'),
    ('Download', '/download/'),
    ('Documentation', '/documentation/'),
    ('Weblog', '/weblog/'),
    ('Forum', '/forum/'))

