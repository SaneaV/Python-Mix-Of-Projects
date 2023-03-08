import telebot
from telebot import types
from bs4 import BeautifulSoup
import requests
import os
from flask import Flask
import logging
from flask import request

TOKEN = "${TOKEN}"
bot = telebot.TeleBot(TOKEN)
BASTV = 'https://bas-tv.md/'
FEEDBACK = 'http://feedback.md/category/актуальное/'
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_menu(message):
    chat_id = message.chat.id
    photoURL = 'https://i.imgur.com/a6FPw7o.jpeg'
    caption = 'Выберите нужный пункт на клавиатуре, чтобы получить новую информацию.'
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itemKeyboard_1 = types.KeyboardButton('Последние новости BasTV')
    itemKeyboard_2 = types.KeyboardButton('Последние новости FeedBack')
    markup.row(itemKeyboard_1)
    markup.row(itemKeyboard_2)
    bot.send_photo(chat_id, photoURL, caption, reply_markup = markup)


@bot.message_handler(content_types=["text"])
def send_menu(message):
    chat_id = message.chat.id

    if message.text == 'Последние новости BasTV':
        bot.send_message(chat_id, text="Процесс сбора информации начался. Ожидайте...")
        allNames, allDescription, allPhotos, allLinks = basTVParser()
        for (p,n,d,l) in zip(allPhotos, allNames, allDescription, allLinks):
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Продолжить чтение", url=l)
            keyboard.add(url_button)
            bot.send_photo(chat_id, photo=p, caption = '<b>'+n+'</b>'+'\n\n'+ d, reply_markup=keyboard, parse_mode='HTML')

    if message.text == 'Последние новости FeedBack':
        bot.send_message(chat_id, text="Процесс сбора информации начался. Ожидайте...")
        allNames, allDescription, allPhotos, allLinks = feedBackParser()
        for (p,n,d,l) in zip(allPhotos, allNames, allDescription, allLinks):
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Продолжить чтение", url=l)
            keyboard.add(url_button)
            bot.send_photo(chat_id, photo=p, caption = '<b>'+n+'</b>'+'\n\n'+ d, reply_markup=keyboard, parse_mode='HTML')

def basTVParser():
    html = requests.get(BASTV)
    soup = BeautifulSoup(html.text, "html.parser")
    lastNews = soup.find('div', class_= 'listing listing-grid listing-grid-1 clearfix columns-2')
    
    allDescriptionHTML = lastNews.findAll('div', class_='post-summary')
    allNamesHTML = lastNews.findAll('h2', class_='title')
    allPhotosHTML = lastNews.findAll('a', class_='img-holder')
    allLinksHTML = lastNews.findAll('a', class_='img-holder')

    allPhotos = []
    allDescription = []
    allNames = []
    allLinks = []

    for a in allPhotosHTML:
        allPhotos.append(a.get("data-src"))

    for a in allLinksHTML:
        allLinks.append(a.get("href"))

    for a in allDescriptionHTML:
        allDescription.append(a.text.strip())

    for a in allNamesHTML:
        allNames.append(a.text.strip())

    return allNames[::-1], allDescription[::-1], allPhotos[::-1], allLinks[::-1]

def feedBackParser():
    html = requests.get(FEEDBACK)
    soup = BeautifulSoup(html.text, "html.parser")
    lastNews = soup.find('div', class_= 'jumla-posts-lists')
    
    allDescriptionHTML = lastNews.find_all('p')
    allNamesHTML = lastNews.find_all('div', class_="post-media")

    allPhotos = []
    allDescription = []
    allNames = []
    allLinks = []

    for a in allDescriptionHTML:
        allDescription.append(a.text.strip())

    for a in allNamesHTML:
        allLinks.append(a.find('a').get('href'))
        allNames.append(a.find('a').get('title'))
        allPhotos.append(a.find('img').get('src'))

    return allNames[::-1], allDescription[::-1], allPhotos[::-1], allLinks[::-1]

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://stark-garden-76424.herokuapp.com/' + TOKEN)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))