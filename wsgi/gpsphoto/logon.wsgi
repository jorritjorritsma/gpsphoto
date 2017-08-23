from webob import Request, Response
import sys
import base64
import json

def application(environ, start_response):
    req = Request(environ)
    
    # let's see if we received a state variable
    # state is base64 encoded json object with referer:<origin> in it for now
    try:
        state = req.GET['state']
        stateArgs = json.loads(base64.b64decode(state))
        # let's redirect user back where he / she came from before authenticating
        res = Response()
        res.status = 303
        res.location = stateArgs['referer']
    except:
        # we did not receive a state let's just show empty page
        res = Response()

    return res(environ, start_response)
