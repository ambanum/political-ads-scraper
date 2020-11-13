The goal of this work is to improve access to information about political advertisement on digital platforms (Facebook, Google, Twitter, Snapchat).

## Install

The install instructions are for ubuntu.

### Create a virtualenv

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
path/to/venv/python -c "from facebook_fetch import fetch; fetch.create_dirs()
```

### Schedule jobs

Schedule daily jobs (using cron for example) to fetch the new archives.

To send alert by email, you could install moreutils and msmtp and copy this to `/etc/crontab`:

```
22 14  * * *   cloud  /path/to/python /path/to/political-ads-scraper/facebook_fetch/reports.py 2>&1 | /usr/bin/ifne msmtp root
22 17  * * *   cloud  /path/to/python /path/to/political-ads-scraper/facebook_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root
22 16  * * *   cloud  /path/to/python /path/to/political-ads-scraper/facebook_fetch/graph.py 2>&1 | /usr/bin/ifne msmtp root

30 14  * * *   cloud  /path/to/python /path/to/political-ads-scraper/twitter_fetch/fetch.py >> /var/log/twitter_fetch/`date "+\%Y-\%m-\%d-\%H-\%M-\%S"`.log 2>&1
38 21  * * *   cloud  /path/to/python /path/to/political-ads-scraper/twitter_fetch/graph.py 2>&1 | /usr/bin/ifne msmtp root

18 14  * * *   cloud  /path/to/python /path/to/political-ads-scraper/google_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root

45 13  * * *   cloud  /path/to/python /path/to/political-ads-scraper/snapchat_fetch/fetch.py 2>&1 | /usr/bin/ifne msmtp root

```