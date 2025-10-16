from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Placeholder for the file path
file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

# Background setup
@given("the user navigates to the BMI Calculator webpage")
def step_given_user_navigates_to_bmi_calculator(context):
    # Initialize the Selenium WebDriver
    context.driver = webdriver.Chrome()
    # Load the test page dynamically
    context.driver.get(f"file://{file_path}")
    # Maximize the browser window
    context.driver.maximize_window()
    time.sleep(1)  # Allow the page to load completely

@then("the table with BMI ranges and categories should be visible")
def step_then_table_with_bmi_ranges_visible(context):
    # Wait for the table to be visible
    table = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "table"))
    )
    assert table.is_displayed(), "BMI table is not visible"

@then('the table header "BMI" should be displayed with data-testid "bmi-header"')
def step_then_bmi_header_displayed(context):
    # Locate the BMI header using data-testid
    bmi_header = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='bmi-header']"))
    )
    assert bmi_header.is_displayed(), '"BMI" header is not visible'
    assert "BMI".lower() in bmi_header.text.strip().lower(), f'Expected "BMI" in header, but got "{bmi_header.text.strip()}"'

@then('the table header "Category" should be displayed with data-testid "category-header"')
def step_then_category_header_displayed(context):
    # Locate the Category header using data-testid
    category_header = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='category-header']"))
    )
    assert category_header.is_displayed(), '"Category" header is not visible'
    assert "Category".lower() in category_header.text.strip().lower(), f'Expected "Category" in header, but got "{category_header.text.strip()}"'

# Teardown
def after_scenario(context, scenario):
    # Close the browser driver after the test
    if hasattr(context, "driver"):
        context.driver.quit()