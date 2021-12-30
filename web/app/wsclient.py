import json
from app.settings import WS_URL
from websocket import create_connection

def send_signin_fail(payload):
    '''This method is used to send data through websocket if user sign in failed'''
    try:
        send_data = {
            'acct': payload.get('acct'),
            'pwd': payload.get('pwd'),
            'is_web': True
        }
        ws = create_connection(WS_URL, timeout=1)
        ws.send(json.dumps(send_data))
        ws.close()
    except Exception as e:
        pass