from django.conf import settings
from django.template.context import RequestContext
from django.shortcuts import redirect, render_to_response

from tools import miner_message as mm

from cgminer import Client
from forms import AddPool

client = Client(getattr(settings, 'CGMINER_HOST', None),
                getattr(settings, 'CGMINER_PORT', None))

ACTIVE_STATUS_SECONDS = getattr(settings, 'ACTIVE_STATUS_SECONDS', 60)
STALE_STATUS_SECONDS = getattr(settings, 'STALE_STATUS_SECONDS', 900)

def pools(request):
    context = RequestContext(request)

    try:
        res = client.command('pools')
        context.update({ 'pool_list': res['POOLS'] })
        now = res['STATUS'][0]['When']
        for pool in context['pool_list']:
            last = pool['Last Share Time']
            if now-last < ACTIVE_STATUS_SECONDS:
                pool['status'] = 'active'
            elif now-last < STALE_STATUS_SECONDS:
                pool['status'] = 'stale'
    except Exception, e:
        context.update({ 'offline': True })

    return render_to_response('pools/pool_list.html', context,)


def remove(request, POOL):
    res = client.command('removepool', POOL)
    if mm(request, res):
        client.command('save')

    return redirect('pools_list')


def switch(request, POOL):
    res = client.command('switchpool', POOL)
    if mm(request, res):
        client.command('save')

    return redirect('pools_list')


def add(request):
    context = RequestContext(request)

    if request.POST:
        form = AddPool(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            res = client.command('addpool', cd.get('url'), cd.get('user'), cd.get('password'))
            if mm(request, res):
                client.command('save')
                return redirect('pools_list')

    else:
        form = AddPool()

    context.update({'form': form})

    return render_to_response('pools/pool_form.html', context,)


def enable(request, POOL):
    res = client.command('enablepool', POOL)
    if mm(request, res):
        client.command('save')

    return redirect('pools_list')


def disable(request, POOL):
    res = client.command('disablepool', POOL)
    if mm(request, res):
        client.command('save')

    return redirect('pools_list')
