import http.cookiejar
import urllib

import pyotp
import requests
import mechanize

import creds


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
    })
    assert response.status_code == 200, (response.status_code, response.text)
    assert len(response.json()['data']) == 1
    print('Token is OK')


# An app token is useless to consult the ads library
def try_app_token():
    response = requests.get(
        "https://graph.facebook.com/v3.3/oauth/access_token",
        params={
            'client_id': creds.APP_ID,
            'client_secret': creds.APP_SECRET,
            'grant_type': 'client_credentials',
        },
    )
    assert response.status_code == 200, (response.status_code, response.text)
    app_token = response.json()['access_token']

    inspect_token(app_token)

    test_token(app_token)


def get_user_token():
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
    browser.open(url)
    browser.select_form(nr=0)
    browser.form['email'] = creds.FB_USER
    browser.form['pass'] = creds.FB_PASSWORD
    browser.submit()

    # 2FA
    totp = pyotp.TOTP(creds.TOTP_SECRET)
    browser.select_form(nr=0)
    browser.form['approvals_code'] = totp.now()
    browser.submit()

    # Do not remember browser
    browser.select_form(nr=0)
    browser.form['name_action_selected'] = ['dont_save']
    response = browser.submit()

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
        'client_id': creds.APP_ID,
        # Make sure to define this url in facebook app's parameters (product login/parameters)
        # This callback does not have to be implemented, because the redirection is caught
        'redirect_uri': 'https://desinfo.quaidorsay.fr/api/ads/1.0/callback',
        'state': 'mystate',
        'response_type': 'token',
    })
    url = 'https://www.facebook.com/v3.3/dialog/oauth?' + params

    try:
        response = browser.open(url)
    except urllib.error.HTTPError as response:
        redirect_location = response.headers['Location']

    fragment = urllib.parse.urlparse(redirect_location).fragment
    user_access_token = urllib.parse.parse_qs(fragment)['access_token']

    return user_access_token
