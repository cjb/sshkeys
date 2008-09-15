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

def view404(request):
    return HttpResponse("No keys were found for that address.", status=404)

def list(request, **kwargs):
    kwargs['allow_empty'] = True
    kwargs['queryset'] = \
      AddressKey.objects.filter(verified=True).order_by("address__address")
    return object_list(request, **kwargs)

def detail(request, address=None, id=None):
    if address:
        keyobjs = AddressKey.objects.filter(verified=True, 
                                        address__address=address)
    elif id:
        keyobjs = AddressKey.objects.filter(verified=True, 
                                        id=id)

    if not keyobjs:
        raise Http404

    keylist = set()
    for key in keyobjs:
        keylist.add(unicode(key.sshkey))

    response = HttpResponse("\n".join(keylist), mimetype="text/plain")
    # wget seems to ignore content-disposition.  What's up with that?
    response['Content-Disposition'] = 'attachment; filename=authorized_keys'
    return response

def upload(request):
    address_str = request.POST['address']
    keytext_str = request.POST['keytext']
    if not "@" in address_str:
        return HttpResponse("Address given is not a valid e-mail address.", status=404)
    if not keytext_str.startswith("ssh-"):
        return HttpResponse("Key given is not an ASCII ssh public key.", status=404)
    newaddress, undef = Address.objects.get_or_create(address=address_str)
    newkey, undef = SSHKey.objects.get_or_create(keytext=keytext_str)
    newrel, created = AddressKey.objects.get_or_create(
                          address=newaddress, sshkey=newkey,
                          defaults={'date_added': datetime.now(),
                                    'verified': False,
                                    'token_sent': datetime.now()})

    # "if created:" can tell us whether we created a new pair or
    # just sent out a reminder about an old one, if we care.
    newrel.send_confirmation(newrel)
    return render_to_response("keys/address_uploaded.html")

def search(request, **kwargs):
    search_str = request.POST['search']
    search = search_str.rstrip()
    kwargs['allow_empty'] = True
    kwargs['queryset'] = AddressKey.objects.filter(verified=True,
        address__address__contains=search).order_by("address__address")
    return object_list(request, extra_context={"search": search}, **kwargs)

def confirm(request, token):
    obj = AddressKey.objects.filter(token=token)
    if len(obj) == 1:
        if AddressKey.confirm_token(obj[0]) is True:
                return render_to_response("keys/address_verified.html")

    return render_to_response("keys/address_verifyfailed.html")

def download(request):
    search_str = request.POST['search']
    keys = AddressKey.objects.filter(verified=True,
        address__address__contains=search_str).order_by("address__address")

    keylist = set()
    for key in keys:
        keylist.add(unicode(key.sshkey))

    return HttpResponse("\n".join(keylist), mimetype="text/plain")
