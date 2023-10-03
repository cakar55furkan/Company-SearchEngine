import en_core_web_lg
import json

nlp = en_core_web_lg.load()


def apply_NER(doc):
    global nlp
    title_nlp = nlp(str(doc['title']))
    title_res = []
    
    text_nlp = nlp(str('text'))
    text_res = []

    address_res = []

    for res in title_nlp.ents:
        if res.label_ == "ORG":
            title_res.append(res.text)
        elif res.label_ == "GPE" or res.label_ == "LOC":
            address_res.append(res.text)
        

    for res in text_nlp.ents:
        if res.label_ == "ORG":
            text_res.append(res.text)
        elif res.label_ == "GPE" or res.label_ == "LOC":
            address_res.append(res.text)
    
    doc['NER_title_res'] = title_res
    doc['NER_text_res'] = text_res
    doc['NER_adress_res'] = address_res

    return doc