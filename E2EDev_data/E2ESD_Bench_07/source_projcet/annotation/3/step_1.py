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
    # Wait for the page to fully load
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='calculate-button']"))
    )

@given('the user enters "{height}" into the height input field with data-testid "height-input"')
def step_impl(context, height):
    # Locate the height input field and enter the provided height value
    height_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    height_input.clear()
    height_input.send_keys(height)
    time.sleep(1)

@given('the user enters "{weight}" into the weight input field with data-testid "weight-input"')
def step_impl(context, weight):
    # Locate the weight input field and enter the provided weight value
    weight_input = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    weight_input.clear()
    weight_input.send_keys(weight)
    time.sleep(1)

@when('the user clicks the "Calculate" button with data-testid "calculate-button"')
def step_impl(context):
    # Locate the calculate button and click it
    calculate_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='calculate-button']"))
    )
    calculate_button.click()
    time.sleep(1)

@then('the result display area with data-testid "result-display" should show "{expected_result}"')
def step_impl(context, expected_result):
    # Locate the result display area and verify the displayed text
    result_display = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result-display']"))
    )
    actual_result = result_display.text.strip()
    assert expected_result in actual_result, f"Expected '{expected_result}', but got '{actual_result}'"

# Teardown to close the browser after the test
def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()