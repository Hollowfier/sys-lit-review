import os
import pandas as pd
import pathlib
import plotly.express as px
import re
import yake

from fuzzysearch import find_near_matches
from nltk.corpus import stopwords
from tqdm import tqdm



# remove hyphens and underscore for processing of text 
def clean_text(text):
    text = text.lower()
    #text = re.sub(r"[,.;@#?!&$-_]+\ *", " ", text)
    text = text.replace('-', ' ')
    text = text.replace('_', ' ')
    text = text.replace('.txt','')
    return text

def preprocess(text):
    # remove white spaces, html tags, numbers, special characters, punctuations

    RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
    RE_TAGS = re.compile(r"<[^>]+>")
    RE_ASCII = re.compile(r"[^A-Za-zÀ-ž ]", re.IGNORECASE)
    RE_SMALLWORDS = re.compile(r"\b[A-Za-zÀ-ž]{1,3}\b", re.IGNORECASE)

    text = re.sub(RE_TAGS, " ", text)
    text = re.sub(RE_ASCII, " ", text)
    text = re.sub(RE_SMALLWORDS, " ", text)
    text = re.sub(RE_WSPACE, " ", text)

    word_tokens = text.split()
    words_tokens_lower = [word.lower() for word in word_tokens if word.lower() not in stop]

    text_clean = " ".join(words_tokens_lower)
    return text_clean

def get_list_from_excel(sheet):
    ki_tags = pd.read_excel('ki_tags_techniques.xlsx', sheet_name=sheet)
    ki_tags = list(set(list(ki_tags['Name'][2:])))
    
    ki_tags_final = []
    for tag in ki_tags:
        sub_tag = None
        tag = tag.lower()
        if tag.find('(') > -1 and tag.find(')') > -1:
            sub_tag = tag[tag.find('(')+1:tag.find(')')]
            tag = tag[:tag.find('(')]
            
        ki_tags_final.append(tag.replace('\xa0', ''))
        #if sub_tag:
        #    ki_tags_final.append(sub_tag.replace('\xa0', ''))
    
    return ki_tags_final

def count_key_word(search_list):
    list_keywords = []
    for i,j in tqdm(df.iterrows()):
        counter = {}
        for ki in search_list:
            counter[ki] = len(find_near_matches(ki, j['CoreText'], max_l_dist=0))

        counter = {x:y for x,y in counter.items() if y!=0}
        list_keywords.append(counter.copy())
        
    return list_keywords

# Read all the gathered papers
script_directory = pathlib.Path('__file__').parent.resolve()
dir_path = os.path.join(script_directory, 'paper_texts')
# Open all text files in the folder and save them in a list
text = []
file_names = []

for path in tqdm(os.listdir(dir_path)):
    path = os.path.join(dir_path, path)
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)) and path.endswith('.txt'):
        # Open file
        with open(path, 'r', encoding='utf-8') as txt:
            file_names.append(path.split('\\')[-1])
            text += [txt.read()]

for i in range(len(file_names)):
    file_names[i] = clean_text(file_names[i])

for i in range(len(text)):
    text[i] = clean_text(text[i])

### Create a dataframe 
df = pd.DataFrame({'Title': file_names, 'Text': text})
df.head()

stop = stopwords.words('english')
# add custom stopwords here
stop += ['ieee', 'universittsbibliothek', 'downloaded', 'xplore', 'utc', 'paderborn']

df['CoreText'] = df.apply(lambda x: preprocess(x['Text']), axis=1)


### Extract bigram keywords using YAKE
max_ngram_size = 2
window_size = 1
deduplication_threshold = 0.3
num_of_keywords = 10
kw_extractor = yake.KeywordExtractor(n=max_ngram_size, dedupLim=deduplication_threshold, top=num_of_keywords, windowsSize=window_size)
df['yake_kws'] = df['CoreText'].apply(kw_extractor.extract_keywords)

df.head()

ki_tags = get_list_from_excel('OECD_2020')
#ki_algorithms = get_list_from_excel('Algorithms')
print("Number of unique KI-Tags ", len(ki_tags))


df['KI_Tags_Lookup'] = count_key_word(ki_tags)

### Draw Treemap

data_map = []

for i, row in df.iterrows():
    keywords = row['KI_Tags_Lookup']
    #center = row['Zuordnung_cluster']
    #prod_cyle = row['Prod_cycles']
    #if not prod_cyle == 'no_product_cycle': 
    for kw, val in sorted(keywords.items(), key=lambda item: item[1], reverse= True):
        obj = list(filter(lambda d: d['keyword'] == kw, data_map))
        if len(obj) == 0:
            data_map.append({
                'keyword': kw,
                'value': val
            })
        else:
            obj[0]['value'] += val
    
fig = px.treemap(
    pd.DataFrame.from_dict(data_map), path=['keyword'], 
    values='value', color='value', color_continuous_scale='blues')

fig.data[0].textinfo = 'label+value'
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.data[0]['textfont']['size'] = 13
fig.show()