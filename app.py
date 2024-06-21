from flask import Flask, request, render_template_string
import requests

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
            var queryValue = select.value; // Directly get the selected option's value
            var form = document.getElementById('query_form');

            if (queryValue === 'sequence') {
                form.innerHTML = '<label for="query">Enter your sequence:</label>' +
                                 '<input type="text" id="query" name="query" required>';
            } else if (queryValue === 'keyword') {
                form.innerHTML = '<label for="country">Country:</label>' +
                                 '<input type="text" id="country" name="country" required><br>' +
                                 '<label for="tax_id">Host Tax ID:</label>' +
                                 '<input type="text" id="tax_id" name="tax_id" required><br>' +
                                 '<label for="body_site">Body Site:</label>' +
                                 '<input type="text" id="body_site" name="body_site" required>';
            } else {
                form.innerHTML = ''; // Clear the form if no valid option is selected
            }
        }
    </script>
</head>
<body>
    <h1>ENA Search Tool</h1>
    <form action="/" method="post">
        <select name="query_type" id="query_type" onchange="updateForm()">
            <option value="sequence" selected>Sequence</option>
            <option value="keyword">Keyword</option>
        </select>
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
        query_type = request.form.get('query_type')

        if query_type == 'sequence':
            sequence = request.form.get('query')
            query = f'accession="{sequence}"'
        elif query_type == 'keyword':
            country = request.form.get('country')
            tax_id = request.form.get('tax_id')
            body_site = request.form.get('body_site')
            query = f'country="{country}" AND host_tax_id="{tax_id}" AND host_body_site="{body_site}"'
        else:
            query = ''

        results = search_ena(query)
        return render_template_string(HTML_TEMPLATE, results=results)
    return render_template_string(HTML_TEMPLATE, results=None)

def search_ena(query):
    base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
    fields = 'sample_accession,run_accession,study_accession,read_count,sample_title'
    result_type = "read_run"
    format_type = "json"
    params = {
        "result": result_type,
        "query": query,
        "fields": fields,
        "format": format_type,
        "limit": "0"
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.text  # Return raw JSON text or parse it if needed
    else:
        return f"Failed to fetch data: {response.status_code}"

if __name__ == "__main__":
    app.run(debug=True)
