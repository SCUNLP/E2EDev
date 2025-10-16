Feature: Accept and store the 'Height in cm' input value for BMI calculation
  The system should allow the user to input a height value in centimeters, validate it, and store it for BMI calculation.


  Scenario: [Error] User enters a non-numeric value in the height field
    Given the BMI Calculator page is loaded
    And the 'Height in cm' input field with data-testid 'height-input' is visible
    When the user enters "abc" into the 'Height in cm' input field with data-testid 'height-input'
    Then the system should not store the value "abc" for BMI calculation

