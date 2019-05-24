from flask import Flask, request

from fb_fetch.fb_login.login import connect_and_get_user_token
from fb_fetch import config

application = Flask(__name__)

@application.route('/')
def hello():
    shared_secret = request.args.get('shared_secret')
    if shared_secret != config.SHARED_SECRET:
        return 'Incorrect shared secret. Send the shared secret as url parameter shared_secret', 401

    token, _ = connect_and_get_user_token()
    return token

if __name__ == '__main__':
   application.run()
