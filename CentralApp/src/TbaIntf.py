
import certifi
import json
import urllib3

from urllib3.contrib import pyopenssl
pyopenssl.inject_into_urllib3()

def get_from_tba_parsed( req_api ):
    
    req_data = get_from_tba( req_api )
    if req_data != '':
        parsed_data = json.loads(req_data)
    else:
        parsed_data = {}
    
    return parsed_data

def get_from_tba( req_api ):
    resp_data = ''
    url_str = 'http://www.thebluealliance.com%s?X-TBA-App-Id=frc1073:scouting-system:v02' % req_api

    http = urllib3.PoolManager( cert_reqs='CERT_REQUIRED',
                                ca_certs=certifi.where())

    resp = http.request('GET', url_str,
                        headers={'User-Agent': 'Mozilla/5.0'})
        
    if resp.status is 200:
        resp_data = resp.data

    return resp_data
    

if __name__ == "__main__":

    #req_api = '/api/v2/team/frc1073'
    req_api = '/api/v2/events/2016'

    result = get_from_tba(req_api)
    
    print result
