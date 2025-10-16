Feature: BMI Calculation
  The system calculates and displays the Body Mass Index (BMI) based on user input for height and weight, rounding the result to two decimal places.


  Scenario: [Edge] Calculate BMI with maximum reasonable height and weight inputs
    Given the BMI Calculator page is loaded
    And the user enters "272" into the height input field with data-testid "height-input"
    And the user enters "635" into the weight input field with data-testid "weight-input"
    When the user clicks the "Calculate" button with data-testid "calculate-button"
    Then the result display area with data-testid "result-display" should show "Your BMI is 85.83"
