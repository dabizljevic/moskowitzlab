from flask import Flask, request, render_template_string, send_file
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
    <style>
        body {
            background-color: #f0f8ff; /* Light blue background */
            font-family: Arial, sans-serif;
        }
        #container {
            text-align: center;
            margin-top: 50px;
        }
        select, input, button, a {
            margin: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: #0056b3; /* Dark blue background */
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #003d7a; /* Darker blue when hovered */
        }
        a {
            display: block; /* Makes the link block to take new line */
            margin-top: 20px; /* Extra space from the form */
        }
        .form-section {
            display: flex;
            justify-content: center;
        }
        .column {
            margin: 10px;
        }
        label, input {
            display: block;
            margin: 0 auto;
            margin-bottom: 10px;
        }
        input {
            min-width: 200px; /* Ensures the input box is not too small */
        }
        #results {
            text-align: left; /* Aligns results text to the left */
            width: 90%; /* Sets a max width for better readability */
            margin: 20px auto; /* Centers the results container */
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            updateForm();  // Initialize form on page load
        });

        function updateForm() {
            var select = document.getElementById('query_type');
            var queryValue = select.value;
            var form = document.getElementById('query_form');

            if (queryValue === 'search') {
                form.innerHTML = '<label for="search">Enter your search term:</label>' +
                                 '<input type="text" id="search" name="search" required>';
            } else if (queryValue === 'keyword') {
                form.innerHTML = '<div class="form-section">' +
                                    '<div class="column">' +
                                        '<label for="accession">Accession:</label>' +
                                        '<input type="text" id="accession" name="accession">' +
                                        '<label for="allele">Allele:</label>' +
                                        '<input type="text" id="allele" name="allele">' +
                                        '<label for="analysis_type">Analysis Type:</label>' +
                                        '<input type="text" id="analysis_type" name="analysis_type">' +
                                        '<label for="base_count">Base Count:</label>' +
                                        '<input type="text" id="base_count" name="base_count">' +
                                        '<label for="breed">Breed:</label>' +
                                        '<input type="text" id="breed" name="breed">' +
                                        '<label for="cell_line">Cell Line:</label>' +
                                        '<input type="text" id="cell_line" name="cell_line">' +
                                        '<label for="cell_type">Cell Type:</label>' +
                                        '<input type="text" id="cell_type" name="cell_type">' +
                                    '</div>' +
                                    '<div class="column">' +
                                        '<label for="country">Country:</label>' +
                                        '<input type="text" id="country" name="country">' +
                                        '<label for="description">Description:</label>' +
                                        '<input type="text" id="description" name="description">' +
                                        '<label for="gene">Gene:</label>' +
                                        '<input type="text" id="gene" name="gene">' +
                                        '<label for="host">Host:</label>' +
                                        '<input type="text" id="host" name="host">' +
                                        '<label for="host_body_site">Host Body Site:</label>' +
                                        '<input type="text" id="host_body_site" name="host_body_site">' +
                                        '<label for="host_common_name">Host Common Name:</label>' +
                                        '<input type="text" id="host_common_name" name="host_common_name">' +
                                        '<label for="host_genotype">Host Genotype:</label>' +
                                        '<input type="text" id="host_genotype" name="host_genotype">' +
                                    '</div>' +
                                    '<div class="column">' +
                                        '<label for="host_sex">Host Sex:</label>' +
                                        '<input type="text" id="host_sex" name="host_sex">' +
                                        '<label for="host_tax_id">Host Tax ID:</label>' +
                                        '<input type="text" id="host_tax_id" name="host_tax_id">' +
                                        '<label for="sample_title">Sample Title:</label>' +
                                        '<input type="text" id="sample_title" name="sample_title">' +
                                    '</div>' +
                                 '</div>';
            } else {
                form.innerHTML = '';
            }
        }
    </script>
</head>
<body>
    <div id="container">
        <h1>ENA Search Tool</h1>
        <form action="/" method="post">
            <select name="query_type" id="query_type" onchange="updateForm()">
                <option value="keyword" selected>Keyword</option>
                <option value="search">Search</option>
            </select>
            <div id="query_form"></div>
            <button type="submit">Search</button>
        </form>
        <a href="/download">Download Results as Excel</a>
        {% if results %}
            <div id="results">
                <h2>Results:</h2>
                <pre>{{ results }}</pre>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''



results = []
#description="{search}" OR title="{search}" OR gene="{search}" OR keywords="{search}" OR sample_title="{search}" OR scientific_name="{search}" OR host="{search}" OR environment_biome="{search}" OR environment_feature="{search}" OR environment_material="{search}" OR study_title="{search}" OR experiment_title="{search}" OR analysis_title="{search}" OR 

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query_type = request.form.get('query_type')

        if query_type == 'search':
            search = request.form.get('search')
            search_words = search.split()  # Split the search string into words
            queries = []
            for word in search_words:
                # Construct query part for each word
                part = f'(country="{word}" OR host_body_site="{word}" OR description="{search}")'
                queries.append(part)
            query = ' AND '.join(queries)  # Combine all parts with AND

        elif query_type == 'keyword':
            numeric_fields = ['host_tax_id', 'base_count']
            field_names = [
                'country', 'host_tax_id', 'host_body_site', 'accession', 'analysis_type',
                'allele', 'base_count', 'breed', 'cell_line', 'cell_type', 'collected_by',
                'collection_date', 'country', 'environment_biome', 'experiment', 'gene',
                'geo_accession', 'host', 'host_body_site', 'host_common_name', 'host_genotype',
                'host_phenotype', 'host_scientific_name', 'host_sex', 'host_tax_id',
                'sample_accession', 'sample_title'
            ]
            query_parts = [f'{field}={request.form.get(field)}' if field in numeric_fields and request.form.get(field) else f'{field}="{request.form.get(field)}"' for field in field_names if request.form.get(field)]
            query = " AND ".join(query_parts) if query_parts else ''

        else:
            query = ''

        print(query)
        global results
        results = search_ena(query)
        return render_template_string(HTML_TEMPLATE, results=results[0])
    return render_template_string(HTML_TEMPLATE)


@app.route('/download')
def download():
    if not results[1]:  # Check if results are empty
        return "No data to download", 404
    
    output = pd.DataFrame(results[1])
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
        data = response.json()
        formatted_results = []
        raw_data = []
        for entry in data:
            formatted_entry = f"Sample Accession: {entry['sample_accession']}, Run Accession: {entry['run_accession']}, " \
                              f"Study Accession: {entry['study_accession']}, Read Count: {entry['read_count']}, " \
                              f"Sample Title: {entry['sample_title']}"
            formatted_results.append(formatted_entry)
        return "\n".join(formatted_results), data
    else:
        return [], []  # Return empty lists if the request fails


if __name__ == "__main__":
    app.run(debug=True)
