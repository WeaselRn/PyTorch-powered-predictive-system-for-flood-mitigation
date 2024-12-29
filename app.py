import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from groq import Groq

# Initialize Flask app
app = Flask(__name__)

# Folder to temporarily save uploaded files
UPLOAD_FOLDER = "upload"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/home2')
def middle():
    return render_template('middlepage.html')

# Initialize Groq client
client = Groq(api_key="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")

@app.route('/process-location', methods=['POST'])
def process_location():
    try:
        # Get the selected block value from the request (sent as JSON)
        data = request.get_json()
        selected_location = data.get('selectedLocation')
        selected_block = data.get('selectedBlock')
        if not selected_block:
            return jsonify({"error": "No block selected."}), 400

        # Load the Excel sheet and find corresponding data
        excel_path = os.path.join(UPLOAD_FOLDER, 'dataset.xlsx')  # Update path to your dataset
        data = pd.read_excel("C:/Users/Robin/Desktop/H4G/RainNet/upload/dataset.xlsx")
        if selected_block == data['Block'] :
            relevant_data = data[['Normal (mm)', 'Actual (mm)', 'Deviation %']]
        
        # Prepare predictions using Groq API
        predictions = []
        for row in relevant_data.iterrows():
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Predict flood risk with normal rainfall {row['Normal (mm)']}, actual rainfall {row['Actual (mm)']}, and deviation {row['Deviation %']}"
                    }
                ],
                model="llama3-8b-8192",
            )
            prediction = chat_completion.choices[0].message.content
            predictions.append(prediction)

    except Exception as e:
        return jsonify({"error": "An error occurred while processing the request", "details": str(e)}), 400
    # Save the prediction to a new Excel sheet
    output_path = os.path.join(OUTPUT_FOLDER, 'results.xlsx')
    block_data['Prediction'] = predictions
    block_data.to_excel(output_path, index=False)

    # Return success response
    return jsonify({"message": "Prediction generated successfully.", "prediction": prediction})

    

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
