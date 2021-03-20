
from flask_socketio import *
from flask_cors import CORS
from flask import Flask, render_template, request, jsonify
from tableau_client import sign_in, create_user, update_user, delete_user, get_user, get_users
import tableau_server_config, tableau_server_config

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('UserAdded')
def userAdded(message):
    print('User Added')
    emit('userAddedResponse', {'data': message}, broadcast=True)    

@app.route("/users")
def users():

    token, site_id, user_id = sign_in(tableau_server_config.SERVER_NAME,tableau_server_config.PERSONAL_ACCESS_TOKEN_NAME, tableau_server_config.PERSONAL_ACCESS_TOKEN_SECRET)
    print(f'signed into {site_id} as {user_id} with token {token}')


    users = get_users(tableau_server_config.SERVER_NAME, token, site_id)
    print(users)

    return jsonify(users)

@app.route("/userTransfer", methods = ['GET', 'POST'])
def userTransfer():
    if request.method == 'POST':
        request_data = request.get_json()
        user = request_data['data']['events'][0]['target'][0]
        print(f'Transferring user: {user}')

        token, site_id, user_id = sign_in(tableau_server_config.SERVER_NAME,tableau_server_config.PERSONAL_ACCESS_TOKEN_NAME, tableau_server_config.PERSONAL_ACCESS_TOKEN_SECRET)
        print(f'signed into site_id: {site_id} as user_id: {user_id} with token: {token}')

        to_add_user_info = {
            'name': user['alternateId'],
            'siteRole': 'Publisher'
        }

        created_user_id = create_user(tableau_server_config.SERVER_NAME, token, site_id, to_add_user_info)
        print(f'created user with user_id: {created_user_id}')

        to_update_user_info = {
            "user": {
                "fullName": user['displayName'],
                "email": user['alternateId'],
                "password": tableau_server_config.DEFAULT_USER_PASSWORD,
                "siteRole": "Publisher",
                "authSetting": "ServerDefault"
            }
        }    

        print(to_update_user_info)

        updated_user_info = update_user(tableau_server_config.SERVER_NAME, token, site_id, created_user_id, to_update_user_info)
        print(f'user with user_id: {created_user_id} is updated with: {updated_user_info}')
        created_user = {
            'id': created_user_id,
            'lastLogin': '',
            'name': user['displayName'],
        }

        payload = {'data': {'user': created_user}}
        socketio.emit('userAddedResponse', payload, broadcast=True)

        return user
    else:
        verificationValue = request.headers['x-okta-verification-challenge']
        returnValue = {
            'verification' : verificationValue
        }

        return returnValue

@app.route("/userRemove", methods = ['GET', 'POST'])
def userRemove():
    if request.method == 'POST':
        request_data = request.get_json()
        user = request_data['data']['events'][0]['target'][0]
        print(f'Removing user: {user}')

        to_remove_user_info = {
            'user': {
                'email': user['alternateId']
            }
        }

        token, site_id, user_id = sign_in(tableau_server_config.SERVER_NAME,tableau_server_config.PERSONAL_ACCESS_TOKEN_NAME, tableau_server_config.PERSONAL_ACCESS_TOKEN_SECRET)
        print(f'signed into site_id: {site_id} as user_id: {user_id} with token: {token}')


        to_remove_user_id = get_user(tableau_server_config.SERVER_NAME, token, site_id, to_remove_user_info)

        is_user_deleted = delete_user(tableau_server_config.SERVER_NAME, token, site_id, to_remove_user_id)
        print(f'Deleted user with user_id: {user_id}? {is_user_deleted}')

        removed_user = {
            'id': to_remove_user_id,
        }

        payload = {'data': {'user': removed_user}}
        socketio.emit('userRemovedResponse', payload, broadcast=True)     

        return user
    else:
        verificationValue = request.headers['x-okta-verification-challenge']
        returnValue = {
            'verification' : verificationValue
        }

        return returnValue

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, ssl_context=('fullchain.pem', 'privkey.pem'))