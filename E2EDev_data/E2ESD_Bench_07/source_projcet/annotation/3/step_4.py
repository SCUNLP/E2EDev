from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Placeholder for the file path
file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given("the BMI Calculator page is loaded")
def step_given_bmi_calculator_page_loaded(context):
    # Initialize the WebDriver
    context.driver = webdriver.Chrome()
    # Load the test page
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    # Maximize the browser window
    context.driver.maximize_window()
    # Wait for the page title to be visible
    WebDriverWait(context.driver, 10).until(EC.title_is("BMI Calculator"))
    time.sleep(1)

@given('the user enters "{height}" into the height input field with data-testid "height-input"')
def step_given_user_enters_height(context, height):
    # Locate the height input field and enter the value
    height_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    height_input.clear()
    height_input.send_keys(height)
    time.sleep(1)

@given('the user enters "{weight}" into the weight input field with data-testid "weight-input"')
def step_given_user_enters_weight(context, weight):
    # Locate the weight input field and enter the value
    weight_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    weight_input.clear()
    weight_input.send_keys(weight)
    time.sleep(1)

@when('the user clicks the "Calculate" button with data-testid "calculate-button"')
def step_when_user_clicks_calculate_button(context):
    # Locate the calculate button and click it
    calculate_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='calculate-button']"))
    )
    calculate_button.click()
    time.sleep(1)

@then('the result display area with data-testid "result-display" should be NaN')
def step_then_result_display_should_be_nan(context):
    # Locate the result display area and verify the text
    result_display = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result-display']"))
    )
    result_text = result_display.text.strip()
    assert "NaN" in result_text, f"Expected 'NaN' in result display, but got '{result_text}'"
    time.sleep(1)

# Cleanup after the test
def after_scenario(context, scenario):
    # Close the browser driver
    if hasattr(context, 'driver'):
        context.driver.quit()