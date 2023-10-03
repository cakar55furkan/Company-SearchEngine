import sys
import os
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import pymongo
import math 
import string
from visit import visit

def calculate_relevancy(soup):
    """
    Calculates the relevancy between given page and Topic Word Table.
    """
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    title = ""
    desc = ""
    try:
        title = soup.find("meta", property="og:title")["content"]
        desc =  soup.find("meta", property="og:description")["content"]
    except Exception as e:
        pass
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    content_text = soup.get_text(separator=" ", strip=True) # get text context
    
    content_words = word_tokenize(content_text)
    content_lemm_words = []
    for word in content_words:
        word = word.lower()
        word = word.translate(str.maketrans('', '', string.punctuation))
        if word not in stop_words:
            content_lemm_words.append(lemmatizer.lemmatize(word))


    title_words = word_tokenize(title)
    title_lemm_words = []
    for word in title_words:
        word = word.lower()
        word = word.translate(str.maketrans('', '', string.punctuation))
        if word not in stop_words:
            title_lemm_words.append(word)

    desc_words = word_tokenize(desc)
    desc_lemm_words = []
    for word in desc_words:
        word = word.lower()
        word = word.translate(str.maketrans('', '', string.punctuation))
        if word not in stop_words:
            desc_lemm_words.append(word)


    cont_lemm_word_str = " ".join([str(s) for s in content_lemm_words])
    title_lemm_word_str = " ".join([str(s) for s in title_lemm_words])
    desc_lemm_word_str = " ".join([str(s) for s in desc_lemm_words])

    db = client['twdb']
    collection = db['twdb']
    a = collection.find({}).sort('date', pymongo.DESCENDING)
    twwt = a[0]['table'] # most recent twwt

    twwt_scores = []
    wkt_squares = []
    wkp_squares = []


    for topic_word in twwt:
        loc_scr = 0
        cont_count = 0
        title_count = 0
        desc_count = 0

        topic_word_str = topic_word[0]
        topic_word_score = topic_word[1]


        cont_count = cont_lemm_word_str.count(topic_word_str)
        # print("content: ", str(cont_count))
        
        title_count = title_lemm_word_str.count(topic_word_str)
        # print("title: ", str(title_count))
        
        desc_count = desc_lemm_word_str.count(topic_word_str)
        # print("content: ", str(desc_count))

        # bu tw icin toplam skor 
        loc_scr = 2 * topic_word_score * title_count + \
        2 * topic_word_score * desc_count + \
        1 * topic_word_score * cont_count
        # print ("total score: ", loc_scr)
        
        twwt_scores.append(loc_scr)
        wkt_squares.append(topic_word_score**2)
        
        wkp_freq = 2 * title_count + 2 * desc_count + 1 * cont_count
        wkp_squares.append(wkp_freq**2)

        #  count in text
        # count in metadata
    wkt_acc = sum(wkt_squares)
    wkp_acc = sum(wkp_squares)

    us = sum(twwt_scores)
    taban = math.sqrt(wkt_acc * wkp_acc)
    res = 0
    try:
        res = us/taban
    except:
        pass
    
    return res

