"""Test dataset download URLs."""
import urllib.request

urls = [
    'https://archive.ics.uci.edu/static/public/470/parkinson+disease+classification.zip',
    'https://archive.ics.uci.edu/static/public/489/parkinson+dataset+with+replicated+acoustic+features.zip',
    'https://archive.ics.uci.edu/static/public/45/heart+disease.zip',
    'https://archive.ics.uci.edu/static/public/891/cdc+diabetes+health+indicators.zip',
    'https://raw.githubusercontent.com/fedesoriano/heart-failure-prediction/master/heart.csv',
    'https://raw.githubusercontent.com/johnsmith88/heart-disease-dataset/master/heart.csv',
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read()
        ctype = resp.headers.get('Content-Type', '?')
        print(f'OK {url[:80]}: {len(data)} bytes [{resp.status}] type={ctype}')
    except Exception as e:
        print(f'FAIL {url[:80]}: {str(e)[:100]}')
