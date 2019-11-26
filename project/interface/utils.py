import urllib

def check_connection():
    try:
        urllib.request.urlopen('http://google.com', timeout=1)
    except urllib.error.URLError as err:
        return False
    
    return True
