def detect_links(soup):
    # relative links!!!!

    ls = []
    for link in soup.find_all('a', href=True):
        if link['href'][0] == "/":
            print("relative url")
            
        ls.append(link['href'])
    return list(set(ls))