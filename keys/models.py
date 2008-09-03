from django.db import models
from django.contrib import admin

class Address (models.Model):
    address = models.CharField(max_length=255)
    def __unicode__(self):
        return self.address

class SSHKey (models.Model):
    owners = models.ManyToManyField(Address, through='AddressKey')
    keytext = models.CharField(max_length=1024)
    def __unicode__(self):
        return self.keytext

class AddressKey (models.Model):
    address = models.ForeignKey(Address)
    sshkey = models.ForeignKey(SSHKey)
    date_added = models.DateTimeField('date added')
    verified = models.BooleanField(default=False)
    def __unicode__ (self):
        return " / ".join([unicode(self.address), unicode(self.sshkey)])

class AddressAdmin (admin.ModelAdmin):
    search_fields = ['address']

admin.site.register(Address, AddressAdmin)
admin.site.register(SSHKey)
admin.site.register(AddressKey)
