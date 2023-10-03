from bs4 import BeautifulSoup
import urllib.request
from fake_useragent import UserAgent
def visit(link, parser):
    try:
        ua = UserAgent()
        hdr = {'User-Agent': ua.random,
       'Connection': 'keep-alive'}
        req = urllib.request.Request(link, None, hdr)
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res, parser)
            return soup
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("Access to the resource is forbidden")
            print(e)
        else:
            print(f"HTTP error: {e.code}")
        return None
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}")
        return None
    
    