
import http.cookiejar
import urllib

import pyotp
import requests
import mechanize

from facebook_fetch import config


def inspect_token(token):
    response = requests.get(
        "https://graph.facebook.com/v3.3/debug_token",
        params={
            'input_token': token,
            'access_token': token,
        },
    )
    assert response.status_code == 200, (response.status_code, response.text)
    print(response.text)


def test_token(token):
    response = requests.get(
        "https://graph.facebook.com/v3.3/ads_archive",
        params={
            'search_terms': "''",
            'fields': 'ad_snapshot_url',
            'ad_reached_countries': "['FR']",
            'limit': 1,
            'access_token': token,
        }
    )
    assert response.status_code == 200, (response.status_code, response.text)
    assert len(response.json()['data']) == 1
    print('Token is OK')


# An app token is useless to consult the ads library
def try_app_token():
    response = requests.get(
        "https://graph.facebook.com/v3.3/oauth/access_token",
        params={
            'client_id': config.APP_ID,
            'client_secret': config.APP_SECRET,
            'grant_type': 'client_credentials',
        },
    )
    assert response.status_code == 200, (response.status_code, response.text)
    app_token = response.json()['access_token']

    inspect_token(app_token)

    test_token(app_token)


def connect_facebook(user, password, totp_secret):
    # Setup browser
    browser = mechanize.Browser()
    cookies = http.cookiejar.LWPCookieJar()
    browser.set_cookiejar(cookies)
    browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36')]
    browser.set_handle_equiv(True)
    browser.set_handle_gzip(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)
    browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Login page
    url = 'https://m.facebook.com/login.php'
    response1 = browser.open(url)
    with open('response1.html', 'wb') as f:
        f.write(response1.read())

    browser.select_form(nr=0)
    browser.form['email'] = user
    browser.form['pass'] = password
    response2 = browser.submit()
    with open('response2.html', 'wb') as f:
        f.write(response2.read())

    # Novembre 2020: need to make another try
    # maybe change text_regex to "Log In" if language is English
    response3 = browser.follow_link(text_regex=r"Connexion", nr=0)
    with open('response3.html', 'wb') as f:
        f.write(response3.read())

    browser.select_form(nr=0)
    browser.form['email'] = user
    browser.form['pass'] = password
    response4 = browser.submit()
    with open('response4.html', 'wb') as f:
        f.write(response4.read())

    # 2FA
    totp = pyotp.TOTP(totp_secret)
    browser.select_form(nr=0)
    browser.form['approvals_code'] = totp.now()
    response5 = browser.submit()
    with open('response5.html', 'wb') as f:
        f.write(response5.read())

    # Do not remember browser
    browser.select_form(nr=0)
    browser.form['name_action_selected'] = ['dont_save']
    response6 = browser.submit()
    with open('response6.html', 'wb') as f:
        f.write(response6.read())

    return browser


def get_user_token(browser, app_id):
    #print(response.read())
    #print(cookies)

    #import sys, logging
    #logger = logging.getLogger("mechanize")
    #logger.addHandler(logging.StreamHandler(sys.stdout))
    #logger.setLevel(logging.DEBUG)
    #browser.set_debug_http(True)
    #browser.set_debug_responses(True)
    #browser.set_debug_redirects(True)

    browser.set_handle_redirect(False)
    params = urllib.parse.urlencode({
        'client_id': app_id,
        # Make sure to define this url in facebook app's parameters (product login/parameters)
        # This callback does not have to be implemented, because the redirection is caught
        'redirect_uri': 'https://disinfo.quaidorsay.fr/api/ads/1.0/callback',
        'state': 'mystate',
        'response_type': 'token',
    })
    url = 'https://www.facebook.com/v3.3/dialog/oauth?' + params

    try:
        browser.open(url)
    except urllib.error.HTTPError as response:
        redirect_location = response.headers['Location']

    # NB: API Graph access can be deactivated if the app is not used for some time.

    fragment = urllib.parse.urlparse(redirect_location).fragment
    user_access_token = urllib.parse.parse_qs(fragment)['access_token'][0]

    return user_access_token

def connect_and_get_user_token(user, app_id, password, totp_secret):
    browser = connect_facebook(user=user, password=password, totp_secret=totp_secret)
    user_access_token = get_user_token(browser=browser, app_id=app_id)
    return user_access_token, browser
