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
            padding: 5px 10px;
            background-color: #0056b3; /* Dark blue background */
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 12px;
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
        #query-preview, #results {
            margin: 10px auto;
            padding: 10px;
            background-color: #eef; /* Light purple background for visibility */
            border: 1px solid #ccc;
            border-radius: 5px;
            width: 80%;
            font-size: 16px;
            text-align: left;
            overflow-x: auto; /* Enables horizontal scrolling */
            white-space: nowrap; /* Prevents text from wrapping */
        }
    </style>
</head>
<body>
    <div id="container">
        <h1>ENA Search Tool</h1>
        <div id="query-preview">Query preview will appear here.</div>
        <form action="/" method="post">
            <select name="query_type" id="query_type" onchange="updateForm()">
                <option value="keyword" selected>Keyword</option>
                <option value="search">Search</option>
            </select>
            <div id="query_form"></div>
            <input type="hidden" name="constructed_query" id="constructed_query">
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
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            updateForm();  // Initialize form on page load
        });

        let andParts = [];
        let orParts = [];

        document.querySelector('form').addEventListener('submit', function() {
            document.getElementById('constructed_query').value = document.getElementById('query-preview').textContent.replace('Query preview: ', '');
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
                `<input type="text" id="${field}" name="${field}">` +
                `<button type="button" onclick="addToQuery('${field}', document.getElementById('${field}').value, 'AND')">AND</button>` +
                `<button type="button" onclick="addToQuery('${field}', document.getElementById('${field}').value, 'OR')">OR</button>`;
            container.appendChild(inputGroup);
        }

        function addToQuery(field, value, operator) {
            if (value.trim() !== '') {
                const queryPart = `${field}="${value}"`;
                if (operator === 'AND') {
                    andParts.push(queryPart);
                } else {
                    orParts.push(queryPart);
                }
                const andString = andParts.length > 0 ? `(${andParts.join(' AND ')})` : '';
                const orString = orParts.length > 0 ? `(${orParts.join(' OR ')})` : '';
                const queryPreview = [andString, orString].filter(part => part !== '').join(' AND ');
                document.getElementById('query-preview').textContent = 'Query preview: ' + queryPreview;
                document.getElementById(field).value = ''; // Clear the input field after adding
            }
        }
    </script>
</body>
</html>
'''

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
            query = request.form.get('constructed_query')  # Use the constructed query directly

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
