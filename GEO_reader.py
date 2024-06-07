import requests
import xml.etree.ElementTree as ET
import xmltodict
import traceback
import json
import pandas as pd 
import sqlparse
import openpyxl

#def python_SRA(accession):

first_req = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&usehistory=y&retmode=json&term=GSE30567')

xml_as_string = str(first_req.content)
print(xml_as_string)

querykey_index = xml_as_string.find("querykey")
if querykey_index == -1:
    raise ValueError("querykey not found, is your accession key correct?")
querykey = ""
for key in xml_as_string[querykey_index + 11:1000:1]:
    if key == '"':
        break
    querykey = querykey + key
print(querykey)

webenv_index = xml_as_string.find("webenv")
if webenv_index == -1:
    raise ValueError("webenv not found")
webenv = ""
for key in xml_as_string[webenv_index + 9:1000:1]:
    if key == '"':
        break
    webenv = webenv + key
print(webenv)

retstart_index = xml_as_string.find("retstart")
if retstart_index == -1:
    raise ValueError("retstart not found")
retstart = ""
for key in xml_as_string[retstart_index + 11:1000:1]:
    if key == '"':
        break
    retstart = retstart + key
print(retstart)

retmax_index = xml_as_string.find("retmax")
if retmax_index == -1:
    raise ValueError("retmax not found")
retmax = ""
for key in xml_as_string[retmax_index + 9:1000:1]:
    if key == '"':
        break
    retmax = retmax + key
print(retmax)

print('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=sra&retmode=json&query_key=1&WebEnv=MCID_65283c5f4a58ec590412a3fd&retstart=0&retmax=20')
second_req = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=sra&retmode=json&query_key='+querykey+'&WebEnv='+webenv+'&retstart='+retstart+'&retmax='+retmax)
#second_req = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&query_key=1&WebEnv=MCID_6536f7ce1f6b9168fb25fffa')
#^testing the example code

xml_as_string_two = json.dumps(str(second_req.content))

dict=json.loads(second_req.content)
df = pd.DataFrame.from_dict(dict)
print(df)

df.to_excel('/Users/sdabiz/Desktop/work/python/GEO_dataset_reader/output.xlsx', index=False)

#parsed_data = json.loads(xml_as_string_two)
#print(parsed_data)


#testing_string = '<Run acc=\\"SRR545707\\" total_spots=\\"132793805\\" total_bases=\\"26824348610\\" load_done=\\"true\\" is_public=\\"true\\" cluster_name=\\"public\\" static_data_available=\\"true\\"/><Run acc=\\"SRR545708\\" total_spots=\\"122623681\\" total_bases=\\"24769983562\\" load_done=\\"true\\" is_public=\\"true\\" cluster_name=\\"public\\" static_data_available=\\"true\\"/>'

#tree = ET.fromstring(testing_string)


#with open('first.xml', 'wb') as file:
#    file.write(req.content)
#xmlstr = ET.tostring(req.content, encoding='utf-8', method='xml')
#try:
#data = ET.parse(req.content)
#except:
#    print("Failed to parse xml from response (%s)" % traceback.format_exc())



#import urllib3
#import xmltodict

#def python_SRA(accession):
#    file = urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&usehistory=y&retmode=json&term='+accession)
#    data = file.read()
#    file.close()

#    data = xmltodict.parse(data)
#    return render_to_response('my_template.html', {'data': data})

#tried turning the xml into a string.
#tried parsing with JSON.
#tried parsing a JSON string.
#trist parsing a JSON file that I created.
#looked into sql parsing... didn't understand it very well.
#my parser is the ET import
#im not so sure its a json or xml