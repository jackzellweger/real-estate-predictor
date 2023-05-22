from flask import Flask, request, jsonify
import joblib
import pandas as pd
import requests

app = Flask(__name__)

# Load the model and preprocessor
model = joblib.load('./model/model.joblib')
preprocessor = joblib.load('./model/preprocessor.joblib')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            data = request.get_json(force=True)

            # Preprocess the data
            processed_data = preprocessor.transform([data])

            # Make prediction using model
            prediction = model.predict(processed_data)

            # Depending on the model used, you may want to transform the prediction back to the original domain
            # prediction = scaler_target.inverse_transform(prediction)

            # Return the prediction
            return jsonify(prediction.tolist())
        except Exception as err:
            return f"{err.__class__.__name__}: {err}"
    else:
        return "This is the prediction page!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)