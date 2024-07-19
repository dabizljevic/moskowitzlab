import requests
import sys

def search_ena(query):
    base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    
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
    if len(sys.argv) == 2:
        #looks up sequence
        if (sys.argv[1].lower() == 'sequence'):
            s = input("Enter your sequence: ")
            query = 'accession="' + s + '"' #looks like   accession="sequence"

        #looks up keywords FILL IN lATER
        if (sys.argv[1].lower() == 'keyword'):
            query = 'country="United Kingdom" AND host_tax_id=9913 AND body_site="rumen"'
        
    result_message = search_ena(query)
    print(result_message)





from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# List of all possible fields
fields = [
    "accession", "allele", "analysis_type", "base_count", "breed", "cell_line",
    "cell_type", "collected_by", "collection_date", "country", "environment_biome",
    "experiment", "gene", "geo_accession", "host", "host_body_site", "host_common_name",
    "host_genotype", "host_phenotype", "host_scientific_name", "host_sex", "host_tax_id",
    "sample_accession", "sample_title"
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ENA Search Tool</title>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            updateForm();  // Initialize form on page load
        });

        function updateForm() {
            var form = document.getElementById('query_form');
            form.innerHTML = `{", ".join(f'<label for="{field}">{field.replace("_", " ").title()}:</label><input type="text" id="{field}" name="{field}"><br>' for field in fields)}`;
        }
    </script>
</head>
<body>
    <h1>ENA Search Tool</h1>
    <form action="/" method="post">
        <div id="query_form">
            <!-- Dynamic form fields will be inserted here -->
        </div>
        <button type="submit">Search</button>
    </form>
    {% if results %}
        <h2>Results:</h2>
        <pre>{{ results }}</pre>
    {% endif %}
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query_parts = []
        for field in fields:
            value = request.form.get(field)
            if value:
                query_parts.append(f'{field}="{value}"')
        query = " AND ".join(query_parts) if query_parts else ''

        results = search_ena(query)
        return render_template_string(HTML_TEMPLATE, results=results)
    return render_template_string(HTML_TEMPLATE, results=None)

def search_ena(query):
    base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    result_fields = 'sample_accession,run_accession,study_accession,read_count,sample_title'
    result_type = "read_run"
    format_type = "json"
    params = {
        "result": result_type,
        "query": query,
        "fields": result_fields,
        "format": format_type,
        "limit": "0"
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # Parse the JSON into a Python list of dictionaries
        data = response.json()
        # Format the output
        results = []
        for entry in data:
            formatted_entry = f"Sample Accession: {entry['sample_accession']}, Run Accession: {entry['run_accession']}, " \
                              f"Study Accession: {entry['study_accession']}, Read Count: {entry['read_count']}, " \
                              f"Sample Title: {entry['sample_title']}"
            results.append(formatted_entry)
        return "\n".join(results)
    else:
        return f"Failed to fetch data: {response.status_code}"

if __name__ == "__main__":
    app.run(debug=True)


accession
allele
analysis_type
base_count
breed
cell_line
cell_type
collected_by
collection_date
country
environment_biome
experiment
gene
geo_accession
host
host_body_site
host_common_name
host_genotype
host_phenotype
host_scientific_name
host_sex
host_tax_id
sample_accession
sample_title

description
study_description




from flask import Flask, request, render_template_string, send_filestu
import requests
import pandas as pd

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ENA Search Tool</title>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            updateForm();  // Initialize form on page load
        });

        function updateForm() {
            var select = document.getElementById('query_type');
            var queryValue = select.value;
            var form = document.getElementById('query_form');

            if (queryValue === 'searchterm') {
                form.innerHTML = '<label for="query">Enter your searchterm:</label>' +
                                 '<input type="text" id="query" name="query" required>';
            } else if (queryValue === 'keyword') {
                form.innerHTML = '<label for="country">Country:</label>' +
                                 '<input type="text" id="country" name="country"><br>' +
                                 '<label for="host_tax_id">Host Tax ID:</label>' +
                                 '<input type="text" id="host_tax_id" name="host_tax_id"><br>' +
                                 '<label for="host_body_site">Host Body Site:</label>' +
                                 '<input type="text" id="host_body_site" name="host_body_site"><br>' +
                                 '<label for="accession">Accession:</label>' +
                                 '<input type="text" id="accession" name="accession"><br>' +
                                 '<label for="analysis_type">Analysis Type:</label>' +
                                 '<input type="text" id="analysis_type" name="analysis_type">';
            } else {
                form.innerHTML = '';
            }
        }
    </script>
</head>
<body>
    <h1>ENA Search Tool</h1>
    <form action="/" method="post">
        <select name="query_type" id="query_type" onchange="updateForm()">
            <option value="searchterm" selected>searchterm</option>
            <option value="keyword">Keyword</option>
        </select>
        <div id="query_form"></div>
        <button type="submit">Search</button>
    </form>
    <a href="/download">Download Results as Excel</a>
    {% if results %}
        <h2>Results:</h2>
        <pre>{{ results }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query_type = request.form.get('query_type')
        if query_type == 'searchterm':
            searchterm = request.form.get('query')
            query = f'accession="{searchterm}"'
        elif query_type == 'keyword':
            numeric_fields = ['host_tax_id']
            field_names = ['country', 'host_tax_id', 'host_body_site', 'accession', 'analysis_type']
            query_parts = [f'{field}={request.form.get(field)}' if field in numeric_fields and request.form.get(field) else f'{field}="{request.form.get(field)}"' for field in field_names if request.form.get(field)]
            query = " AND ".join(query_parts) if query_parts else ''
        else:
            query = ''

        global results
        results = search_ena(query)
        return render_template_string(HTML_TEMPLATE, results=results)
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download():
    output = pd.DataFrame(results)
    output.to_excel('results.xlsx', index=False)
    return send_file('results.xlsx', as_attachment=True)

def search_ena(query):
    base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    fields = 'sample_accession,run_accession,study_accession,read_count,sample_title'
    params = {
        "result": "read_run",
        "query": query,
        "fields": fields,
        "format": "json",
        "limit": "0"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # Parse the JSON into a Python list of dictionaries
        data = response.json()
        
        # Format the output
        results = []
        for entry in data:
            formatted_entry = f"Sample Accession: {entry['sample_accession']}, Run Accession: {entry['run_accession']}, " \
                              f"Study Accession: {entry['study_accession']}, Read Count: {entry['read_count']}, " \
                              f"Sample Title: {entry['sample_title']}"
            results.append(formatted_entry)
        return "\n".join(results)
    else:
        return f"Failed to fetch data: {response.status_code}"

if __name__ == "__main__":
    app.run(debug=True)
