#!/bin/bash
set -e

### Configuration ###

APP_DIR=/home/cloud/political-ads-scraper
GIT_URL=git@github.com:ambanum/political_ads_scraper.git

### Automation steps ###

set -x

eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_rsa_deploy_key
# Pull latest code
if [[ -e $APP_DIR ]]; then
  cd $APP_DIR
  git pull
else
  git clone $GIT_URL $APP_DIR
  cd $APP_DIR
fi

# Install dependencies
npm install --production
npm prune --production

# Restart app
forever restart bin/www || forever start bin/www
