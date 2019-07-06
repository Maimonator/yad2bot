import herepy

class LocationManager(object):
    """docstring for LocationManager"""
    def __init__(self, app_id, app_code):
        super(LocationManager, self).__init__()
        self.geo = herepy.geocoder_api.GeocoderApi(app_id=app_id, app_code=app_code)
        self.rout = herepy.RoutingApi(app_id=app_id, app_code=app_code)

    def search_addr(self, addr_name):
        response = self.geo.free_form(addr_name).Response
        if len(response['View']) == 0:
            raise ValueError(f"Could not find address {addr_name}")
        pos = response['View'][0]['Result'][0]['Location']['DisplayPosition']
        return [pos['Latitude'], pos['Longitude']]

    def get_distance_between_addresses(self, addr1, addr2):
        response = self.rout.pedastrian_route(addr1, addr2).response
        distance = response['route'][0]['summary']['distance']
        travel_time = response['route'][0]['summary']['travelTime']
        return distance, travel_time
