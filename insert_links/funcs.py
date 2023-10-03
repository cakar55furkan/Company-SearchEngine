from loc_regex import is_valid_url
from tldextract import extract
import datetime
import re
from link_score.link_score import calculate_link_score
import es
from link_score.get_parent import get_parent
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.crawl
rel_col = db.relevant

def get_document_by_url(url):
    try:
        q = {"url" : url}
        return rel_col.find_one(q)
    except:
        return None


def insert_page_urls(soup, level, source_url, collection, is_relevant, twwt, depth): #find all links in a webpage and insert it to db.

    for link in soup.find_all('a', href=True):
        try:
            clean_link = link['href']

            if len(clean_link) < 1:
                continue
            
            if clean_link[0] == "/":
                # relative url
                prefix, current_domain, suffix = extract(source_url)
                clean_link = "https://" + prefix + "."+ current_domain +"."+ suffix + clean_link

            if "http" not in clean_link:
                continue

            if clean_link[-1] == "/":
                clean_link = clean_link[0:-1]
            
            # check with regex
            pattern = r'https?://\S+'
            urls = re.findall(pattern, clean_link)
            
            if len(urls) == 0: # it is not a http url
                continue
            if "#" in clean_link:
                clean_link = clean_link.split("#")[0]

            doc_list = list(collection.find({"url" : clean_link}))
            if len(doc_list) == 1:
                """
                    If link is already present in frontier.
                    Update the count
                    Update the Anchor
                """
                current_record = doc_list[0]

                if current_record['visited']: 
                    # if the url is visited, no need to update the count or anchor.
                    continue

                anchor_arr = list(current_record['anchor'])
                anchor_arr.append(str(link.string).strip())
                
                filter = { 'url': current_record['url'] }
                updated_values = { "$set": { 
                        'count': current_record['count'] + (1 if is_relevant else 0),
                        'anchor' : list(set(anchor_arr)),
                        "depth" : min(doc_list[0]['depth'], depth),
                        # if link is skipped even after following irrelevant pages, and re discovered by
                        # relevant page, level is updated to visit in the future.
                        # "level" : current_record['level'] if current_record['count'] > 0 else level 
                    }}
                collection.update_one(filter, updated_values)
                
            else:
                """
                    Insert the newly discovered link.
                """
                anchor_arr = []
                anchor_arr.append(link.string)
                new_frontier_element = {
                    "date" : datetime.datetime.now(),
                    "anchor" : anchor_arr,
                    "url" : clean_link,
                    "level" : level,
                    "visited" : False,
                    "count" : 1 if is_relevant else 0,
                    "parent" : source_url,
                    "depth" : depth
                }
                new_frontier_element['link_score'] = calculate_link_score(new_frontier_element, twwt)
                collection.insert_one(new_frontier_element)
        except Exception as e:
            print(e, link)