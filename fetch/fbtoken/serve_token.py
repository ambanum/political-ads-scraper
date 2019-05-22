from flask import Flask, request

from get_token import get_user_token
import credentials

application = Flask(__name__)

@application.route('/')
def hello():
    shared_secret = request.args.get('shared_secret')
    if shared_secret != credentials.SHARED_SECRET:
        return 'Incorrect shared secret. Send the shared secret as url parameter shared_secret', 401

    token = get_user_token()
    return token

if __name__ == '__main__':
   application.run()
