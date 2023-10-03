from visit import visit
import pymongo
import json
import datetime
from insert_links.funcs import insert_page_urls
from urllib.parse import urlparse
from tldextract import extract
from lemmatization import lemmetization
from external_links import detect_links
import NER
from relevancy_calculation.relevancy import calculate_relevancy
from link_score.get_links_from_frontier import get_ordered_links
from tf_idf.apply_tf_idf import calculate_tf_idf
import random

file = open('config.json')
config = json.load(file)
# twwt.create_twwt(config['twwt']['query'], stop=config['twwt']['stop'])

seeds = config['seeds']
focused_mode = config['focused_mode']

client = pymongo.MongoClient('mongodb://localhost:27017/')
# client.drop_database('crawl')
db = client['crawl']
seed_collection = db['seed']
seed_collection.create_index('url', unique=True)

frontier = db['frontier']
frontier.create_index([('url', pymongo.TEXT)])
frontier.create_index('url', unique=True)


relevant_collection = db['relevant']
relevant_collection.create_index('url', unique=True)

irrelevant_collection = db['irrelevant']
irrelevant_collection.create_index('url', unique=True)


# move it to another file. for better looking
for seed in seeds: # insert seeds to seed and to_visit collections.
    dict = {
        "date" : datetime.datetime.now(),
        "url" : seed,
        "level" : 0,
        "visited" : False,
        "parent" : None,
        "count" : 1
        }
    seed_dict = {
        "url" : seed
    }

    try:

        seed_collection.insert_one(seed_dict)
        frontier.insert_one(dict)
    except Exception as e:
        print(e)

level = 0
q = {"level" : level, "visited" : False}
docs = list(frontier.find(q))

db = client['twdb']
collection = db['twdb']
a = collection.find({}).sort('date', pymongo.DESCENDING)
tw = a[0]['table'] 

while True:
    try:
        doc = docs[0]
        
        print("Processing: ", doc['url'])

        url = urlparse(doc['url']).netloc
        _, dom, _ = extract(doc['url']) 

        soup = visit(doc['url'], "html.parser")
        doc['title'] = soup.title.string
        try:
            doc['description'] = soup.find("meta", property="og:description")['content']
        except Exception as e:
            pass
        doc['text'] = soup.get_text(separator=" ", strip=True) # get text context
        # doc['linked_domains'] = detect_linked_domains(soup, doc['url'], domains_collection) # count links to external domains
        doc['text_lemm'] = lemmetization.lemmetize_text(doc['text']) # uzun bir cikti veriyor
        doc['relevancy'] = calculate_relevancy(soup)
        doc['tf_idf_calculated'] = False
        doc['visited'] = True

        doc = NER.apply_NER(doc)
        filter = { 'url': doc['url'] }
        updated_values = { "$set": { 
                'visited' : True
        }}
        frontier.update_one(filter, updated_values)


        if doc['relevancy'] > 0.6:
            relevant_collection.insert_one(doc)
            if doc['count'] == 0:
                # irrelevant to relevant. Set depth to zero.
                print("[!] Reached relevant page from irrelevant parent. ", doc['url'])
                insert_page_urls(soup, doc['level'] + 1, doc['url'], frontier, True, tw, depth=0)
            else:
                # relevant to relevant
                print("[+] Relevant page linked from another relevant page. ", doc['url'])
                insert_page_urls(soup, doc['level'] + 1, doc['url'], frontier, True, tw, depth=0)
        
        else: # if document is not relevant
            if not focused_mode:
                # insert all the links
                relevant_collection.insert_one(doc)
                insert_page_urls(soup, doc['level'] + 1, doc['url'], frontier, True, tw, depth=0)
                calculate_tf_idf()
            else:
                if doc['count'] > 0:
                    # irrelevant page linked from a relevant page
                    print("[+] Irrelevant page linked from relavant page. ", doc['url'])
                    irrelevant_collection.insert_one(doc)
                    insert_page_urls(soup, doc['level'] + 1, doc['url'], frontier, False, tw, depth=1)
                else:
                    # irrelevant from an irrelevant parent.
                    if doc['depth'] > 2:
                        # Depth limit reached. No relevancy detected for 3 generation. Do not record this.
                        # This document is the last member of three irrelevant lineage.
                        # Since this prevents inserting links that linked from 3 generetaion irrelevant documents, 
                        # this documents children will not be present in the frontier collection.
                        print("[!] Reached depth limit. ", doc['url'])
                    else:
                        # if depth < 3 , visit the page and insert its links.
                        # print("[+] Irrelevant from irrelevant, depth not reached. ", doc['url'])
                        irrelevant_collection.insert_one(doc)
                        insert_page_urls(soup, doc['level'] + 1, doc['url'], frontier, False, tw, depth=doc['depth'] + 1)
        calculate_tf_idf()
        docs.remove(doc)
    except Exception as e:
        if docs:
            if len(docs) > 0:
                doc = docs[0]
                filter = { 'url': doc['url'] }
                updated_values = { "$set": { 
                        'visited' : True
                }}
                docs.remove(doc)
                frontier.update_one(filter, updated_values)
        print("[-] ", e)

    if not docs:
        level = level + 1
        max_level = frontier.find({}).sort("level",  -1)[0]['level']
        print(max_level)
        # level = max_level - 1
        docs = get_ordered_links(level, frontier, focused_mode)
        if not focused_mode:
            random.shuffle(docs)

        if not docs:
            if level >= max_level:
                print("[!] FINISH")
                exit()
            else:
                continue