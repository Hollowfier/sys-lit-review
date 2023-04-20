# Artificial Intelligence; Machine Learning; Deep Learning; Neural Network; Computer Vision; Image Processing; Knowledge Representation; Data Mining; Natural Language Processing; NLP;  Computational Intelligence; Advanced Data Analytics; Data Science; Big Data
# Product Creation; Product Planning; Product Development; Product Engineering; Service Development; Service Engineering; Production System Development; Production System Engineering; Product Lifecycle Management
# Review; Survey; Literature Study
# Case Study; Use Case; Application

import itertools

class Queries:

    def __init__(self, keywords) -> None:
        self.map_of_keywords = keywords
        self.final_list_of_queries = []

    def form_simple_queries(self):
        list_of_queries = list(itertools.product(*self.map_of_keywords))
        for query_tuple in list_of_queries:
            #print(query_tuple)
            query_tuple = ["\"" + x + "\"" for x in query_tuple]
            #print(query_tuple)
            query = "(" + ' AND '.join(query_tuple) + ")"
            query.replace(' ', '%20')
            self.final_list_of_queries.append(query)
    
        return self.final_list_of_queries


#print(queries[0])


