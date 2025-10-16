Feature: BMI Calculation
  The system calculates and displays the Body Mass Index (BMI) based on user input for height and weight, rounding the result to two decimal places.


Scenario: [Error] Calculate BMI with empty height and weight inputs
    Given the BMI Calculator page is loaded
    And the height input field with data-testid "height-input" is empty
    And the weight input field with data-testid "weight-input" is empty
    When the user clicks the "Calculate" button with data-testid "calculate-button"
    Then the result display area with data-testid "result-display" should be NaN