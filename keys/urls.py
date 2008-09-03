from django.conf.urls.defaults import *
from sshkeys.keys.models import Address

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

info_dict = {
    'queryset': Address.objects.all(),
}

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list', info_dict),
    (r'^(?P<object_id>.*@.*)/$', 'django.views.generic.list_detail.object_detail', info_dict),


    # Uncomment the next line to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
