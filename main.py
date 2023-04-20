import json
import os

from query.form_queries import Queries
from search.ieee_search import IeeeSearch
from time import time

''' 
TODO:
Define data models for storing

1. Review Info - date & time of review, keywords and start-end year
2. Search Queries - Mapping of Review and Search Queries
3. Papers - Title, Authors, Abstract, Paper Url, Date Published, Open Access
As we move ahead, we would also need isSelected, isDownloaded, DownloadUri in Papers
4. Query - Paper Mapping
5. Data Extraction & Paper Mapping

'''
review_data = {}

# Input Year
year_string = input("Enter a year range [start-end]:\n")
start_year, end_year = map(int, year_string.split("-"))

review_data['start_year'] = start_year
review_data['end_year'] = end_year

# Input Keywords
areas_of_interest = int(input("How many classes of keywords? Enter a number [1-9]:\n"))
keywords_map = ['']*areas_of_interest
#print(keywords_map)
count_keywords = 0

review_data['areas_of_interest'] = areas_of_interest


for i in range(areas_of_interest):
    input_string = input("\nEnter Keywords in class {}. Please separate the keywords with a semi-colon (;)\n".format(i+1))
    list_of_kws = input_string.split(';')
    list_of_kws = [x.lower().strip() for x in list_of_kws]
    count_keywords += len(list_of_kws)
    keywords_map[i] = list_of_kws.copy()
    print('Read {} keywords for class {}'.format(len(list_of_kws), i+1))

print('\nThank you!\nYou have entered a total of {} keywords across {} classes\n'.format(count_keywords, len(keywords_map)))

review_data['keywords'] = keywords_map

qstart = time()
queries = Queries(keywords_map).form_simple_queries()
qend = time()

print('Created {} queries from input keywords'.format(len(queries)))

review_data['time_query_formation'] = qend - qstart
review_data['basic_queries'] = queries

print("Searching in IEEE database - ")

searcher = IeeeSearch()

#TODO: Figure out how to get all documents from a search string 
totals = 200
records_size = 200
raw_articles = []
query_paper_map = {}
s_start = time()

for search_strings in queries:
    start, continue_search = 0, True
    while continue_search:
        #print(search_strings)
        parameters = searcher.parameters_fix(keyword=search_strings, start_year=start_year, end_year=end_year,
                                        records=records_size, start_record=(1 + start * records_size))
        #print(parameters)
        url = searcher.create_url_search(parameters)
        print(url)
        request = searcher.make_request(url)
        if request:
            #print(request.text)
            root = searcher.get_root(request)
            #print(root)
            if root:

                searched_papers = searcher.parse(root)

                if len(searched_papers) < records_size:
                    continue_search = False
                else:
                    start += 1

                raw_articles += searched_papers
                query_paper_map[search_strings] = query_paper_map.get(search_strings, []) + searched_papers
            else:
                continue_search = False
        else:
            continue_search = False

s_end = time()


review_data['query_paper_map'] = query_paper_map
review_data['time_search_papers'] = s_end - s_start
review_data['search_papers'] = raw_articles

file_path = os.getcwd() + '\\output\\review_process.json'
with open(file_path, 'w') as f:
    json.dump(review_data, f)

