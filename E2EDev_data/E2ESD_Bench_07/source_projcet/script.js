document.querySelector("[data-testid='calculate-button']").addEventListener("click", function() {
  var height_val = document.querySelector("[data-testid='height-input']").value; // in cm
  var weight_val = document.querySelector("[data-testid='weight-input']").value; // in kg

  // Convert height from cm to m
  var height_in_m = height_val / 100;

  // Calculate BMI
  var bmi = weight_val / (height_in_m * height_in_m);

  // Round BMI to 2 decimal places
  var bmio = bmi.toFixed(2);

  document.querySelector("[data-testid='result-display']").innerHTML = "Your BMI is " + bmio;
});
