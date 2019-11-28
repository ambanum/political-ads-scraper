The goal of this work is to improve access to information about political advertisement on digital platforms (Facebook, Google, Twitter, Snapchat).

## Install

The isntractions are for ubuntu.

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
