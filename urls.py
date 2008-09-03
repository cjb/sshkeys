from django.conf.urls.defaults import *
from sshkeys.keys.models import Address

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('sshkeys.keys.views',
    (r'^$',                    'index'),
    (r'^list/$',               'list'),
    (r'^(?P<address>.*@.*)/$', 'detail'),
    (r'^upload/$',             'upload'),
    (r'^search/$',             'search'),
    (r'^download/$',           'download'),
    (r'^admin/(.*)',           admin.site.root),
)
