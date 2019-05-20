#!/bin/bash
set -e

### Configuration ###

SERVER=cloud@disinfo.quaidorsay.fr
APP_DIR=/home/cloud/political-ads-scraper
REMOTE_SCRIPT_PATH=/tmp/deploy-political-ads-scraper.sh


### Library ###

function run()
{
  echo "Running: $@"
  "$@"
}


### Automation steps ###

run scp $KEYARG deploy/work.sh $SERVER:$REMOTE_SCRIPT_PATH
echo
echo "---- Running deployment script on remote server ----"
run ssh $SERVER bash $REMOTE_SCRIPT_PATH

echo "Fine! Now you should update the data by running scp or rsync: 'scp -r data cloud@desinfo.quaidorsay.fr:/home/cloud/political-ads-scraper' or 'rsync -rltzvh data/ cloud@desinfo.quaidorsay.fr:~/political-ads-scraper/data'"
