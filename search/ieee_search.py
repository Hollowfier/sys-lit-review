import requests
import ratelimit
from arcas.tools import Api
from arcas.tools import APIError

class IeeeSearch(Api):
    """
     API argument is 'ieee'.
    """
    def __init__(self):
        self.standard = 'https://ieeexploreapi.ieee.org/api/v1/search/articles?'
        self.key_api = 'bjxzyx3wk4yce8zd6wd9e2yf'

    def create_url_search(self, parameters):
        """Creates the search url, combining the standard url and various
        search parameters."""
        url = self.standard
        url += parameters[0]
        for i in parameters[1:]:
            url += '&{}'.format(i)
        url += '&apikey={}'.format(self.key_api)
        return url

    @staticmethod
    @ratelimit.rate_limited(3)
    def make_request(url):
        """Request from an API and returns response."""
        response = requests.get(url, stream=True, verify=False)
        if response.status_code != 200:
            raise APIError(response.status_code)
        return response

    def to_dataframe(self, raw_article):
        """A function which takes a dictionary with structure of the IEEE
        results and transform it to a standardized format.
        """
        raw_article['url'] = raw_article.get('pdf_url', None)
        try:
            raw_article['author'] = [author['full_name'] for author in raw_article['authors']['authors']]
        except KeyError:
            raw_article['author'] = ['No authors found for this document.']
        raw_article['abstract'] = raw_article.get('abstract', None)
        if raw_article['content_type'] == 'Conferences':
            date = raw_article.get('conference_dates', None)
        else:
            date = raw_article.get('publication_date', None)
        if date is not None:
            date = int(date.split(' ')[-1])
        raw_article['date'] = date

        category = raw_article.get('index_terms', None)
        if category is not None:
            try:
                category = category['author_terms']['terms']
            except KeyError:
                try:
                    category = category['ieee_terms']['terms']
                except KeyError:
                    category = None
        raw_article['doi'] = raw_article.get('doi', None)
        raw_article['category'] = category

        raw_article['journal'] = raw_article.get('publication_title', None)
        raw_article['provenance'] = 'IEEE'
        raw_article['key'], raw_article['unique_key'] = self.create_keys(raw_article)

        raw_article['open_access'] = raw_article['access_type'] == 'OPEN_ACCESS'
        raw_article['score'] = 'Not available'
        return self.dict_to_dataframe(raw_article)

    def parse(self, root):
        """Parsing the response data"""
        if root['total_records'] == 0:
            return False
        return root['articles']

    @staticmethod
    def parameters_fix(author=None, title=None, abstract=None, year=None,
                       records=None, start_record=None, category=None, journal=None,
                       keyword=None, start_year=None, end_year=None, open_access=None, 
                       sort_field=None, sort_order=None):
        parameters = []
        if author is not None:
            parameters.append('author={}'.format(author))
        if title is not None:
            parameters.append('article_title={}'.format(title))
        if abstract is not None:
            parameters.append('abstract={}'.format(abstract))
        if year is not None:
            parameters.append('publication_year={}'.format(year))
        if category is not None:
            parameters.append('index_terms={}'.format(category))
        if journal is not None:
            parameters.append('publication_title={}'.format(journal))
        if keyword is not None:
            parameters.append('querytext={}'.format(keyword))
        if records is not None:
            parameters.append('max_records={}'.format(records))
        if start_record is not None:
            parameters.append('start_record={}'.format(start_record))
        
        if start_year is not None:
            parameters.append('start_year={}'.format(start_year))
        if end_year is not None:
            parameters.append('end_year={}'.format(end_year))
        if open_access is not None:
            parameters.append('open_access={}'.format(open_access))
        
        if sort_field is not None:
            parameters.append('sort_field={}'.format(sort_field))
        else:
            parameters.append('sort_field=article_number')
        
        if sort_order is not None:
            parameters.append('sort_order={}'.format(sort_order))
        else:
            parameters.append('sort_order=asc')
            
        return parameters

    @staticmethod
    def get_root(response):
        root = response.json()
        if root['total_records']:
            return root
        else: 
            return None


    def to_standardized_dictionary(self, raw_article):
        standard_dict_object = {}
        standard_dict_object['doi'] = raw_article.get('doi', None)
        standard_dict_object['title'] = raw_article.get('title', None)
        standard_dict_object['abstract'] = raw_article.get('abstract', None)
        standard_dict_object['url'] = raw_article.get('pdf_url', None)
        standard_dict_object['open_access'] = raw_article['access_type'] == 'OPEN_ACCESS'
        standard_dict_object['source'] = 'ieee'
        return standard_dict_object
        
# main-api-key = 'bjxzyx3wk4yce8zd6wd9e2yf'
# backup-api-key = 'hjdyck49fz46r8yfpju8h2kc'