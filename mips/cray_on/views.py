import socket
import urllib2

import datetime
import pytz


from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember

import icalendar


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

STATUS = {'ON' : 'on',
          'OFF': 'off'}

# todo cache docpile
def readCalendar(url):
    req = urllib2.urlopen(url)
    return icalendar.Calendar.from_ical(req.read())


def isMipsOpen(calendar, now):
    return any([checkEvent(event, now) for event in calendar.subcomponents])

def checkEvent(event, now):
    return event['DTSTART'].dt <= now and event['DTEND'].dt >= now



@view_config(route_name='crays', renderer='templates/crays.pt', request_method='GET', permission='authenticated')
def crays(request):
    settings = request.registry.settings

    cray_managers = [{'name': manager,
                      'ip' : settings['cray.%s.ip' % manager],
                      'port' : int(settings['cray.%s.port' % manager]),
                      'number': int(settings['cray.%s.number' % manager])}
                      for manager in settings['cray.manager'].strip().split() if manager]

    for manager in cray_managers:
        blades = []
        for blade in range(1, manager['number'] + 1):
            sock.sendto('stat%d' % blade, (manager['ip'], manager['port']))
            try:
                data, ip = sock.recvfrom(2048)
            except socket.timeout:
                print "timeout !"
                data = 'unknown'

            status = STATUS.get(data, 'unknown')

            blades.append({'status': status, 'id': blade})

        manager.update({'blades': blades})

    return {'managers': cray_managers}


@view_config(route_name='home', renderer='templates/home.pt', request_method='GET', permission='view')
def home(request):
    return {'project': 'mips.cray_on'}


@view_config(route_name='login_submit', request_method='POST', permission='view')
def login_submit(request):
    login = request.POST.get('login')
    password = request.POST.get('password')

    if (login == request.registry.settings['login']) and \
        (password == request.registry.settings['password']):

        headers = remember(request, login)
        request.session['login'] = login
        request.session.flash(u'Logged in successfully.')

        return HTTPFound(location=request.route_path('crays'), headers=headers)
    else:
        return HTTPFound(location=request.route_path('home'))


@view_config(route_name='switch_on', request_method='POST', permission='authenticated', check_csrf=True, renderer='json')
def switch_on(request):

    now = pytz.utc.localize(datetime.datetime.utcnow())
    calendar = readCalendar(request.registry.settings['calendar_url'])

    if not isMipsOpen(calendar, now):


        manager = request.registry.settings.get('cray.%s.ip' % request.matchdict['manager'])
        if not manager:
            pass

        port = request.registry.settings.get('cray.%s.port' % request.matchdict['manager'], 9496)

        print "lame%s" % request.matchdict['blade']
        print manager
        # todo proper logs
        sock.sendto("lame%s" % request.matchdict['blade'], (manager, int(port)))

        # todo flash
    else:
        pass
        # todo flash
    return HTTPFound(location=request.route_path('crays'))
