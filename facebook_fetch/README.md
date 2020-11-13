
## Serve FB user token

Cheatsheet:

```
pew workon political-ads-scraper

tmux new -s fbtoken
tmux attach-session -t fbtoken

git clone https://github.com/ambanum/political-ads-scraper.git

# For local testing
python facebook_fetch/fb_login/serve_token.py

# On remote server
pip install uwsgi
cd facebook_fetch/fb_login
uwsgi --ini uwsgi.ini
```

`/etc/nginx/sites-available/fbtoken`:
```
server {
    listen 443 ssl;

    ssl_certificate /etc/letsencrypt/live/{servername}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{servername}/privkey.pem;

    server_name {servername};

    location /fbtoken {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/fbtoken.sock;
    }
}
```

`config.py`:
```
APP_ID = 'xxx'
APP_SECRET = 'xxx'
...
```
