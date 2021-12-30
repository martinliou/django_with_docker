from websocket_server import WebsocketServer  
import json
client_dict = dict()

# Called when client connected
def new_client(client, server):
    try:
        client_dict[client['id']] = {'client_obj': client}
    except Exception as e:
        pass

# Called when client is disconected                                       
def client_left(client, server):
    try:
        del client_dict[client['id']]
    except:
        pass

# Called when a client sends a message                                          
def message_received(client, server, message):
    try:
        msg_dict = json.loads(message)
        client_dict[client['id']]['is_web'] = msg_dict.get('is_web')

        for k, v in client_dict.items():
            # Ignore to send data to web server itself
            if v.get('is_web'):
                continue

            msg = 'User {} failed to login with password {}'.format(
                msg_dict.get('acct'),
                msg_dict.get('pwd'),
            )

            server.send_message(v.get('client_obj'), json.dumps({'msg': msg}))
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    server = WebsocketServer('0.0.0.0', 5566)
    server.set_fn_new_client(new_client)                                            
    server.set_fn_client_left(client_left)                                          
    server.set_fn_message_received(message_received)                                
    server.run_forever()