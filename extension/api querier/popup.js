document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("send").addEventListener("click", function () {
    var borough_code = document.getElementById("borough_code").value;
    var grouped_category = document.getElementById("grouped_category").value;
    var gross_square_feet = document.getElementById("gross_square_feet").value;
    var land_square_feet = document.getElementById("land_square_feet").value;
    var latitude = document.getElementById("latitude").value;
    var longitude = document.getElementById("longitude").value;

    var data = {
      "BOROUGH CODE": borough_code,
      "GROUPED CATEGORY": grouped_category,
      "GROSS SQUARE FEET": gross_square_feet,
      "LAND SQUARE FEET": land_square_feet,
      "LATITUDE": latitude,
      "LONGITUDE": longitude,
    };

    fetch('http://localhost:8080/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(response => response.json())
      .then(response => document.getElementById('response').textContent = JSON.stringify(response))
      .catch(err => document.getElementById('response').textContent = err);
  });
});
