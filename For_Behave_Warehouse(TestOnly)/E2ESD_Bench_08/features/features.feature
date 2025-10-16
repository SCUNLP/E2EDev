Feature: Display list of books from local storage on page load
  The system should display the list of books stored in local storage in the table body when the page loads.


  Scenario: [Edge] Display no books when local storage is empty
    Given the local storage is empty
    When the user opens the Library Management System webpage
    Then the table body with data-testid "table-body" should be empty
