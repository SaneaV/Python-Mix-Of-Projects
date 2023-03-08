from flask import Flask
from flask import request
from flask import jsonify
import requests
import json
import re
from flask_sslify import SSLify
from bs4 import BeautifulSoup
import os

app = Flask(__name__) #__name__ - Ссылка на текущий файл
TOKEN = "${TOKEN}"
URL = "https://api.telegram.org/bot" + TOKEN + "/"
SSLify = SSLify(app)
BASTV = 'https://bas-tv.md/'
FEEDBACK = 'http://feedback.md/category/актуальное/'

def writeJson(data, fileName = "answer.json"):
    with open(fileName, "w", encoding='utf8') as f:
        json.dump(data, f, indent = 2, ensure_ascii = False)


def keyBoardSendMessage(chat_id):
    url = URL + "sendPhoto"
    photoURL = 'https://i.imgur.com/a6FPw7o.jpeg'
    keyboard = {"keyboard":[["Последние новости BASTV"],["Последние новости FeedBack"]], "resize_keyboard":True, 'remove_keyboard': True}
    answer = {'chat_id': chat_id, 'photo': photoURL,  "caption":'Выберите нужный пункт на клавиатуре, чтобы получить новую информацию.', 'reply_markup': keyboard}
    r = requests.post(url, json=answer)

def menuSendMessage(chat_id):
    url = URL + "sendPhoto"
    photoURL = 'https://i.imgur.com/n1OeU8N.jpg'
    keyboard = {"keyboard":[["Вернуться в меню"]], "resize_keyboard":True}
    answer = {'chat_id': chat_id, 'photo':photoURL, 'caption':"Чтобы вернуться в меню нажмите кнопку ниже, далее \"Вернуться в меню\".", 'reply_markup': keyboard}
    r = requests.post(url, json=answer)

def newsSendMessage(chat_id, photoURL, name, descriprion, links):
    url = URL + "sendPhoto"
    keyboard={ "inline_keyboard": [ [ {"text": "Продолжить чтение", "url": links} ] ] }
    answer = {'chat_id': chat_id, 'photo': photoURL, 'caption': "<b>"+name+"</b>"+'\n\n'+descriprion, 'reply_markup': keyboard, "parse_mode": "HTML"}
    r = requests.post(url, json = answer)

def sendMessage(chat_id, text):
    url = URL + "sendMessage"
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json = answer)

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

    return allNames, allDescription, allPhotos, allLinks

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

    return allNames, allDescription, allPhotos, allLinks

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']

        if message == 'Последние новости BASTV':
            allNames, allDescription, allPhotos, allLinks = basTVParser()

            for (p,n,d,l) in zip(allPhotos, allNames, allDescription, allLinks):
                newsSendMessage(chat_id, p, n, d, l)
            menuSendMessage(chat_id)

        elif message == 'Последние новости FeedBack':
            allNames, allDescription, allPhotos, allLinks = feedBackParser()

            for (p,n,d,l) in zip(allPhotos, allNames, allDescription, allLinks):
                newsSendMessage(chat_id, p, n, d, l)
            menuSendMessage(chat_id)                

        elif message == 'Вернуться в меню' or message =='/start':
            keyBoardSendMessage(chat_id)
        else:
            sendMessage(chat_id, "Ну я понимаю только комманды, пока что ничего больше(((")

        return jsonify(r)
    return '<h1>Hello bot</h1>'
    

if __name__ == "__main__":
    app.run(threaded=True)

