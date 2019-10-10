import requests
import random
import threading
from bs4 import BeautifulSoup as bs
from time import sleep
token = '811976009:AAHhccp6wVYT66Y_SEUwakWz8D-nbUJ_L_8'
URL = 'https://api.telegram.org/bot'+token +'/'

global offset
offset = 0
global last_ipdate_id
last_ipdate_id = 0
global current_update_id
current_update_id = 0
global msgs
msgs = 0

pages = 0
reqs = []#запросы трубы для поиска. Например 864*1
results = []

headers = {'accept':'*/*',
           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}




def info_truba(headers, reqs, pages):
    for i in range(0,pages):
        session = requests.Session()
        request = session.get(f'http://trubamet.ru/?p=doska&act=show&pos=1&razdId={i}', headers=headers)
        if request.status_code==200:
            soup = bs(request.content, 'html.parser')
            divs = soup.find_all('td',attrs={'colspan':'2','class':'msgText'})
            for div in divs:
                title = div.text
                for req in reqs:
                    find = title.find(req)
                    if find>=0:
                        print(title)
                        results.append(title)

        else:
            print('Error')

def send_results(results, chat_id):
    cleared_results = list(set(results))
    if len(cleared_results)<=0:
        send_message(chat_id, 'Увы, найти ничего не удалось.')
    for i in range(len(cleared_results)):
        send_message(chat_id, cleared_results[i])


def get_updates():
    url = URL+f'getupdates?offset={last_ipdate_id}'
    r =requests.get(url)
    return r.json()

def get_message():
    data = get_updates()
    last_object = data['result'][-1]
    msgs = last_object['message']['message_id']

    current_update_id = last_object['update_id']
    global last_ipdate_id
    if  last_ipdate_id != current_update_id:
        last_ipdate_id = current_update_id

        chat_id = last_object['message']['chat']['id']
        message_text = last_object['message']['text']
        print(message_text)
        message = {'chat_id': chat_id,
                   'text': message_text}
        return message
    return None
def send_message(chat_id, text='Здравствуйте. Возможно, бот на данный момент выключен, напишите позже!'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id,text)
    requests.get(url)


def main():

    global enabled
    enabled = False

    global done
    done = False


    while True:
        answer = get_message()
        if answer != None:

            chat_id = answer['chat_id']
            print(chat_id)
            text = answer['text']

            if '/очистить' in text:
                reqs.clear()
                send_message(chat_id, 'Очистил список труб для поиска!')

            if '/трубы' in text:
                send_message(chat_id, f'Список труб для поиска: {reqs}')

            if text[0]=='!':
                    send_message(chat_id, 'Добавил трубу в список для поиска!')
                    reqs.append(text[1:len(text)])

            if text[0]=='?':
                    send_message(chat_id, 'Количество страниц для поиска записано!')
                    pages = int(text[1:len(text)])

            if '/старт' in text:
                    results.clear()
                    send_message(chat_id, 'Начинаю искать трубы...')
                    info_truba(headers, reqs, pages)
                    send_message(chat_id, 'Отправляю результаты...')
                    send_results(results, chat_id)

        else:
            continue
        sleep(0.3)

if __name__ == '__main__':
    main()