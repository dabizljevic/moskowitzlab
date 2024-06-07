import requests
from bs4 import BeautifulSoup
import re
import sys

def reader():
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esearch_params = {
        "db": "gds",
        "term": "yeast[orgn] AND 2007/01:2007/03[PDAT] AND (gse[ETYP] OR gds[ETYP])",
        "retmax": "5000",
        "usehistory": "y"
    }

    esearch_response = requests.get(esearch_url, params=esearch_params)
    esearch_soup = BeautifulSoup(esearch_response.content, features='xml')
    
    #count = int(esearch_soup.find('Count').text)   FIGURE OUT WHAT COUNT DOES
    #if count == 0:
    #    print("No items found.")
    #    return
 
    query_key = esearch_soup.find('QueryKey').text
    web_env = esearch_soup.find('WebEnv').text

    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    efetch_params = {
        "db": "gds",
        "query_key": query_key,
        "WebEnv": web_env
    }   

    efetch_response = requests.get(efetch_url, params=efetch_params)
    print(efetch_response.text)

if __name__ == "__main__":
    reader()
    