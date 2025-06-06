import requests

bot_token = '8100528566:AAG1B8WC_BgD2yN3t7U8NFeuMJDvcLp4mak'
chat_id = '5834307479'
message = 'Hello from Python! 🧠'

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

payload = {
    'chat_id': chat_id,
    'text': message,
    'disable_notification': False
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print('Error sending message:', e)
