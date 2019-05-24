
## Serve FB user token

```
tmux new -s fbtoken
tmux attach-session -t fbtoken
git clone https://github.com/ambanum/political-ads-scraper.git
pew new desinfo
pip install uwsgi flask pyotp requests mechanize
python serve_token.py
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

`credentials.py`:
```
APP_ID = 'xxx'
APP_SECRET = 'xxx'

FB_USER = 'xxx'
FB_PASSWORD = 'xxx'
TOTP_SECRET = 'xxx'

SHARED_SECRET = 'xxx'
```
