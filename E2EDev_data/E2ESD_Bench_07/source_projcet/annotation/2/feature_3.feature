Feature: Accept and store the weight input for BMI calculation
  The system should allow the user to input a weight value in kilograms, validate it, and store it for BMI calculation.


  Scenario: [Edge] User enters the maximum valid weight value
    Given the BMI Calculator page is loaded
    And the "Weight in kg" input field with data-testid "weight-input" is visible
    When the user enters "500" into the "Weight in kg" input field with data-testid "weight-input"
    Then the "Weight in kg" input field with data-testid "weight-input" should display the value "500"
