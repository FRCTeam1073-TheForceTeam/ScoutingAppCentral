'''
Created on Feb 08, 2013

@author: ksthilaire
'''

import re
import base64
import web

allowed = (
    ('user','dean'),
    ('user2','woodie')
)

    
def auth_user():
    auth = web.ctx.env.get('HTTP_AUTHORIZATION')
    
    authreq = False
    if auth is None:
        authreq = True
    else:
        auth = re.sub('^Basic ','',auth)
        username,password = base64.decodestring(auth).split(':')
        if (username,password) in allowed:
            raise web.seeother('/home')
        else:
            authreq = True
    if authreq:
        web.header('WWW-Authenticate','Basic realm="Auth example"')
        web.ctx.status = '401 Unauthorized'
        return

def check_access():
    if web.ctx.env.get('HTTP_AUTHORIZATION') is None:
        raise web.seeother('/login')

