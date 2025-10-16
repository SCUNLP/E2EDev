from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Placeholder for the file path
file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given('the BMI Calculator page is loaded')
def step_impl_bmi_calculator_page_loaded(context):
    # Initialize the WebDriver
    context.driver = webdriver.Chrome()
    # Load the test page
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    # Maximize the browser window
    context.driver.maximize_window()
    time.sleep(1)  # Allow the page to load completely

@given('the "Weight in kg" input field with data-testid "weight-input" is visible')
def step_impl_weight_input_field_visible(context):
    # Wait for the "Weight in kg" input field to be visible
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    time.sleep(1)

@when('the user enters "70" into the "Weight in kg" input field with data-testid "weight-input"')
def step_impl_user_enters_weight(context):
    # Locate the "Weight in kg" input field
    weight_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='weight-input']")
    # Clear any existing value and enter "70"
    weight_input.clear()
    weight_input.send_keys("70")
    time.sleep(1)

@then('the "Weight in kg" input field with data-testid "weight-input" should display the value "70"')
def step_impl_weight_input_field_displays_value(context):
    # Locate the "Weight in kg" input field
    weight_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='weight-input']")
    # Verify that the input field displays the value "70"
    assert weight_input.get_attribute("value") == "70", f"Expected value '70', but got '{weight_input.get_attribute('value')}'"
    time.sleep(1)

# Teardown to close the browser after the test
def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()