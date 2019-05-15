#!/bin/bash
set -e

### Configuration ###

REPO_DIR=/home/cloud/political-ads-scraper
APP_DIR=/home/cloud/political-ads-scraper/srv
GIT_URL=git@github.com:ambanum/political-ads-scraper.git

### Automation steps ###

set -x

eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_rsa_deploy_key
# Pull latest code
if [[ -e $REPO_DIR ]]; then
  cd $REPO_DIR
  git pull
else
  git clone $GIT_URL $REPO_DIR
fi

# Install dependencies
cd $APP_DIR
npm install --production
npm prune --production

# Restart app
forever restart bin/www || forever start bin/www
