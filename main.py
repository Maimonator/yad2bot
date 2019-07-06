import random
import ipdb
from telebot import AsyncTeleBot
import os
import argparse
import json
from yad2db import Yad2DB
from yad2request import Yad2Request, Yad2Apartment
import time
import configparser
import traceback
from locationmanager import LocationManager

CONFIG_PATH = "yad2.conf"
config = configparser.ConfigParser()
config.sections()
config.read('yad2.conf')

bot = AsyncTeleBot(config['DEFAULT']['token'])

@bot.message_handler(commands=['start'])
def command_subscribe(msg):
    with Yad2DB(msg.from_user.id) as cdb:
        bot.reply_to(msg, "Subscribed successfuly")

@bot.message_handler(commands=['query'])
def command_set_query(msg):
    bot.reply_to(msg, "Hiii")

def get_params(param_list):
    param_list = [v.split("=") for v in param_list]
    data = {v[0]:v[1] for v in param_list}
    return data

def configure(args):
    data = {"key": args.key,
            "token": args.token}
    config['DEFAULT'] = data
    config['PARAMS'] = get_params(args.params)
    with open(CONFIG_PATH, "w") as writer:
        config.write(writer)


def poll_function(lm, base_addr):
    users = os.listdir("db")
    for user in users:
        request = Yad2Request("https://www.yad2.co.il/realestate/rent", dict(config['PARAMS'].items()), config['DEFAULT']['key'])
        items = request._get_items_from_page(1)
        with Yad2DB(user) as db:
            for item in items:
                item_loc = lm.search_addr("Israel, Tel Aviv {}".format(item.address))
                distance, travel_time = lm.get_distance_between_addresses(base_addr, item_loc)
                print(distance)
                print(travel_time)
                if distance <= int(config['LOCATION']['min_distance']):

                    if db.is_updated_or_new(item):
                        db.add_item(item)
                        bot.send_message(user, item.to_string(distance, travel_time))


def polling(args):
    # ipdb.set_trace()
    lm = LocationManager(config['DEFAULT']['here_appid'], config['DEFAULT']['here_appcode'])
    base_addr = lm.search_addr(config['LOCATION']['base_address'])

    while True:
        try:
            poll_function(lm, base_addr)
            time.sleep(5)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            time_to_wait = args.timeout + random.randint(-args.timeout / 20, args.timeout / 20)
            time.sleep(time_to_wait)


def main():
    parser = argparse.ArgumentParser("Yad2Bot Controller")
    subparsers = parser.add_subparsers()
    configure_parser = subparsers.add_parser("configure")
    configure_parser.add_argument(
        "--key", help="yad2 session key", required=True)
    configure_parser.add_argument(
        "--token", help="Telegram bot API token", required=True)
    configure_parser.add_argument(
        "--params", help="yad2 params followed by '='", nargs='+')
    configure_parser.set_defaults(do=configure)

    poll_parser = subparsers.add_parser("poll")
    poll_parser.add_argument("--timeout", help="Time to wait, always add a random of 10%, default is 600 seconds", default=600, type=int)
    poll_parser.set_defaults(do=polling)

    args = parser.parse_args()
    try:
        args.do(args)
    except Exception as ex:
        print(ex)
        traceback.print_exc(limit=None, file=None)


if __name__ == '__main__':
    main()
