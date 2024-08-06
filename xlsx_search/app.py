from flask import Flask, request, render_template, flash, send_file
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file 
        if 'file' not in request.files:
            flash('No file')
            return render_template('index.html')

        files = request.files.getlist('file')
        search_string = request.form['search_string']

        if not files or files[0].filename == '':
            flash('No selected files')
            return render_template('index.html')

        results = []

        # read through all files 
        for file in files:
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                try:
                    df = pd.read_excel(filepath)

                    # check for 'Experiment description' column 
                    if 'Experiment description' not in df.columns:
                        flash(f'No "Experiment description" column found in {file.filename}')
                        continue

                    matches = df[df['Experiment description'].astype(str).str.contains(search_string, na=False, case=False)]

                    if not matches.empty:
                        for _, row in matches.iterrows():
                            results.append((file.filename, row['Experiment description']))

                except Exception as e:
                    flash(f'Error processing file {file.filename}: {str(e)}')
                    continue

        # create an output Excel file
        output_filepath = None
        if results:
            output_filepath = os.path.join(app.config['RESULTS_FOLDER'], 'search_results.xlsx')
            # Create a DataFrame from the results
            results_df = pd.DataFrame(results, columns=['File Name', 'Experiment Description'])
            # Write the results DataFrame to an Excel file
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
