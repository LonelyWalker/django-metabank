import psutil
import time
import datetime
from subprocess import PIPE, Popen

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.utils.dateformat import format

from cgminer import Client
from models import LogAverage


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
    c = Client()
    data = {}
    context = RequestContext(request)

    try:
        summary = c.command('summary')
    except:
        data['offline'] = True
        summary = {}
    else:
        summary = summary['SUMMARY'][0]
        data['offline'] = False

    #summary_lower = {}
    new_summary = {}

    for k, v in summary.iteritems():
        lower = k.lower().replace(' ', '_')
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
def realtime_data(request):

    c = Client()

    try:
        devs = c.command('devs')['DEVS']
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

    c = Client()
    try:
        values.append({
            'x': time.time(),
            'y': c.command('summary')['SUMMARY'][0].get('MHS av')
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
