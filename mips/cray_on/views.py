import socket

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

@view_config(route_name='crays', renderer='templates/crays.pt', request_method='GET', permission='authenticated')
def crays(request):
    settings = request.registry.settings

    cray_managers = [{'name': manager} for manager in settings['cray.manager'].strip().split() if manager]

    for manager in cray_managers:

        number = int(settings.get('cray.'+manager['name']+'.number', 0))

        if not number:
            pass
            # log warning
        manager.update({'number': number})

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
    manager = request.settings.get('%s.ip' % request.matchdict['manager'])
    if not manager:
        pass

    port = request.settings.get('%s.port' % request.matchdict['manager'], 9496)
    # todo check ICS

    sock.sendto("lame%s" % request.matchdict['blade'], (int(port), manager))

    # todo flash
    return
