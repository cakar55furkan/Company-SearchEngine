from elasticsearch import Elasticsearch
es =  Elasticsearch("http://localhost:9200", \
                    http_auth=("elastic", "0dv5W=eRTUVeHZwc3PHt"), \
                        verify_certs=False)

def insert_document_to_index(index, doc, id):
    if es.exists(index=index, id=id):
        return
    try:
        es.index(index=index, document=doc, id=id)
    except Exception as e:
        print(e)

def mongo_to_es_object(doc): # remove _id field from dictionary
    keys = doc.keys()
    new_doc = {}
    for key in keys:
        if key != "_id":
            new_doc[key] = doc[key]

    return new_doc

def is_doc_exist(index, id):
    if es.exists(index=index, id=id):
        return True
    return False

def is_index_exist(index):
    return es.indices.exists(index=index)


def update_doc(index, id, doc):
    try:
        es.update(index=index, id=id, doc=doc)
    except Exception as e:
        print(e)