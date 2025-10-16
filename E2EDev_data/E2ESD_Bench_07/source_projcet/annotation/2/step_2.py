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
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)

@given('the "Weight in kg" input field with data-testid "weight-input" is visible')
def step_given_weight_input_field_visible(context):
    weight_input = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='weight-input']"))
    )
    assert is_visible(weight_input), "Weight input field is not visible"
    time.sleep(1)

@when('the user enters "0.1" into the "Weight in kg" input field with data-testid "weight-input"')
def step_when_user_enters_weight(context):
    weight_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='weight-input']")
    weight_input.clear()
    weight_input.send_keys("0.1")
    time.sleep(1)

@then('the "Weight in kg" input field with data-testid "weight-input" should display the value "0.1"')
def step_then_weight_input_field_should_display_value(context):
    weight_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='weight-input']")
    assert weight_input.get_attribute("value") == "0.1", f"Expected value '0.1', but got '{weight_input.get_attribute('value')}'"
    time.sleep(1)

def after_scenario(context, scenario):
    context.driver.quit()