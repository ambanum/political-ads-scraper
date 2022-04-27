The goal of this work is to improve access to information about political advertisement on digital platforms (Facebook, Google, Twitter, Snapchat).

## Install

The install instructions are for ubuntu.

### Create a virtualenv

#### Using pew
For example, install `pew`:

```
sudo apt update
sudo apt install python3-pip
pip3 install pew
pew new political-ads-scraper
```

Note the path to the newly created python integreter:

```
which python
```
#### Using virtualenv

```
pip3 install virtualenv
virtualenv -p python3 political-ads-scraper
source political-ads-scraper/bin/activate
```

### Install the package

```
git clone https://github.com/ambanum/political-ads-scraper.git
cd political-ads-scraper
pip install --editable .
```

### Configure the package

Add the files `facebook_fetch/config.py`, `google_fetch/config.py`, `snapchat_fetch/config.py`, `twitter_fetch/config.py`.

Then create the data directory and its subdirectories `facebook`, `google`, `twitter` and `snapchat`. Create the subdirectories specific to facebook using:

```
path/to/venv/python -c "from facebook_fetch import fetch; fetch.create_dirs()"
```

### Configure access to facebook API

For this, you need to have a valid Facebook account
#### Review your ID

This is step 1 from https://www.facebook.com/ads/library/api and it will make you think you're tracked, but that's fine.

> Go to Facebook.com/ID. This is the same ID confirmation required to become authorized to run ads about social issues, elections or politics. If you haven't already confirmed your ID, it typically takes 1-2 days to complete this step.

From there, you need to enable the 2FA authentication first.

**IMPORTANT**: Note the code at the right of the QR Code "XXXX XXXX XXXX XXXX XXXX XXXX XXXX XXXX" as you will need to add it to the config later on as `TOTP_SECRET`

Then, you need to wait 48 hours before validation
#### Create a facebook developer account

See Doc on Facebook website

1. Register
2. Verify your account by SMS
3. Confirm email
4. About You

#### Retrieve token

- Create or login to a [Facebook Developer Account](https://developer.facebook.com)
- Once your account is validated [Create app](https://developers.facebook.com/apps/)
- Select an app type by choosing "none"
- Pick a name like "Political Ads Scraper"
- Then get an access token https://blog.coupler.io/facebook-ads-api/
- save it to put it in `facebook_fetch/config.py` as `FB_TOKEN_SERVICE_SECRET`

#### Add other environment variables

your `facebook_fetch/config.yml` should look like this

```python
FB_TOKEN_SERVICE_URL = ' http://127.0.0.1:5000'
FB_TOKEN_SERVICE_SECRET = 'XXXXX'
FB_USER = 'facebook email'
FB_PASSWORD = 'facebook password'
APP_ID = 'XXXXXXXXXXXXXX'
TOTP_SECRET = 'XXXXXXXXXXXXXXX' # Remove all white spaces

import pathlib
DATA_DIR = pathlib.Path("./data/political-ads-scraper")
```

#### Launch server

##### on local 

```sh
pip install markupsafe==2.0.1 # only this version works
python facebook_fetch/fb_login/serve_token.py
```


### Schedule jobs

Schedule daily jobs (using cron for example) to fetch the new archives.

To send alert by email, you could install moreutils and msmtp and copy this to `/etc/crontab`:

```
22 14  * * *   cloud  python ./facebook_fetch/reports.py 2>&1 | /usr/bin/ifne msmtp root
22 16  * * *   cloud  python ./facebook_fetch/graph.py 2>&1 | /usr/bin/ifne msmtp root
22 17  * * *   cloud  python ./facebook_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root

30 14  * * *   cloud  python ./twitter_fetch/fetch.py >> /var/log/twitter_fetch/`date "+\%Y-\%m-\%d-\%H-\%M-\%S"`.log 2>&1
38 21  * * *   cloud  python ./twitter_fetch/graph.py 2>&1 | /usr/bin/ifne msmtp root

18 14  * * *   cloud  python ./google_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root

45 13  * * *   cloud  python ./snapchat_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root

```

## Troubleshoot

### Cython-generated file '{src}' not found

NOT WORKING
https://fixexception.com/pandas/cython-generated-file-src-not-found-cython-is-required-to-compile-pandas-from-a-development-branch-please-install-cython-or-download-a-release-package-of-pandas/



