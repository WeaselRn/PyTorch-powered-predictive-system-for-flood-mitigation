import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from groq import Groq

# Initialize Flask app
app = Flask(__name__)

# Folder to temporarily save uploaded files
UPLOAD_FOLDER = "upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Groq client
client = Groq(api_key="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")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract input data from the request
        data = request.json
        normal_rainfall = float(data['normal_rainfall'])
        actual_rainfall = float(data['actual_rainfall'])
        deviation = float(data['deviation'])

        # Use Groq client to get predictions
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Predict flood risk with normal rainfall {normal_rainfall}, actual rainfall {actual_rainfall}, and deviation {deviation}"
                }
            ],
            model="llama3-8b-8192",
        )

        prediction = chat_completion.choices[0].message.content

        return jsonify({"prediction": prediction})  # Send the prediction back to the frontend
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the request", "details": str(e)}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save the uploaded file
        file_path = os.path.join(app.config[upload], dataset_idukki.xlsx)
        file.save(file_path)

        # Read the Excel file
        data = pd.read_excel(file_path)

        # Extract relevant columns (update column names as needed)
        relevant_data = data[['Normal (mm)', 'Actual (mm)', 'Deviation %']]

        # Prepare predictions using Groq API
        predictions = []
        for _, row in relevant_data.iterrows():
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

        # Add predictions to the original data
        data['Flood_Risk_Prediction'] = predictions

        # Save the updated file with predictions
        output_path = os.path.join(app.config[upload], "predictions_with_data.xlsx")
        data.to_excel(output_path, index=False)

        return jsonify({"message": "File processed successfully", "output_file": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
