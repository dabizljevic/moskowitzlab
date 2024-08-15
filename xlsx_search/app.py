from flask import Flask, request, render_template, flash, send_file
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# CHANGE DIRECTORY HERE!!
SEARCH_DIRECTORY = '/Users/sdabiz/Desktop/work/2024summer/moskowitzlab/xlsx_search/sample_directory'
RESULTS_FOLDER = 'results'
app.config['SEARCH_DIRECTORY'] = SEARCH_DIRECTORY
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

# results directory
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_strings = request.form.getlist('search_strings[]')
        results_set = set()  # set stops duplicates

        # iterates through directory
        for filename in os.listdir(app.config['SEARCH_DIRECTORY']):
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                filepath = os.path.join(app.config['SEARCH_DIRECTORY'], filename)

                try:
                    df = pd.read_excel(filepath)

                    # find 'Experiment description' column
                    if 'Experiment description' not in df.columns:
                        flash(f'No "Experiment description" column found in {filename}')
                        continue

                    # string searching
                    for search_string in search_strings:
                        matches = df[df['Experiment description'].astype(str).str.contains(search_string, na=False, case=False)]
                        if not matches.empty:
                            for _, row in matches.iterrows():
                                results_set.add((filename, row['Experiment description']))

                except Exception as e:
                    flash(f'Error processing file {filename}: {str(e)}')
                    continue

        results = list(results_set) #set to list

        # creates output excel using pandas
        output_filepath = None
        if results:
            output_filepath = os.path.join(app.config['RESULTS_FOLDER'], 'search_results.xlsx')
            results_df = pd.DataFrame(results, columns=['File Name', 'Experiment Description'])
            results_df.to_excel(output_filepath, index=False)

        if results:
            return render_template('index.html', results=results, output_file=output_filepath)
        else:
            flash('No matches found')
            return render_template('index.html')

    return render_template('index.html')

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
