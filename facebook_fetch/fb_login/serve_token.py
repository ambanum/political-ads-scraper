from flask import Flask, request

from facebook_fetch.fb_login.login import connect_and_get_user_token
from facebook_fetch import config

application = Flask(__name__)

@application.route('/')
def hello():
    shared_secret = request.args.get('shared_secret')
    if shared_secret != config.FB_TOKEN_SERVICE_SECRET:
        return 'Incorrect shared secret. Send the shared secret as url parameter shared_secret', 401

    token, _ = connect_and_get_user_token(user=config.FB_USER, app_id=config.APP_ID, password=config.FB_PASSWORD, totp_secret=config.TOTP_SECRET)
    return token

if __name__ == '__main__':
    application.run()
