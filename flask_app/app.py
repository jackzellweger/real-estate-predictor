from flask import Flask, request, jsonify
import joblib
import pandas as pd
import requests

app = Flask(__name__)

# Load the model and preprocessor
model = joblib.load("./model/model.joblib")
encoder = joblib.load("./model/preprocessor.joblib")


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            # Get the data from the POST request
            data = request.get_json(force=True)

            # Convert the data to a DataFrame
            df = pd.DataFrame([data])  # Wrap the data in another list

            # print(df.to_string())

            # One-hot encode the categorical features
            encoded_features = encoder.transform(
                df[["BOROUGH CODE", "GROUPED CATEGORY"]]
            )
            processed_data = encoded_features

            # Combine the numerical and encoded categorical features
            processed_data = np.concatenate(
                [
                    df[
                        [
                            "GROSS SQUARE FEET",
                            "LAND SQUARE FEET",
                            "LATITUDE",
                            "LONGITUDE",
                            "SALE PRICE",  # FIXME: Is sale price necessary?
                        ]
                    ].values,
                    encoded_features,
                ],
                axis=1,
            )

            # Make prediction using model
            prediction = model.predict(processed_data)

            # Return the prediction
            return jsonify({"prediction": prediction[0]})

        except Exception as err:
            return f"{err.__class__.__name__}: {err}"

    else:
        return "This is the prediction page!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
