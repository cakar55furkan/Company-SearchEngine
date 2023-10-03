from link_score.get_parent import get_parent


def calculate_link_score(doc, twwt):
    """
        Gets frontier element and calculates its score using Topic Word Table.
    """

    total_score = 0

    parents_score = 0
    current_doc = doc
    for i in range(3):
        parent = get_parent(current_doc)
        if parent:
            parents_score += parent['relevancy']
        current_doc = parent

    total_score += parents_score
    # start a loop and get parents if any.

    
    #get anchor
    anchor_str = ''
    try: # anchor field for seeds are not initalized. So there may be an error.
        anchor_str = " ".join([a for a in list(doc['anchor'])])
        anchor_str = anchor_str.lower()
    except:
        pass

    # get url
    url_str = str(doc['url']).lower()
    for element in twwt: # iterate through topic words.
        word = element[0]
        score = element[1]

        element_score = 0

        anchor_count = 0
        url_count = 0

        anchor_count = anchor_str.count(word)
        url_count = url_str.count(word)

        element_score = (anchor_count + url_count) * score
        total_score += element_score
    
    # add count
    try:
        total_score += doc['count']
    except:
        pass
    
    return total_score
    







