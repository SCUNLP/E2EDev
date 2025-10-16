Feature: Display BMI ranges and corresponding categories for user reference
  The system should display a table with BMI ranges and their corresponding categories (Underweight, Ideal, Overweight, Obesity) for user reference.


  Scenario: [Normal] Verify the BMI range and category values in the table
    Given the user navigates to the BMI Calculator webpage
    Then the table should contain the BMI range "less than 18.5" with data-testid "bmi-value-1"
    And the corresponding category "Underweight" should be displayed with data-testid "category-value-1"
    And the table should contain the BMI range "between 18.5 and 24.9" with data-testid "bmi-value-2"
    And the corresponding category "Ideal" should be displayed with data-testid "category-value-2"
    And the table should contain the BMI range "between 25 and 29.9" with data-testid "bmi-value-3"
    And the corresponding category "Overweight" should be displayed with data-testid "category-value-3"
    And the table should contain the BMI range "over 30" with data-testid "bmi-value-4"
    And the corresponding category "Obesity" should be displayed with data-testid "category-value-4"
