import streamlit as st
from elasticsearch import Elasticsearch
es =  Elasticsearch("http://localhost:9200", \
                    http_auth=("elastic", "0dv5W=eRTUVeHZwc3PHt"), \
                        verify_certs=False)


def main():
    st.title('Search')
    search = st.text_input('Enter query:')
    if search:
        results = es.search(index="relevant", query={
		"multi_match" : {
            "query" : search,
            "type" : "most_fields",
            "fields": [
                "url^5",
                "keywords^5",
                "anchor^4",
                "title^4",
                "description^3",
                "text^1"
            ],
            "fuzziness" : "AUTO",
            "prefix_length" : 2
        }
	    })
        for a in results['hits']['hits'][0:10]:

            object = a['_source']
            keywords = " ".join(object['keywords'][0:5])

            st.markdown("#### " + object['title'].strip())
            st.markdown("##### " + object['url'])
            st.markdown("###### *" + keywords + "*")
            st.divider()


if __name__ == '__main__':
    main()