import configparser
import requests
import json
import datetime
import time
import os
import mimetypes

session = requests.Session()
config = configparser.ConfigParser()
config_path = ("path/to/config/file")
config.read(config_path)
RV_URL = config['rvision']['url']
RV_TOKEN = config['rvision']['token']
DOZOR_URL = config['dozor']['url']
DOZOR_IP = config['dozor']['ip']
DOZOR_USERNAME = config['dozor']['username']
DOZOR_PASS = config['dozor']['password']
EVENTS_DIR = config['path']['events_dir']
LOG_DIR = config['path']['log_dir']
LAST_ID_DIR = = config['path']['last_id_dir']
incident = {}

headers = {
    'Host' : f'{DOZOR_IP}',
    'Sec-Ch-Ua' : '"(Not(A:Brand";v="8", "Chromium";v="98"',
    'Content-Type' : 'application/json',
    'X-Requested-With' : 'XMLHttpRequest',
    'Accept-Language' : 'ru',
    'Sec-Ch-Ua-Mobile' : '?0',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Sec-Ch-Ua-Platform' : '"Windows"',
    'Accept' : '*/*',
    'Origin' : f'{DOZOR_URL}',
    'Sec-Fetch-Site' : 'same-origin',
    'Sec-Fetch-Mode' : 'cors',
    'Sec-Fetch-Dest' : 'empty',
    'Referer' : f'{DOZOR_URL}',
    'Accept-Encoding' : 'gzip, deflate',
    'Connection' : 'close',
}

def get_csrf_token():
    """ Получаем CSRF токен """
    url =  f"{DOZOR_URL}/"
    payload = {}
    response = session.get(url, verify = False,headers = headers, data=payload)
    return response.headers['Set-Cookie']

def login(csrf_token):
    """ Логинимся с использованием полученного токена """
    url =  f"{DOZOR_URL}/auth/login"
    headers.update({'Cookie':csrf_token})
    payload = {
                "login" : f"{DOZOR_USERNAME}",
                "password" : f"{DOZOR_PASS}"
                }
    response = session.post(url, verify = False, headers = headers, data=json.dumps(payload))
    return response.headers['Set-Cookie']

def get_events(csrf_token, session_token):
    """ Получение всех отмеченных событий """
    url =  f"{DOZOR_URL}/event/menu/events"
    headers.update({'Cookie': f"{csrf_token}; {session_token}"})
    payload = {"buildFacets":[],"query":{"sourcedest":{"direction":"bidirectional"},"orgUnits":[],"text":[""],"persons":[],"endpoints":[]},"facets":{"period":"total","text":""},"selected":{"path":["my-incidents","open"]},"orderBy":"date","dir":"DESC","from":0,"size":50}
    response = session.post(url, verify = False, headers = headers, data=json.dumps(payload))
    return json.loads(response.text)["events"]

def send_to_rvision(incident):
    """ Отправляем инцидент в R-Vision, возвращаем его идентификатор """
    url = f"{RV_URL}api/v2/incidents"
    session = requests.Session()
    response = session.post(url, json = incident, verify = False)
    return json.loads(response.text)["data"][0]["identifier"]

def get_added_inc_ids():
    """ Получаем список отработанных ицнидентов """
    id_list = []
    infile = open(str(LAST_ID_DIR) + "last_dozor_id.txt")
    infile = infile.read()
    id_list = infile.split('\n')
    return id_list

def write_last_inc_id(current_id):
    """ Добавляем инцидент в список отработанных """
    outfile = open(str(LAST_ID_DIR) + "log.txt")
    outfile.write(str(current_id) + '\n')

def check_inc_id(current_id):
    """ Проверяем нет ли инцидента в списке отработанных """
    id_list = get_added_inc_ids()
    if current_id not in id_list:
        return 1
    else:
        return 0

def log(msg):
    """ Логирование """
    print(msg)
    outfile = open(str(LOG_DIR) + "log.txt")
    outfile.write(str(datetime.datetime.now()) + " " + str(msg) + '\n')
    return 0

def check_files(attachments, event_id, message_id, incident_id):
    """ Проверяем наличие вложений, если они есть - то выкачиваем их в папку инцидента """
    if attachments != []:
        os.chdir(EVENTS_DIR)
        os.mkdir(f"{event_id}")
        for item in attachments:
            print(item['filename'])
            print(item['partId'])
            get_file_from_dozor(message_id, item['partId'], item['filename'], event_id, incident_id)
    return 0

def get_file_from_dozor(message_id, part_id, filename, event_id, incident_id):
    """ Скачиваем файл инцидента из Dozor """
    url =  f"{DOZOR_URL}/archiveserver/messages/" + str(message_id) + "/parts/" + str(part_id) +"/data"
    file = open(f"{event_id}\\{filename}", 'wb')
    path = f"{event_id}"
    response = session.get(url, verify = False, headers = headers)
    file.write(response.content)
    file.close()
    time.sleep(2)
    send_file_to_rvision(incident_id,filename,path)
    return 0

def send_file_to_rvision(incident_id,filename, path):
    """ Прикрепляем файл к инциденту в R-Vision """
    url = f"{RV_URL}api/v2/incidents"

    type = mimetypes.guess_type(filename)
    payload = {
                    'identifier': incident_id
            }
    files=[('files',("Обнаруженный документ: " + filename, open(path + '/' + filename,'rb'), str(type[0]) ))]
    headers = {
                'X-Token' : RV_TOKEN
                }
    response = requests.request("POST", url, headers=headers, verify = False, data=payload,files=files)
    return response.text

def events_processing(events):
    """ Обработка инцидентов """
    global incident

    for event in events:
        incident = {
            'token': RV_TOKEN,
            'company':'Test_Company',
            'category':'Test_Category',
            'INCIDENT_OWNER':'Test_user',
            'level':'Средний',
        }
        if check_inc_id(event['eventId']):
            incident['DETECTION_DATE'] = event['regDate']
            incident_id = send_to_rvision(incident)
            write_last_inc_id(event['eventId'])
            time.sleep(5)
            check_files(event['attachments'], event['eventId'], event['messageId'], incident_id)
    return 0

if __name__ == "__main__":

    try:
        csrf_token = get_csrf_token()
        session_token = login(csrf_token)
        events = get_events(csrf_token, session_token)
        events_processing(events)
    except Exception as err:
        log(err)
