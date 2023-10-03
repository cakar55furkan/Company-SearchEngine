import pymongo
from pymongo import MongoClient
import datetime
import string
from TWWT.get_text_content import visit
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from googlesearch import search
from datetime import date


def create_twwt(query, stop):
    client = MongoClient("localhost", 27017)
    db = client.twdb
    collection = db.twdb

    search_results = search(query,  num=50, stop=stop)
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    docs = []

    for idx, search_result in enumerate(search_results):
        print(search_result, " loading!")
        soup_object = visit(search_result)
        if soup_object != None:
            text = soup_object.get_text(separator=" ", strip=True)
            words = word_tokenize(text)
            lemm_words = []
            for word in words:
                word = word.lower()
                word = word.translate(str.maketrans('', '', string.punctuation))
                lemm_words.append(lemmatizer.lemmatize(word))
            for lemm_word in lemm_words:
                if lemm_word in stop_words:
                    lemm_words.remove(lemm_word)
            docs.append(" ".join([str(w) for w in lemm_words]))
        else:
            print("error fetching.")

    print("Visit done. Total Result: ", str(len(docs)))

    sentences = []
    word_set = []

    for sent in docs:
        words = [word.lower() for word in word_tokenize(sent) if word.isalpha()]
        for idx,word in enumerate(words):
            if word[0:3] == "ico":
                words[idx] = word[3:]
        sentences.append(words)
        for word in words:
            if word not in word_set:
                word_set.append(word)

    word_set = set(word_set)

    total_docs = len(docs)
    print('Total documents: ', total_docs)
    print('Total words: ', len(word_set))
    word_index = {}
    for i, word in enumerate(word_set):
        word_index[word] = i


    count_dict = {}
    
    for word in word_set:
        count_dict[word] = 0
    for sent in sentences:
        for word in sent:
            count_dict[word] += 1

    doc_dict = {}
    for k in count_dict.keys():
        cnt = 0
        for doc in docs:
            if k in doc:
                cnt = cnt + 1
        doc_dict[k] = cnt
    

    mult_dict = {}
    for k in doc_dict.keys():
        mult_dict[k] = doc_dict[k] * count_dict[k]
    
    res = sorted(mult_dict.items(), key=lambda x:x[1], reverse=True)
    for a in res:
        if a[0] in stop_words:
            res.remove(a)
            
    normalized = []
    for r in res[0:10]:
        word = r[0]
        val = r[1] / res[0][1]
        normalized.append((word, val))

    db_obj = {
        "table": normalized,
        "date": datetime.datetime.now()
    }

    collection.insert_one(db_obj)

    



