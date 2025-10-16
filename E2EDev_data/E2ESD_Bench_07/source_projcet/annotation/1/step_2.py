from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given('the BMI Calculator page is loaded')
def step_impl(context):
    # Initialize the WebDriver and load the test page
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    context.driver.maximize_window()
    time.sleep(1)  # Allow the page to load completely

@given("the 'Height in cm' input field with data-testid 'height-input' is visible")
def step_impl(context):
    # Wait for the 'Height in cm' input field to be visible
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    time.sleep(1)

@when("the user enters \"1\" into the 'Height in cm' input field with data-testid 'height-input'")
def step_impl(context):
    # Locate the 'Height in cm' input field and enter the value "1"
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    height_input.clear()
    height_input.send_keys("1")
    time.sleep(1)

@then('the system should store the value "1" for BMI calculation')
def step_impl(context):
    # Verify that the value "1" is stored in the 'Height in cm' input field
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    stored_value = height_input.get_attribute("value")
    assert stored_value == "1", f"Expected stored value to be '1', but got '{stored_value}'"
    time.sleep(1)

@then("the 'Height in cm' input field should display \"1\"")
def step_impl(context):
    # Verify that the 'Height in cm' input field displays the value "1"
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    displayed_value = height_input.get_attribute("value")
    assert displayed_value == "1", f"Expected displayed value to be '1', but got '{displayed_value}'"
    time.sleep(1)

# Teardown to close the browser after the test
def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()