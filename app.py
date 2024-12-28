import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from groq import Groq

# Initialize Flask app
app = Flask(__name__)

# Folder to temporarily save uploaded files
UPLOAD_FOLDER = "upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def home():
    return render_template('midindex.html')

# Initialize Groq client
client = Groq(api_key="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")

@app.route('/process-location', methods=['POST'])
def process_location():
    try:
        # Get the selected block value from the request (sent as JSON)
        data = request.get_json()
        selected_block = data.get('selectedBlock')
        if not selected_block:
            return jsonify({"error": "No block selected."}), 400

        # Load the Excel sheet and find corresponding data
        excel_path = os.path.join(UPLOAD_FOLDER, 'dataset.xlsx')  # Update path to your dataset
        data = pd.read_excel(excel_path)

        # Filter data for the selected block
        block_data = data[data['Block'] == selected_block]
        if block_data.empty:
            return jsonify({"error": f"No data found for block '{selected_block}'."}), 404
	grok_input = {
        "normal_rainfall": block_data['Normal_Rainfall'].values[0],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[1],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[2],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[3],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[4],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[5],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[6],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[7],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[8],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[9],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[10],
	    "normal_rainfall": block_data['Normal_Rainfall'].values[11],
        "actual_rainfall": block_data['Actual_Rainfall'].values[0],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[1],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[2],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[3],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[4],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[5],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[6],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[7],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[8],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[9],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[10],
	    "actual_rainfall": block_data['Normal_Rainfall'].values[11],
        "deviation": block_data['Deviation'].values[0],
	    "deviation": block_data['Deviation'].values[1],
	    "deviation": block_data['Deviation'].values[2],
	    "deviation": block_data['Deviation'].values[3],
	    "deviation": block_data['Deviation'].values[4],
	    "deviation": block_data['Deviation'].values[5],
	    "deviation": block_data['Deviation'].values[6],
	    "deviation": block_data['Deviation'].values[7],
	    "deviation": block_data['Deviation'].values[8],
	    "deviation": block_data['Deviation'].values[9],
	    "deviation": block_data['Deviation'].values[10],
	    "deviation": block_data['Deviation'].values[11],
        }
	chat_completion = client.chat.completions.create(
            messages=[grok_input],
            model="llama3-8b-8192",
        )
	prediction = chat_completion.choices[0].message.content
	# Save the prediction to a new Excel sheet
        output_path = os.path.join(OUTPUT_FOLDER, 'results.xlsx')
        block_data['Prediction'] = prediction
        block_data.to_excel(output_path, index=False)

        # Return success response
        return jsonify({"message": "Prediction generated successfully.", "prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def results():
    try:
        # Load the results Excel sheet
        output_path = os.path.join(OUTPUT_FOLDER, 'results.xlsx')
        results_data = pd.read_excel(output_path)

        # Render results in HTML
        return "<h1>Flood Prediction Results</h1>" + results_data.to_html(index=False, classes='table table-bordered')

    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    app.run(debug=True)
