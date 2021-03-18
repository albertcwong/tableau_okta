
from tableau_server_config import API_VERSION, PERSONAL_ACCESS_TOKEN_NAME, PERSONAL_ACCESS_TOKEN_SECRET
import requests, json

def sign_in(server, pat_name, pat_secret, site=''):
    url = f'{server}/api/{API_VERSION}/auth/signin'

    payload = {
        'credentials': {
            'personalAccessTokenName': pat_name,
            'personalAccessTokenSecret': pat_secret,
            'site': {
                'contentUrl': site,
            },
        },
    }

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    req = requests.post(url, json=payload, headers=headers, verify=False)
    req.raise_for_status()

    response = json.loads(req.content)
    token = response['credentials']['token']
    site_id = response['credentials']['site']['id']
    user_id = response['credentials']['user']['id']

    return token, site_id, user_id

def create_user(server, auth, site_id, user_info):
    url = f'{server}/api/{API_VERSION}/sites/{site_id}/users?overwrite=true'

    user_name = user_info.get('name', None)
    site_role = user_info.get('siteRole', 'Publisher')

    if user_name is None:
        return None

    payload = {
        'user': {
            'name': user_name,
            'siteRole': site_role,
        }
    }

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'X-Tableau-Auth': auth,
    }

    req = requests.post(url, json=payload, headers=headers, verify=False)
    req.raise_for_status()

    response = json.loads(req.content)
    user_id = response['user']['id']

    return user_id

def update_user(server, auth, site_id, user_id, user_info):
    url = f'{server}/api/{API_VERSION}/sites/{site_id}/users/{user_id}'
    
    user_full_name = user_info['user'].get('fullName', '')
    user_email = user_info['user'].get('email', '')
    user_password = user_info['user'].get('password', '')
    user_site_role = user_info['user'].get('siteRole', 'Publisher')
    user_auth_setting = user_info['user'].get('authSetting', 'ServerDefault')

    payload = {
        'user': {
            'fullName': user_full_name,
            'email': user_email,
            'password': user_password,
            'siteRole': user_site_role,
            'authSetting': user_auth_setting,
        }
    }

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'X-Tableau-Auth': auth,
    }

    req = requests.put(url, json=payload, headers=headers, verify=False)
    req.raise_for_status()

    response = json.loads(req.content)
    user_id = response['user']['id']    

    return True

def get_user(server, auth, site_id, user_info):
    url = f'{server}/api/{API_VERSION}/sites/{site_id}/users'
    
    # user_full_name = user_info['user'].get('fullName', '')
    user_email = user_info['user'].get('email', '')

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'X-Tableau-Auth': auth,
    }

    if user_email != '':
        url = f'{url}?filter=name:eq:{user_email}'

    req = requests.get(url, headers=headers, verify=False)
    req.raise_for_status()
    response = json.loads(req.content)
    user_id = response['users']['user'][0]['id']

    return user_id

def delete_user(server, auth, site_id, user_id):
    url = f'{server}/api/{API_VERSION}/sites/{site_id}/users/{user_id}'

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'X-Tableau-Auth': auth,
    }

    req = requests.delete(url, headers=headers, verify=False)
    req.raise_for_status()

    return True    

if __name__ == '__main__':
    server = 'https://elsa408.asuscomm.com'

    token, site_id, user_id = sign_in(server,PERSONAL_ACCESS_TOKEN_NAME, PERSONAL_ACCESS_TOKEN_SECRET)
    print(f'signed into {site_id} as {user_id} with token {token}')

    to_add_user_info = {
        'name': 'albwong@netflix.com',
        'siteRole': 'Publisher'
    }

    created_user_id = create_user(server, token, site_id, to_add_user_info)
    print(f'created user {created_user_id}')

    to_update_user_info = {
        "user": {
            "fullName": "albert wong",
            "email": "albwong@netflix.com",
            "password": "tester123",
            "siteRole": "Publisher",
            "authSetting": "ServerDefault"
        }
    }    

    print(to_update_user_info)

    is_updated = update_user(server, token, site_id, created_user_id, to_update_user_info)
    print(f'user {created_user_id} is updated? {is_updated}')
