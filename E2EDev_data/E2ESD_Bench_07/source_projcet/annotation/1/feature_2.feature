Feature: Accept and store the 'Height in cm' input value for BMI calculation
  The system should allow the user to input a height value in centimeters, validate it, and store it for BMI calculation.


  Scenario: [Edge] User enters the minimum valid height value
    Given the BMI Calculator page is loaded
    And the 'Height in cm' input field with data-testid 'height-input' is visible
    When the user enters "1" into the 'Height in cm' input field with data-testid 'height-input'
    Then the system should store the value "1" for BMI calculation
    And the 'Height in cm' input field should display "1"
