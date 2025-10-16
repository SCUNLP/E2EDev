Feature: Accept and store the 'Height in cm' input value for BMI calculation
  The system should allow the user to input a height value in centimeters, validate it, and store it for BMI calculation.


  Scenario: [Error] User leaves the height field empty
    Given the BMI Calculator page is loaded
    And the 'Height in cm' input field with data-testid 'height-input' is visible
    When the user does not enter any value into the 'Height in cm' input field with data-testid 'height-input'
    Then the system should not store any value for BMI calculation
    And the 'Height in cm' input field should remain empty