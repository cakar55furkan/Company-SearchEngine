def get_ordered_links(level, frontier, focused_mode):
    print("finding links at level : ", str(level))
    links = []
    from_irrelevant = []
    max_score = 0
    irr_max_score = 0
    try:
        max_score = frontier.find({"level" : level, "count" : {"$gt" : 0}}).sort("link_score", -1)[0]['link_score']
        irr_max_score = frontier.find({"level" : level, "count" : 0}).sort("link_score", -1)[0]['link_score']
    except:
        pass
    if not focused_mode:
        links = list(frontier.find({"visited" : False,"level" : level}))

    else:
        # get links from relevant pages
        links = list(frontier.find({"visited" : False,"level" : level, "count" : {"$gt" : 0}}))
        # get links from unrelevant pages (count = 0), check the depth. calculate the link score. and sort using another cutoff
        from_irrelevant = list(frontier.find({"visited" : False, "level" : level, "count" : 0}))
    
    
    
    if len(links) == 0 and len(from_irrelevant) == 0:
        return None
   
    try:
        links.sort(key=lambda x: x["link_score"], reverse=True)
    except:
        pass

    try:
        from_irrelevant.sort(key=lambda x: x['link_score'], reverse=True)
    except:
        pass

    result = []
    cut_off = 0
    if len(links) > 0:
        cut_off = max_score * 0.25
        for link in links:
            if link['link_score'] > cut_off:
                result.append(link)

    if len(from_irrelevant) > 0:
        cut_off = irr_max_score * 0.25
        for link in from_irrelevant:
            if link['link_score'] >= cut_off:
                result.append(link)
    return result 
