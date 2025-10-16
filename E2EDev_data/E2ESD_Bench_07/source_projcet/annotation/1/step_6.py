from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given("the BMI Calculator page is loaded")
def step_given_bmi_calculator_page_loaded(context):
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)

@given("the 'Height in cm' input field with data-testid 'height-input' is visible")
def step_given_height_input_field_visible(context):
    height_input = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    assert height_input.is_displayed(), "Height input field is not visible"
    time.sleep(1)

@when("the user does not enter any value into the 'Height in cm' input field with data-testid 'height-input'")
def step_when_user_does_not_enter_height(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    height_input.clear()
    time.sleep(1)

@then("the system should not store any value for BMI calculation")
def step_then_system_should_not_store_value(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    assert height_input.get_attribute("value") == "", "Height input field is not empty"
    time.sleep(1)

@then("the 'Height in cm' input field should remain empty")
def step_then_height_input_field_remains_empty(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    assert height_input.get_attribute("value") == "", "Height input field is not empty"
    time.sleep(1)

def after_scenario(context, scenario):
    context.driver.quit()