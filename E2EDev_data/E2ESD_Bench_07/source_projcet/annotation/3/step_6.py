from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

def is_visible(element):
    return element.is_displayed()

@given('the BMI Calculator page is loaded')
def step_given_bmi_calculator_page_loaded(context):
    # Initialize the WebDriver and load the test page
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)  # Allow the page to load completely

@given('the height input field with data-testid "height-input" is empty')
def step_given_height_input_empty(context):
    # Locate the height input field and ensure it is empty
    height_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    height_input.clear()
    assert height_input.get_attribute("value") == "", "Height input field is not empty"
    time.sleep(1)

@given('the weight input field with data-testid "weight-input" is empty')
def step_given_weight_input_empty(context):
    # Locate the weight input field and ensure it is empty
    weight_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    weight_input.clear()
    assert weight_input.get_attribute("value") == "", "Weight input field is not empty"
    time.sleep(1)

@when('the user clicks the "Calculate" button with data-testid "calculate-button"')
def step_when_user_clicks_calculate_button(context):
    # Locate the calculate button and click it
    calculate_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='calculate-button']"))
    )
    calculate_button.click()
    time.sleep(1)  # Allow time for the result to be displayed

@then('the result display area with data-testid "result-display" should be NaN')
def step_then_result_display_nan(context):
    # Locate the result display area and verify its content
    result_display = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result-display']"))
    )
    assert "NaN" in result_display.text, f"Expected 'NaN' in result display, but got '{result_display.text}'"
    time.sleep(1)

# Teardown to close the browser after the test
def after_scenario(context, scenario):
    context.driver.quit()