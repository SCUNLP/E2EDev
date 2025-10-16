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

@given('the \'Height in cm\' input field with data-testid \'height-input\' is visible')
def step_given_height_input_field_visible(context):
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='height-input']"))
    )
    time.sleep(1)

@when('the user enters "170" into the \'Height in cm\' input field with data-testid \'height-input\'')
def step_when_user_enters_height(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    height_input.clear()
    height_input.send_keys("170")
    time.sleep(1)

@then('the system should store the value "170" for BMI calculation')
def step_then_system_stores_height_value(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    stored_value = height_input.get_attribute("value")
    assert stored_value == "170", f"Expected height value to be '170', but got '{stored_value}'"
    time.sleep(1)

@then('the \'Height in cm\' input field should display "170"')
def step_then_height_input_field_displays_value(context):
    height_input = context.driver.find_element(By.CSS_SELECTOR, "[data-testid='height-input']")
    displayed_value = height_input.get_attribute("value")
    assert displayed_value == "170", f"Expected height input field to display '170', but got '{displayed_value}'"
    time.sleep(1)

def after_scenario(context, scenario):
    context.driver.quit()