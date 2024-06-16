import requests

def search_ena():
    base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    #only the UK works?
    query = 'host_tax_id=9913 AND host_body_site="rumen"'
    #fields = 'host_body_site,host_tax_id,country,submitted_ftp'
    fields = 'sample_accession,run_accession,study_accession,read_count,sample_title'
    result_type = "read_run"
    format_type = "json"  # or tsv?
    
    params = {
        "result": result_type,
        "query": query,
        "fields": fields,
        "format": format_type,
        "limit": "0"  # no limit?
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # write to file
        with open("results.txt", "w") as file:
            json_data = response.json()
            for item in json_data:
                file.write(str(item) + '\n')
        return "Results written to results.txt"
    else:
        return f"Failed to fetch data: {response.status_code}"

if __name__ == "__main__":
    result_message = search_ena()
    print(result_message)
