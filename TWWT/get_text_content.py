from bs4 import BeautifulSoup
import urllib.request

def visit(link):
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Connection': 'keep-alive'}
        req = urllib.request.Request(link, None, hdr)
        with urllib.request.urlopen(req, timeout=10) as res:
            info = res.info()
            if info.get_content_type() != 'text/html':
                return None
            soup = BeautifulSoup(res, "html.parser")
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
    except Exception as e:
        return None
    
    