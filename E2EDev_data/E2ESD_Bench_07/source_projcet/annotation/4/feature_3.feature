Feature: Display BMI ranges and corresponding categories for user reference
  The system should display a table with BMI ranges and their corresponding categories (Underweight, Ideal, Overweight, Obesity) for user reference.


  Scenario: [Edge] Verify table visibility on different screen sizes
    Given the user navigates to the BMI Calculator webpage
    When the user resizes the browser window to a small screen size
    Then the table with BMI ranges and categories should remain visible and properly formatted
