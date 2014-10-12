from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from mips.cray_on.permissions import RootFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session.secret']
        )

    authn_policy = SessionAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory
        )

    for include in ['pyramid_fanstatic',
                    'pyramid_chameleon',
                    'rebecca.fanstatic', ]:

        config.include(include)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login_submit', '/login_submit')
    config.add_route('logout', '/logout')
    config.add_route('crays', '/crays')
    config.add_route('switch_on', '/cray/{manager}/{number}')

    config.scan()


    config.add_fanstatic_resources(['js.bootstrap.bootstrap',
                                    'js.bootstrap.bootstrap_theme',
                                    'css.fontawesome.fontawesome',
                                    ], r'.*\.pt')

    return config.make_wsgi_app()
