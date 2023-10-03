from difflib import SequenceMatcher

def score (doc):
    '''
        ONEMLI ASAGIDAKI NOTLARI OKU VE ONA GORE ALGORTMA GELISTIR.
        - linklere ve icerige tf-idf yapmak zorundayiz
        - NER'in basarisiz oldugu durumlarda bu veriler kullanilir.
        - Ayni domainden 10 - 15 farkli sayfada linklere tf-idf yap.
        - domain collectionundaki sayilari kullan.
        
    '''


    if len(doc['NER_title_res']) == 0:
        print("title ner not found")

    if len(doc['NER_text_res']) == 0:
        print("text ner not found")

    # compare the domains and title of the page
    similarities = []

    for domain in doc['linked_domains']:
        similarities.append((domain, SequenceMatcher(None, domain, doc['title']).ratio()))

    similarities.sort(key=lambda a: a[1], reverse=True)
    # get tfidf result and scores of the document. if none, pass
    if not doc['domain_tf_idf_results']:
        print("No tf idf domain detected.")
        # try to detect linked domains field.
        doc['detected_company_domain'] = similarities[0][0]
    else:
        pass # calculate in case of detected domain

    doc['title_link_similarity'] = similarities

    return doc