from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.crawl
rel_col = db.relevant

def get_parent(doc):
    try:
        q = {"url" : doc['parent']}
        return rel_col.find_one(q)
    except:
        return None
    
