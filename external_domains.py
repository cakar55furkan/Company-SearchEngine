from tldextract import extract

def detect_linked_domains (soup, url, domain_collection):
    linked_domains = []

    _, this_domain, _ = extract(url)
    for link in soup.find_all('a', href=True):
        _, link_domain, _ = extract(link['href']) 

        if link_domain != "":
            linked_domains.append(link_domain)
            q_current_count = {"domain": link_domain}
            domain_db_record = domain_collection.find_one(q_current_count)

            if not domain_db_record:
                # create new one
                new_domain_document = {
                    "domain" : link_domain,
                    'count' : 1
                }
                try:
                    domain_collection.insert_one(new_domain_document)
                except Exception as e:
                    print("[-] Error creating domain collection.")
            else:
                # increment
                try:
                    current_count = domain_db_record['count']
                    myquery = { "domain": link_domain }
                    newvalues = { "$set": { "count": current_count + 1 } }

                    domain_collection.update_one(myquery, newvalues)
                    # print("[+] domain count incremented.")
                except Exception as e:
                    print("[-] Error updating domain collection.")
        else:
            # print("[-] error in link:", link['href'])
            pass
    return list(set(linked_domains))