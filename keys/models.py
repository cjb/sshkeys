from django.db import models
from django.contrib import admin
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
from random import random
import sha

# favour django-mailer but fall back to django.core.mail
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

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
    token = models.CharField(max_length=40)
    token_sent = models.DateTimeField()

    def token_expired(self):
        expiration_date = self.token_sent + timedelta(days=14)
        return expiration_date <= datetime.now()
    token_expired.boolean = True

    def confirm_token(self):
        if not self.token_expired():
            self.verified = True
            self.save()
            return True
        else:
            return False

    def send_confirmation(self, email_address):
        salt = sha.new(str(random())).hexdigest()[:5]
        # FIXME: Is this random enough?
        confirmation_key = sha.new(salt + email_address.address.address).hexdigest()
        activate_url = u"http://%s%s" % (
            "sshkeys.net/confirm_email/", confirmation_key)

        message = render_to_string("keys/email_confirmation_message.txt", {
            "confirmation_key": confirmation_key,
        })
        send_mail("SSH Key verification.", message, settings.FROM_EMAIL, [email_address.address.address])
        email_address.token = confirmation_key
        email_address.save()

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.token_expired():
                confirmation.delete()

    def __unicode__ (self):
        return " / ".join([unicode(self.address), unicode(self.sshkey)])

class AddressAdmin (admin.ModelAdmin):
    search_fields = ['address']

admin.site.register(Address, AddressAdmin)
admin.site.register(SSHKey)
admin.site.register(AddressKey)
