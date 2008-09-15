from django.conf.urls.defaults import *
from sshkeys.keys.models import Address

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = 'sshkeys.keys.views.view404'
urlpatterns = patterns('sshkeys.keys.views',
    (r'^$',                         'index'),
    (r'^list/?$',                   'list'),
    (r'^(?P<id>[0-9]+)/?$',         'detail'),
    (r'^(?P<address>.*@.*)/?$',     'detail'),
    (r'^upload/?$',                 'upload'),
    (r'^search/?$',                 'search'),
    (r'^download/?$',               'download'),
    (r'^confirm/(?P<token>\w+)/?$', 'confirm'),
    (r'^admin/?(.*)',               admin.site.root),
)

