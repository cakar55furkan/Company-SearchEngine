import pymongo
from sklearn.feature_extraction.text import TfidfVectorizer
import es
from tldextract import extract

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['crawl']
relevant_collection = db['relevant']

def calculate_tf_idf():
    # check uncalculated tf idf
    doc_count = relevant_collection.count_documents({})
    
    if doc_count < 25:
        return
    
    docs = relevant_collection.find({"tf_idf_calculated" : False})
    for doc in docs:
        # get domain
        _, dom, _ = extract(doc['url'])

        similar_elements = list(relevant_collection.aggregate([
            {"$match" : {"url" : {"$regex" : dom}}},
            {"$sample" : {"size" : 25}}
        ]))
        if doc in similar_elements:
            similar_elements.remove(doc)
        
        random_elements = list(relevant_collection.aggregate([
                # {"$match" : {"visited" : True}}, 
                { "$sample": { "size": 25 }}
            ]))
        if doc in random_elements:
            random_elements.remove(doc)
        
        field_values = []
        field_values.append(doc['text_lemm'])
        
        for similar_element in similar_elements:
            field_values.append(similar_element['text_lemm'])
        for random_element in random_elements:
            field_values.append(random_element['text_lemm'])

        tfidf = TfidfVectorizer()
        result = tfidf.fit_transform(field_values)
        dict_of_tokens={i[1]:i[0] for i in tfidf.vocabulary_.items()}
        vectors = []
        for row in result:
            vectors.append({dict_of_tokens[column]:value for (column,value) in zip(row.indices,row.data)})
        

        result_dict = vectors[0]
        result_arr = []

        for key in result_dict.keys():
            result_arr.append((key, result_dict[key]))
        result_arr.sort(key=lambda a: a[1], reverse=True)
        
        if len(result_arr) > 20:
            result_arr = result_arr[0:20]
        final_arr = []
        for r in result_arr:
            final_arr.append(r[0])
            
        filter = { 'url': doc['url'] }
        newvalues = { "$set": { 'keywords': final_arr , "tf_idf_calculated" : True} }
        relevant_collection.update_one(filter, newvalues)
        doc['keywords'] = final_arr
        doc['tf_idf_calculated'] = True
        es.insert_document_to_index("relevant", es.mongo_to_es_object(doc), doc['url'])

        # save to ES here.