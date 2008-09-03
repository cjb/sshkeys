from django.shortcuts import render_to_response, get_object_or_404
from sshkeys.keys.models import Address
from django.http import Http404, HttpResponse
from django.views.generic.list_detail import object_list, object_detail
from sshkeys.keys.models import Address, SSHKey, AddressKey
from datetime import datetime


# favour django-mailer but fall back to django.core.mail
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

def index(request):
    return render_to_response("keys/address_index.html")

def list(request, **kwargs):
    kwargs['allow_empty'] = True
    kwargs['queryset'] = Address.objects.all().order_by("address")
    return object_list(request, **kwargs)

def detail(request, address):
    owner = Address.objects.get(address=address)
    keys = [unicode(key) for key in owner.sshkey_set.all()]
    return HttpResponse("\n".join(keys), mimetype="text/plain")

def upload(request):
    address_str = request.POST['address']
    keytext_str = request.POST['keytext']
    if not "@" in address_str:
        raise Http404, "Address given is not a valid e-mail address."
    if not keytext_str.startswith("ssh-"):
        raise Http404, "Key given is not an ASCII ssh public key."
    newaddress, undef = Address.objects.get_or_create(address=address_str)
    newkey, undef = SSHKey.objects.get_or_create(keytext=keytext_str)
    newrel, created = AddressKey.objects.get_or_create(
                          address=newaddress, sshkey=newkey,
                          defaults={'date_added': datetime.now(),
                                    'verified': False,
                                    'token_sent': datetime.now()})
    if created:
        newrel.send_confirmation(newrel)
        return render_to_response("keys/address_uploaded.html")
    else:
        newrel.send_confirmation(newrel)
        return render_to_response("keys/address_index.html")

def search(request, **kwargs):
    search_str = request.POST['search']
    search = search_str.rstrip()
    kwargs['allow_empty'] = True
    kwargs['queryset'] = Address.objects.filter(address__contains=search)
    return object_list(request, extra_context={"search": search}, **kwargs)

def confirm(request, token):
    obj = AddressKey.objects.filter(token=token)
    if len(obj) == 1:
        if AddressKey.confirm_token(obj[0]) is True:
                return render_to_response("keys/address_verified.html")

    return render_to_response("keys/address_verifyfailed.html")

def download(request):
    search_str = request.POST['search']
    addresses = Address.objects.filter(address__contains=search_str)
    keys = set()
    for address in addresses:
        for key in address.sshkey_set.all():
            keys.add(unicode(key))

    if len(keys) > 0:
        return HttpResponse("\n".join(keys), mimetype="text/plain")
    else:
        raise Http404
