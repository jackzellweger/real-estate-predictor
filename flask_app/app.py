from flask import Flask, request, jsonify
import joblib
import pandas as pd
import requests
import sklearn
import numpy as np

app = Flask(__name__)
app.debug = True

errorString = None

try:
    # Load the model and preprocessor
    model = joblib.load("./model/model.joblib")
    encoder = joblib.load("./model/preprocessor.joblib")
except:
    errorString = "Model or encoder files not found."


# Define column structure & DataFrame for prediction...
df_cols = pd.DataFrame(
    columns=[
        "BOROUGH CODE",
        "GROSS SQUARE FEET",
        "LAND SQUARE FEET",
        "GROUPED CATEGORY",
        "LATITUDE",
        "LONGITUDE",
        "SALE PRICE",
    ]
)


@app.route("/")
def hello_world():
    if errorString is not None:
        return errorString

    return "Import copacetic!"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            # Get the data from the POST request
            data = request.get_json(force=True)

            # Convert to appropriate data types
            for key in data:
                if key in ["BOROUGH CODE", "GROSS SQUARE FEET", "LAND SQUARE FEET"]:
                    data[key] = int(data[key])
                elif key in ["LATITUDE", "LONGITUDE"]:
                    data[key] = float(data[key])

            # Define the actual DataFrame & put data into it
            dummy_api_df = pd.DataFrame([data], columns=df_cols.columns)

            # Transform the data using the encoder
            encoded_features = encoder.transform(dummy_api_df)

            # Delete irrelevant features & extract prediction
            encoded_features = np.delete(encoded_features, 4, axis=1)
            prediction = model.predict(encoded_features)
            prediction_price = encoder.transformers_[0][1].inverse_transform(
                [0, 0, 0, 0, prediction[0]]
            )[4]

            # Return the prediction
            return jsonify({"prediction_price": int(prediction_price)})

        except Exception as err:
            return f"{err.__class__.__name__}: {err}"

    else:
        return "This is the prediction page!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
