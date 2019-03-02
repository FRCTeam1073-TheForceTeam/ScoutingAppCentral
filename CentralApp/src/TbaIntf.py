
import certifi
import json
import urllib3

from urllib3.contrib import pyopenssl
pyopenssl.inject_into_urllib3()

# Auth Key from the TBE account
auth_key_str = 'Hv3ANwNNnNk4pEBEIZzk2wtZPAmWQEJqJGu9mxbgoqqCu0h27eUqaEJpDWr6Vguj'

error_logged = False

def get_from_tba_parsed( req_api ):
    
    req_data = get_from_tba( req_api )
    if req_data != '':
        parsed_data = json.loads(req_data)
    else:
        parsed_data = {}
    
    return parsed_data

def get_from_tba( req_api ):
    global error_logged
    resp_data = ''
    url_str = 'http://www.thebluealliance.com%s' % req_api

    try:
        http = urllib3.PoolManager( cert_reqs='CERT_REQUIRED',
                                    ca_certs=certifi.where())
    
        resp = http.request('GET', url_str,
                            headers={'User-Agent': 'Mozilla/5.0',
                                     'X-TBA-Auth-Key': auth_key_str})

            
        if resp.status is 200:
            resp_data = resp.data
    except:
        if not error_logged:
            print 'Error accessing TheBlueAlliance - check internet connection'
            error_logged = True
        pass

    return resp_data
    

if __name__ == "__main__":

    #req_api = '/api/v2/team/frc1073'
    req_api = '/api/v2/events/2016'

    result = get_from_tba(req_api)
    
    print result
