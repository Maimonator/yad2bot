from telebot import AsyncTeleBot
import configparser
from yad2db import Yad2DB

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
