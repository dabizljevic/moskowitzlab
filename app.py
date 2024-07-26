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
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh; /* Full viewport height */
        }
        #container {
            text-align: center;
            width: 80%; /* Manageable width */
            background-color: #ffffff; /* White background for the form area */
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1); /* Subtle shadow */
            margin-top: 20px; /* Adds space at the top */
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
            text-decoration: none;
            color: #0056b3; /* Stylish blue link */
        }
        .form-section {
            display: flex;
            justify-content: center;
            flex-wrap: wrap; /* Ensures wrapping on small screens */
        }
        .input-group {
            margin-bottom: 10px;
        }
        label, input {
            display: block;
            margin: 0 auto;
            margin-bottom: 5px;
        }
        input {
            min-width: 180px; /* Ensures the input box is not too small */
        }
        h1 {
            margin-bottom: 20px;
        }
        /* Styles for the + and - buttons */
        .input-group button {
            padding: 5px 8px; /* Smaller padding */
            font-size: 12px; /* Smaller font size */
            margin: 0 5px; /* Less margin for tighter spacing */
            width: 30px; /* Fixed width */
            height: 30px; /* Fixed height */
            line-height: 12px; /* Adjust line height to center the text */
        }
        #results {
            text-align: left; /* Aligns results text to the left */
            width: 80%; /* Width relative to the container size */
            margin-top: 20px; /* Space above the results */
            padding: 10px;
            background-color: #eef; /* Lighter shade for visibility */
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1); /* Subtle shadow for results */
            overflow: auto; /* Adds scrollbar if content is too long */
        }
    </style>
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
    </div>
    {% if results %}
        <div id="results">
            <h2>Results:</h2>
            <pre>{{ results }}</pre>
        </div>
    {% endif %}
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
                                 '<input type="text" id="search" name="search">';
            } else if (queryValue === 'keyword') {
                form.innerHTML = '<div class="form-section" id="keyword_form"></div>';
                ['accession', 'allele', 'analysis_type', 'base_count', 'breed', 'cell_line', 'cell_type', 'country', 'description', 'gene', 'host', 'host_body_site', 'host_common_name', 'host_genotype', 'host_sex', 'sample_title'].forEach(field => {
                    addKeywordInput(field);
                });
            } else {
                form.innerHTML = '';
            }
        }

        function addKeywordInput(field) {
            var container = document.getElementById('keyword_form');
            var inputGroup = document.createElement('div');
            inputGroup.className = 'input-group';
            inputGroup.innerHTML = 
                `<label for="${field}">${field.replace(/_/g, ' ').charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')}:</label>` +
                `<input type="text" name="${field}">`;
            container.appendChild(inputGroup);

            var addButton = document.createElement('button');
            addButton.type = 'button';
            addButton.onclick = () => addKeywordInput(field);
            addButton.textContent = '+';  // Changed button text to "+"
            inputGroup.appendChild(addButton);

            var removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.onclick = function() { removeInput(this); };
            removeButton.textContent = '-';  // Changed button text to "-"
            inputGroup.appendChild(removeButton);
        }

        function removeInput(button) {
            var group = button.parentNode;
            group.parentNode.removeChild(group);
        }
    </script>
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
                # Construct query part for each word, ensuring each word is individually considered for all fields
                part = f'(country="{word}" OR host_body_site="{word}" OR description="{word}" OR sample_title="{word}")'
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
            query_parts = []
            for field in field_names:
                field_values = request.form.getlist(field)
                for value in field_values:
                    if value:
                        if field in numeric_fields:
                            query_parts.append(f'{field}={value}')
                        else:
                            query_parts.append(f'{field}="{value}"')
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


