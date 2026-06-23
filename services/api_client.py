
import time
import requests

HEADERS = {"User-Agent": "CryptoTradingOS/1.0"}

def get_json(url, retries=3, timeout=12, sleep=1):
    last_error = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_error = e
            time.sleep(sleep * (i + 1))
    return None

def get_text(url, retries=3, timeout=12, sleep=1):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception:
            time.sleep(sleep * (i + 1))
    return None

def to_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None
