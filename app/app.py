from flask import Flask, render_template, request
from tableau_client import sign_in, create_user, update_user, delete_user, get_user
import tableau_server_config, tableau_server_config

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/userTransfer", methods = ['GET', 'POST'])
def userTransfer():
    if request.method == 'POST':
        request_data = request.get_json()
        user = request_data['data']['events'][0]['target'][0]
        print(f'received userTransfer request: {user}')

        token, site_id, user_id = sign_in(tableau_server_config.SERVER_NAME,tableau_server_config.PERSONAL_ACCESS_TOKEN_NAME, tableau_server_config.PERSONAL_ACCESS_TOKEN_SECRET)
        print(f'signed into {site_id} as {user_id} with token {token}')

        to_add_user_info = {
            'name': user['alternateId'],
            'siteRole': 'Publisher'
        }

        created_user_id = create_user(tableau_server_config.SERVER_NAME, token, site_id, to_add_user_info)
        print(f'created user {created_user_id}')

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

        is_updated = update_user(tableau_server_config.SERVER_NAME, token, site_id, created_user_id, to_update_user_info)
        print(f'user {created_user_id} is updated? {is_updated}')

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
        print(f'received userRemove request: {request_data}')
        print(f' for user: {user}')

        to_remove_user_info = {
            'user': {
                'email': user['alternateId']
            }
        }

        token, site_id, user_id = sign_in(tableau_server_config.SERVER_NAME,tableau_server_config.PERSONAL_ACCESS_TOKEN_NAME, tableau_server_config.PERSONAL_ACCESS_TOKEN_SECRET)
        print(f'signed into {site_id} as {user_id} with token {token}')


        to_remove_user_id = get_user(tableau_server_config.SERVER_NAME, token, site_id, to_remove_user_info)

        is_user_deleted = delete_user(tableau_server_config.SERVER_NAME, token, site_id, to_remove_user_id)
        print(f'Deleted user {user_id}? {is_user_deleted}')

        return user
    else:
        verificationValue = request.headers['x-okta-verification-challenge']
        returnValue = {
            'verification' : verificationValue
        }

        return returnValue