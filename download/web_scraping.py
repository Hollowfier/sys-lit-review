import json
import pandas as pd
import requests
import time
import random


from bs4 import BeautifulSoup
from tqdm import tqdm
'''
Accepts a excel file with at least 1 column: Paper Title. 
Scrapes for URL on Google Scholar and fetches it in a json file. 
'''
file_name = '<INSERT FILE NAME HERE>'

user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\ AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)']

status_enum = {
    'LIMIT_EXCEEDED': 429,
    'SUCCESS': 200,
    'CAPTCHA_ID': "gs_captcha_f",
    'CAPTCHA_MSG': "Please show you're not a robot",
    'DOCS_COUNT': 863
}

sheet = pd.ExcelFile(file_name)
sheet = sheet.sheet_names[0]
data = pd.read_excel(file_name, sheet_name=sheet)
# paper_titles = data['Title'].fillna('').tolist()
paper_titles = data.query('URL != URL')['Title'].fillna('').tolist()
paper_repos = []

def get_paperinfo(paper_url):
    headers = { 
        'User-Agent': user_agents[random.randrange(len(user_agents))] 
    }
    
    #download the page
    response=requests.get(paper_url, headers=headers)
  
    # with open("response.html", "wb") as outfile:
        # outfile.write(response.content)
    
    # print(response.content)
    #check successful response
    if response.status_code == status_enum['LIMIT_EXCEEDED']: 
        return False
    
    if response.status_code != status_enum['SUCCESS']:
        print('Status code:', response.status_code, ' for url:', paper_url)
        return False

    #parse using beautiful soup
    paper_doc = BeautifulSoup(response.text,'html.parser')
    #check for captcha
  
    captcha_body = paper_doc.find("form", {"id" : status_enum['CAPTCHA_ID']})
    if captcha_body:
        captcha_text = captcha_body.find('h1').text
        if captcha_text == status_enum['CAPTCHA_MSG']:
            return False
    
    # All successful return the bs4 object
    return paper_doc

def get_link(doc, title):
    link_tags = doc.find_all('div', {'class': 'gs_or_ggsm'})
    link = link_tags[0]  if len(link_tags) else ''
    if not link:
        link = doc.find_all('h3',{"class" : "gs_rt"})
        if len(link) and link[0].find('a'):
                link = link[0].a['href']
                return_link = link if bool(link.strip()) else 'LINK_NOT_FOUND'
        else:
            return 'LINK_NOT_FOUND'
    else:
        return_link = link.a['href'] if bool(link.a['href'].strip()) else 'LINK_NOT_FOUND'
    return return_link


def add_in_paper_repo(papername, link):
    paper_repos.append({ 'paper_title' : papername, 'paper_url' : link })

# change starting point from where you want to scrape in the excel sheet
start = 0

for i, title in tqdm(enumerate(paper_titles[start:])):
    if title:
        # get url for the each paper
        url = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={}&btnG='.format(title.replace(" ", "+"))
        #print(url)

        # function for the get content of each page
        doc = get_paperinfo(url)

        if not doc:
            # 429 encountered or Failed to fetch web page. 
            # Stop the code and save the info in file!
            break

        # url of the paper
        link = get_link(doc, title)

        # add in paper repo dict
        final = add_in_paper_repo(title, link)

        # use sleep to avoid status code 429
        time.sleep(random.randint(5, 10))


if i > 0:
    with open("paper_links_" + str(start) + ".json", "w") as outfile:
        outfile.write(json.dumps(paper_repos, indent=2))

if i == status_enum['DOCS_COUNT']:
    print('Complete! No need to run again!')
else:
    print('429 encountered or Failed to fetch web page! Start next time from', start + i)