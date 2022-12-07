# tableau_okta

## Purpose
A service to demonstrate how to leverage webhooks to synchronize Tableau user accounts with Okta employee directory.

Configure Tableau Server with CA
* sudo apt install certbot
* sudo certbot certonly --standalone
* configure via TSM UI
* tableau server now trusted by most browsers

Re-use CA certificates for SAML
* only requires small modification
* openssl rsa -in domain.key -out domain-rsa.key
* configure as usual via TSM UI
* tableau server can now communicate with okta on secure channel

Re-use CA certificates for Custom Server
* FLASK_APP=app/app.py flask run --host=0.0.0.0 --cert=fullchain.pem --key=privkey.pem

Service can now communicate with okta on secure channel
