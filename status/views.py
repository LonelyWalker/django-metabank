import psutil
import time
import datetime
from subprocess import PIPE, Popen

from django.conf import settings
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.utils.dateformat import format
from django.views.decorators.csrf import csrf_exempt

from cgminer import Client
from models import LogAverage

client = Client(getattr(settings, 'CGMINER_HOST', None),
                getattr(settings, 'CGMINER_PORT', None))

BAD_GHASH, GOOD_GHASH = getattr(settings, 'CHIP_OK_GHASH_RANGE', [2,2.8])
BAD_ERRORS, GOOD_ERRORS = getattr(settings, 'CHIP_OK_ERROR_RANGE', [40, 2])



def sizeof_fmt(num):
    for x in [' bytes',' KB',' MB',' GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, ' TB')



def get_cpu_temperature():
    temp = open('/sys/class/thermal/thermal_zone0/temp','rb').readline()
    return float(temp[:2] + '.' + temp[2:])



# Gives a human-readable uptime string
def uptime():
    try:
        f = open( "/proc/uptime" )
        contents = f.read().split()
        f.close()
    except:
       return "Cannot open uptime file: /proc/uptime"

    total_seconds = float(contents[0])

    # Helper vars:
    MINUTE  = 60
    HOUR    = MINUTE * 60
    DAY     = HOUR * 24

    # Get the days, hours, etc:
    days    = int( total_seconds / DAY )
    hours   = int( ( total_seconds % DAY ) / HOUR )
    minutes = int( ( total_seconds % HOUR ) / MINUTE )
    seconds = int( total_seconds % MINUTE )

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
    if len(string) > 0 or hours > 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
    if len(string) > 0 or minutes > 0:
        string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )

    return string;



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
            new_summary['ghs_av'] = {'value': round(v/1000, 3), 'label': 'Gh/s av'}
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
        'eth0_sent': sizeof_fmt(psutil.net_io_counters(pernic=True)['eth0'].bytes_sent),
        'eth0_recv': sizeof_fmt(psutil.net_io_counters(pernic=True)['eth0'].bytes_recv),
        'wlan0_sent': sizeof_fmt(psutil.net_io_counters(pernic=True)['wlan0'].bytes_sent),
        'wlan0_recv': sizeof_fmt(psutil.net_io_counters(pernic=True)['wlan0'].bytes_recv),
        'server_uptime': uptime(),
    }
    data['system'] = system

    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")

    context.update(data)
    return render_to_response('status/index.html', context,)


@login_required
def devicehr(request):
    context = RequestContext(request)
    context.update({})
    return render_to_response('status/devicehr.html', context,)

@login_required
def chipinfo(request):
    return render(request, 'status/chipinfo.html')

@login_required
def chipinfo_data(request):
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

        slots = sorted(list(set([k.split('_')[0] for k in chips.keys()])), key=lambda s: int(s) if s.isdigit() else s)
        data = {
            'slots': [
                {'id': s,
                 'chips': [chips[k] for k in sorted(chips.keys(),
                                                    key=lambda c: int(c.split('_')[1]) if c.split('_')[1].isdigit() else c)
                           if k.startswith(s+'_')],
                 } for s in slots]
            }
        for slot in data['slots']:
            for key in ('ghash', 'works', 'errors'):
                slot[key] = round(sum(c[key] for c in slot['chips']), 3)
            slot['ghash_status'] = 'good' if slot['ghash'] >= GOOD_GHASH*len(slot['chips']) else 'bad' if slot['ghash'] < BAD_GHASH*len(slot['chips']) else 'ok'
            slot['error_pct'] = round(100.0*slot['errors']/(slot['works']+slot['errors']), 2) if (slot['works']+slot['errors']) > 0 else 0
            slot['error_status'] = 'good' if slot['error_pct'] < GOOD_ERRORS else 'bad' if slot['error_pct'] > BAD_ERRORS else 'ok'

    return HttpResponse(json.dumps(data), mimetype="application/json")

@login_required
@csrf_exempt
def set_bits(request, direction):
    if request.method == 'POST':
        try:
            slot, chip = request.REQUEST['chip'].split('_')
            bits = int(request.REQUEST['bits']) + (1 if direction == 'up' else -1)
        except Exception, e:
            return HttpResponseBadRequest("Bad arguments")

        try:
            data = client.command('setclkb', slot, chip, bits)['STATUS'][0]
        except Exception, e:
            data = {'STATUS': 'E',
                    'Msg': unicode(e)}
        return HttpResponse(json.dumps(data), mimetype="application/json")
    return HttpResponseNotAllowed(['POST'])

@login_required
def devicehr_data(request):
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
    logs = LogAverage.objects.values()

    values = []
    for l in logs:
        values.append({
            'x': int(format(l['time'], 'U')),
            'y': float(l.get('mhs', 0)/1000)
        })

    try:
        values.append({
            'x': time.time(),
            'y': client.command('summary')['SUMMARY'][0].get('MHS av', 0)/1000
        })
    except Exception:
        values.append({
            'x': time.time(),
            'y': 0
        })

    data = [{
        'key': 'Hashrate (GH/s)',
        'values': values
    }]

    return HttpResponse(json.dumps(data), mimetype="application/json")


@login_required
def realtime(request):
    context = RequestContext(request)
    context.update({})
    return render_to_response('status/realtime.html', context,)


@login_required
def realtime_data(request):
    c = Client()
    data = {}

    try:
        stats = c.command('stats')['STATS']
    except Exception:
        stats = []

    data['stats'] = stats

    return HttpResponse(json.dumps(data), mimetype="application/json")
