import os
import re
import string


def clean_text(text):
    text = text.lower()
    text = ''.join(ch for ch in text if ch.isalnum())
    return text.strip()


def download_paper(url, name):
    name = '"' + clean_text(name) +'.pdf"'
    cmd = 'wget ' + url + ' -O ' + name
    output = os.system(cmd)
    return True if output == 0 else False

def get_science_direct_papers(url, name):
    suffix = '/pdfft?isDTMRedir=true&amp;download=true'
    url += suffix
    download_paper(url, name)


def get_springer_papers(url, name):
    if url.find('.pdf') > -1:
        download_paper(url, name)
    elif url.find('article') > -1:
        url = url.replace('/article/', '/content/pdf/')
        url += '.pdf'
        download_paper(url, name)

def get_arxiv_papers(url, name):
    download_paper(url, name)

def get_ieee_papers(url, name):
    try:
        # Extract the journal id out of the link, old papers can have 6 digits
        journal_id = re.findall("\/\d{6,7}|\=\d{6,7}", url)[0].replace("/","")    
    except IndexError:
        raise ValueError(f"URL does not include the 7 digit long IEEE journal id that is required to download the paper: {url}")

    pdf_url = fr"http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber={journal_id}"
    #print(pdf_url)
    pdf_url = '"' + pdf_url + '"'
    if not name:
        name = journal_id
    if not name.endswith(".pdf"):
        name = name+".pdf"
    name = name.replace('/', ' or ')
    name = '"' + name + '"'
    cmd = 'wget ' + pdf_url + ' -O ' + name
    # download file
    os.system(cmd)