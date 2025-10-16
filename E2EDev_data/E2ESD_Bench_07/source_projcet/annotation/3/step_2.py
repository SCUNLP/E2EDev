from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given('the BMI Calculator page is loaded')
def step_given_bmi_calculator_page_loaded(context):
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)

@given('the user enters "{height}" into the height input field with data-testid "height-input"')
def step_given_user_enters_height(context, height):
    height_input = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    height_input.clear()
    height_input.send_keys(height)
    time.sleep(1)

@given('the user enters "{weight}" into the weight input field with data-testid "weight-input"')
def step_given_user_enters_weight(context, weight):
    weight_input = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    weight_input.clear()
    weight_input.send_keys(weight)
    time.sleep(1)

@when('the user clicks the "Calculate" button with data-testid "calculate-button"')
def step_when_user_clicks_calculate_button(context):
    calculate_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='calculate-button']"))
    )
    calculate_button.click()
    time.sleep(1)

@then('the result display area with data-testid "result-display" should show "Your BMI is {expected_bmi}"')
def step_then_result_display_should_show_bmi(context, expected_bmi):
    result_display = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='result-display']"))
    )
    actual_text = result_display.text.strip()
    expected_text = f"Your BMI is {expected_bmi}"
    assert expected_text in actual_text, f"Expected '{expected_text}', but got '{actual_text}'"

def after_scenario(context, scenario):
    context.driver.quit()