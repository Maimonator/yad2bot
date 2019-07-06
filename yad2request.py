import ipdb
from abc import abstractmethod
import re
from bs4 import BeautifulSoup
import copy
import requests

city=5000 # Tel Aviv


property=1 # always needed?
rooms=3-4 # number of rooms
price=5000-7000 # price
pandorDoors=1 # pandoorDoors
parking=1 # parking
elevator=1 # elevator
airConditioner=1 # air conditioner
balcony=1 # balcony
sunProch=1 # su
shelter=1 # mamad
bars=1 # soragim
warhouse=1 # mahsan
accessibility=1 # nehim
renovated=1 # meshupetzet
furniture=1 # merohetet
pets=1 # pets
forPartners=1 #
longTerm=1 #
asset_exclusive=1 #
floor=1000-1 # floors
squaremeter=60-80 # size
EnterDate=1-9-2019 # start date
# comment=


class Yad2SearchParam(object):
    """docstring for Yad2SearchParam"""
    def __init__(self, name, value):
        super(Yad2SearchParam, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        param = self.name
        value = self.value
        return f"{param}={value}"

class Yad2SearchBoolean(Yad2SearchParam):
    """docstring for Yad2SearchBoolean"""
    def __init__(self, name):
        super(Yad2SearchBoolean, self).__init__(name, value=1)

class Yad2SearchRange(object):
    """docstring for Yad2SearchRange"""
    def __init__(self, name, min_val, max_val):
        value = f"{min_value}-{max_val}"
        super(Yad2SearchRange, self).__init__(name, value)

class Yad2SearchDate(object):
    """docstring for Yad2SearchDate"""
    DATE_FORMAT = "%d-%m-%Y"
    def __init__(self, name, start_date):
        value = start_date.strftime(Yad2SearchDate.DATE_FORMAT)
        super(Yad2SearchDate, self).__init__(name, value)


class Yad2Apartment(object):
    """docstring for Yad2Apartment"""
    HTML_ITEMID_KEY = "itemid"
    HTML_PRICE_KEY = "_price"
    HTML_ROOM_KEY = "data_rooms"
    HTML_FLOOR_KEY = "data_floor"
    HTML_SIZE_KEY = "data_SquareMeter"
    HTML_ADDRESS_KEY = "title"
    def __init__(self, item_id, price, address, num_rooms):
        super(Yad2Apartment, self).__init__()
        self.item_id = item_id
        self.price = price
        self.address = address
        self.num_rooms = num_rooms

    def __str__(self):
        price = self.price
        num_rooms = self.num_rooms
        address = self.address
        itemid = self.item_id
        url = f"https://www.yad2.co.il/item/{itemid}/"
        return f"Price : {price}\nNumber Of Rooms: {num_rooms}\nAddress: {address}\nURL: {url}"


    def to_dict(self):
        dic = {"id": self.item_id,
        "price": self.price,
        "address": self.address,
        "num_rooms": self.num_rooms,
        }
        return dic

    def to_string(self, travel_distance, travel_time):
        st = str(self)
        st = f"{st}\nDistance: {travel_distance}\n Time: {travel_time}"
        return st


    def __eq__(self, other):
        pass

    @classmethod
    def from_dict(cls, dic):
        item_id = dic['id']
        price = dic['price']
        num_rooms = dic['num_rooms']
        address = dic['address']
        return cls(item_id, price, num_rooms, address)

    @classmethod
    def from_html_div(cls, bs4_tag):
        # ipdb.set_trace()
        item_id = bs4_tag[Yad2Apartment.HTML_ITEMID_KEY]
        price_tag = bs4_tag.findAll("div", {"id" : lambda x : x and x.find(Yad2Apartment.HTML_PRICE_KEY)})[-1]
        address_tag = bs4_tag.findAll("span", {"class" : lambda x : x and x.startswith(Yad2Apartment.HTML_ADDRESS_KEY)})[-1]
        num_rooms_tag = bs4_tag.findAll("span", {"id" : lambda  x : x and x.startswith(Yad2Apartment.HTML_ROOM_KEY)})[-1]
        floor_tag = bs4_tag.findAll("span", {"id" : lambda x : x and x.startswith(Yad2Apartment.HTML_FLOOR_KEY)})[-1]
        size_tag = bs4_tag.findAll("span", {"id" : lambda x : x and x.startswith(Yad2Apartment.HTML_SIZE_KEY)})[-1]

        # print(price_tag)
        # ipdb.set_trace()
        price =  price_tag.contents[0].strip()
        num_rooms = num_rooms_tag.contents[0].strip()
        address = address_tag.contents[0].strip()

        return cls(item_id, price, address, num_rooms)

class Yad2Request(object):
    """docstring for Yad2Request"""
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    PARAM_CONCATENATOR = "&"
    YAD2_SESSION_KEY = "yad2_session"
    def __init__(self, base_url, search_params, cookie):
        super(Yad2Request, self).__init__()
        self.base_url = base_url
        self.search_params = search_params
        self.cookie = cookie

    @staticmethod
    def _generate_params_str(params_dict):
        params = []
        for key, val in params_dict.items():
            params.append(Yad2SearchParam(key, val))

        params = map(lambda x: str(x), params)
        params = Yad2Request.PARAM_CONCATENATOR.join(params)
        return params

    @staticmethod
    def _construct_search_url(base_url, params):
        params = Yad2Request._generate_params_str(params)
        return f"{base_url}?{params}"

    @staticmethod
    def _append_params(url, params):
        params = Yad2Request._generate_params_str(params)
        return f"{url}&{params}"

    def send_request(self, extra_params):
        cookies = {Yad2Request : self.cookie}
        headers = {"User-Agent" : Yad2Request.USER_AGENT}
        params = copy.copy(self.search_params)
        params.update(extra_params)
        url = Yad2Request._construct_search_url(self.base_url, params)

        response = requests.get(url, cookies=cookies, headers=headers)
        return response

    def _get_items_from_page(self, page_num):
        extra_params = {"page":page_num}
        response = self.send_request(extra_params)
        html = BeautifulSoup(response.content, 'html.parser')
        items_divs = html.findAll("div", {"id" : lambda x : x and x.startswith("feed_item_") and not x.endswith("price")})
        items_divs = filter(lambda x: x is not None , items_divs)
        # x = list(items_divs)
        # ipdb.set_trace()
        items = map(lambda x: Yad2Apartment.from_html_div(x), items_divs)
        return items
