import psutil
import time
import datetime
from subprocess import PIPE, Popen

from django.conf import settings
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.utils.dateformat import format

from cgminer import Client
from models import LogAverage

client = Client(getattr(settings, 'CGMINER_HOST', None),
                getattr(settings, 'CGMINER_PORT', None))

BAD_GHASH, GOOD_GHASH = getattr(settings, 'CHIP_OK_GHASH_RANGE', [2,2.8])
BAD_ERRORS, GOOD_ERRORS = getattr(settings, 'CHIP_OK_ERROR_RANGE', [2, 40])

def sizeof_fmt(num):
    for x in [' bytes',' KB',' MB',' GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, ' TB')



def get_cpu_temperature():
    temp = open('/sys/class/thermal/thermal_zone0/temp','rb').readline()
    return float(temp[:2] + '.' + temp[2:])


@login_required
def index(request):
    data = {}
    context = RequestContext(request)

    try:
        summary = client.command('summary')
    except:
        data['offline'] = True
        summary = {}
    else:
        summary = summary['SUMMARY'][0]
        data['offline'] = False

    #summary_lower = {}
    new_summary = {}

    for k, v in summary.iteritems():
        lower = k.lower().replace(' ', '_').replace('%','_')
        if lower =='mhs_av':
            new_summary['ghs_av'] = {'value': round(v/1024, 3), 'label': 'Gh/s av'}
        else:
            new_summary[lower] = {'value': v, 'label': k}

    data['summary'] = new_summary

    try:
        temp = get_cpu_temperature()
    except:
        temp = 0

    system = {
        'cpu_percent': psutil.cpu_percent(),
        'cpu_temp': temp,
        'mem_percent': psutil.virtual_memory().percent,
        'mem_total': sizeof_fmt(psutil.virtual_memory().total),
        'mem_used': sizeof_fmt(psutil.virtual_memory().used),
        'disk_percent': psutil.disk_usage('/').percent,
        'disk_total': sizeof_fmt(psutil.disk_usage('/').total),
        'disk_used': sizeof_fmt(psutil.disk_usage('/').used),
        'eth0_sent': psutil.net_io_counters(pernic=True)['eth0'].bytes_sent,
        'eth0_recv': psutil.net_io_counters(pernic=True)['eth0'].bytes_recv,
    }
    data['system'] = system

    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")

    context.update(data)
    return render_to_response('status/index.html', context,)


@login_required
def realtime(request):
    context = RequestContext(request)
    context.update({})
    return render_to_response('status/realtime.html', context,)

@login_required
def chipinfo(request):
    if request.is_ajax():
        try:
            r = client.command('stats')['STATS'][0]
        except:
            data = None
        else:
            chips = {}

            for k,v in r.iteritems():
                if k.startswith('ghash_'):
                    chips.setdefault(k[6:], {'id': k[6:]})
                    chips[k[6:]]['ghash'] = round(v, 3)
                elif k.startswith('clock_bits_'):
                    chips.setdefault(k[11:], {'id': k[11:]})
                    chips[k[11:]]['bits'] = v
                elif k.startswith('match_work_count_'):
                    chips.setdefault(k[17:], {'id':k[17:]})
                    chips[k[17:]]['works'] = v
                elif k.startswith('hw_errors_'):
                    chips.setdefault(k[10:], {'id':k[10:]})
                    chips[k[10:]]['errors'] = v
            for v in chips.values():
                v['ghash_status'] = 'good' if v['ghash'] >= GOOD_GHASH else 'bad' if v['ghash'] < BAD_GHASH else 'ok'
                v['error_pct'] = round(100.0*v['errors']/(v['works']+v['errors']), 2) if (v['works']+v['errors']) > 0 else 0
                v['error_status'] = 'good' if v['error_pct'] < GOOD_ERRORS else 'bad' if v['error_pct'] > BAD_ERRORS else 'ok'

            slots = sorted(list(set([k.split('_')[0] for k in chips.keys()])))
            data = {
                'slots': [
                    {'id': s,
                     'chips': [chips[k] for k in sorted(chips.keys()) if k.startswith(s)],
                     } for s in slots]
                }
        return HttpResponse(json.dumps(data), mimetype="application/json")
    return render(request, 'status/chipinfo.html')


@login_required
def realtime_data(request):
    try:
        devs = client.command('devs')['DEVS']
    except Exception:
        devs = []
        pass

    data = []
    t = time.time()

    for i, d in enumerate(devs):
        if 'GPU' in d:
            name = 'GPU %s' % d.get('GPU')
        else:
            name = 'unknown %s' % i

        data.append({
            'name': name,
            'data': [{
                'x': t,
                'y': d.get('MHS 5s', 0)
            }]
        })

    data = sorted(data, key=lambda dev: dev['name'])

    return HttpResponse(json.dumps(data), mimetype="application/json")


SPLIT = 500

@login_required
def av_data(request):
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=720)
    logs = LogAverage.objects.filter(time__gt=time_threshold).values()

    values = []
    for l in logs:
        values.append({
            'x': int(format(l['time'], 'U')),
            'y': float(l.get('mhs', 0))
        })

    try:
        values.append({
            'x': time.time(),
            'y': client.command('summary')['SUMMARY'][0].get('MHS av')
        })
    except Exception:
        values.append({
            'x': time.time(),
            'y': 0
        })

    data = [{
        'key': 'Hashrate',
        'values': values
    }]

    return HttpResponse(json.dumps(data), mimetype="application/json")
