import pymongo
import pika
import json
from elasticSearch import search_unvisited_index
con_param = pika.ConnectionParameters("localhost")
connection = pika.BlockingConnection(con_param)
channel = connection.channel()
channel.queue_declare(queue='letterbox')

def get_to_visit_links(to_visit_collection, level):
    global channel

   
   
    # check if level is not empty: continue else stop.
    # check if level and visited false not empty
    # else increase level

    while True:
        print("-------------")
        print("Level:\t", level)
        count_check = to_visit_collection.count_documents( # no documents at this level.
                {
                    'level': level
                }
            )
        if count_check == 0:
            return None
        total = count_check
        count_check = to_visit_collection.count_documents(
            {
                'level' : level,
                'visited' : False
            }
        )
        rem = count_check
        print("Progress:\t" + str(total - rem) + "/" + str(total))



        if count_check == 0: # all documents visited at this level. Increase level.
            level = level  + 1
            req_tf_idf = {
                'operation' : 'tf_idf',
                'level' : level - 1
                }
            channel.basic_publish(exchange='', routing_key='letterbox', body=json.dumps(req_tf_idf))
            continue

        else: # at this level, there are unvisited documents.
            print("-----------------------------------------HERE")
            req_tf_idf = {
                'operation' : 'tf_idf',
                'level' : level
                }
            channel.basic_publish(exchange='', routing_key='letterbox', body=json.dumps(req_tf_idf))

            docs = to_visit_collection.find({
                'level' : level,
                'visited' : False
            }).limit(10)
            return list(docs)




    # q_unvisited = {"visited": False, "level" : level}
    # docs = list(to_visit_collection.find(q_unvisited).sort([('date', pymongo.ASCENDING)]))
    # for doc in docs:
    #     _, domain, _ = extract(doc['url'])
    #     if domain not in domains:
    #         docs.remove(doc)
    #     if "profile" not in doc['url']:
    #         docs.remove(doc)

    #return docs


def get_to_visit_links_from_index(level):
    global channel

    # check if level is not empty: continue else stop.
    # check if level and visited false not empty
    # else increase level

    while True:
        print("-------------")
        print("Level:\t", level)

        query = {"visited": "", "level": level}
        docs = search_unvisited_index("to_visit_index", query)
        count_check = len(docs)

        if count_check == 0:
            return None
        total = count_check

        query = {"visited": False, "level": level}
        docs = search_unvisited_index("to_visit_index", query)
        count_check = len(docs)

        rem = count_check
        print("Progress:\t" + str(total - rem) + "/" + str(total))

        if count_check == 0:  # all documents visited at this level. Increase level.
            level = level + 1
            req_tf_idf = {
                'operation': 'tf_idf',
                'level': level - 1
            }
            channel.basic_publish(exchange='', routing_key='letterbox', body=json.dumps(req_tf_idf))
            continue

        else:  # at this level, there are unvisited documents.
            print("-----------------------------------------HERE")
            req_tf_idf = {
                'operation': 'tf_idf',
                'level': level
            }
            channel.basic_publish(exchange='', routing_key='letterbox', body=json.dumps(req_tf_idf))

            query = {"visited": False, "level": level}
            docs = search_unvisited_index("to_visit_index", query)
            return docs