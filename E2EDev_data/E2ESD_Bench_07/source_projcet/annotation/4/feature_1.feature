Feature: Display BMI ranges and corresponding categories for user reference
  The system should display a table with BMI ranges and their corresponding categories (Underweight, Ideal, Overweight, Obesity) for user reference.


  Scenario: [Normal] Verify the presence of the BMI table and its headers
    Given the user navigates to the BMI Calculator webpage
    Then the table with BMI ranges and categories should be visible
    And the table header "BMI" should be displayed with data-testid "bmi-header"
    And the table header "Category" should be displayed with data-testid "category-header"
