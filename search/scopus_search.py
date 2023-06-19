import time
import json
from arcas.tools import Api
#from .api_key import api_key
from xml.etree import ElementTree


class ScopusSearch(Api):
    def __init__(self):
        self.standard = 'https://api.elsevier.com/content/search/scopus?query='
        self.key_api = '7c77ee51e8576a4707753c94f17a37e1'

    def create_url_search(self, parameters):
        """Creates the search url, combining the standard url and various
        search parameters."""
        url = self.standard
        url += parameters[0]
        for i in parameters[1:]:
            if 'start=' in i or 'count=' in i:
                url += '&{}'.format(i)
            else:
                url += '+AND+{}'.format(i)
        url += '&apiKey={}'.format(self.key_api)
        time.sleep(3)
        return url

    def parse(self, root):
        """Parsing the xml file"""
        if len(root["search-results"]["entry"]):
            return root["search-results"]["entry"]
        
        print(root)

    @staticmethod
    def parameters_fix(author=None, title=None, abstract=None, start_year=None, end_year=None,
                       records=25, start_record=0, category=None, journal=None,
                       keyword=None):
        parameters = []
        if author is not None:
            parameters.append('AUTH({})'.format(author))
        if title is not None:
            parameters.append('TITLE({})'.format(title))
        if start_year is not None:
            parameters.append('PUBYEAR > {}'.format(start_year-1))
        if end_year is not None:
            parameters.append('PUBYEAR < {}'.format(end_year+1))
        # if category is not None:
        #     parameters.append('subject:{}'.format(category))
        # if journal is not None:
        #     parameters.append('pub:{}'.format(journal))
        if keyword is not None:
            if type(keyword) is list:
                parameters += keyword
            else:
                parameters.append('KEY({})'.format(keyword))
        if records is not None:
            parameters.append('count={}'.format(records))
        if start_record is not None:
            parameters.append('start={}'.format(start_record))
        #if abstract is not None:
            #print('Springer does not support argument abstract.')
            #print()

        return parameters

    @staticmethod
    def get_root(response):
        return json.loads(response.text)
    
    def to_standardized_dictionary(raw_article):
        standard_dict_object = {}
        standard_dict_object['doi'] = raw_article.get('prism:doi', None)
        standard_dict_object['title'] = raw_article.get('dc:title', None)
        #standard_dict_object['abstract'] = raw_article.get('abstract', None)
        standard_dict_object['url'] = raw_article.get('link', None)
        for link in standard_dict_object['url']:
            if link.get('@ref') == 'scopus':
                  standard_dict_object['url'] = link.get('@href')
        standard_dict_object['open_access'] = raw_article['openaccessFlag']
        standard_dict_object['source'] = 'scopus'
        return standard_dict_object