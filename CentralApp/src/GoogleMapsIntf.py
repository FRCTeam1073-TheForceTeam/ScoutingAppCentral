import traceback

import googlemaps
from datetime import datetime
import json

gmaps = googlemaps.Client(key='AIzaSyA17MA82Z5UXV0KaDbTg7MadrbRjdpEkG4')

def get_geo_location( address_str ):
    geo_location = None
    try:
        geocode_results = gmaps.geocode( address_str )
        
        if geocode_results is None:
            print 'Geo location not found for %s' % address_str
        else:
            if len(geocode_results) > 0:          
                geocode_result = geocode_results[0]
                geo_location = geocode_result['geometry']['location']
            else:
                print 'Empty Geo location for %s' % address_str        
    except Exception:
        print 'Error obtaining Geo location for %s' % address_str
        print(traceback.format_exc())
        raise
        
    return geo_location


if __name__ == "__main__":

    # Geocoding an address
    #geo_location = get_geo_location('24 Cavalier Ct, Hollis, NH')

    geo_location = get_geo_location('25 Columbus Ave. Concord NH')
    
    geo_location_json = json.dumps(geo_location)
    
    parsed_geo_location = json.loads(geo_location_json)

    print parsed_geo_location
    
