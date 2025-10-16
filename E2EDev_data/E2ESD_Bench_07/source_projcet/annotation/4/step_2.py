from behave import given, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given("the user navigates to the BMI Calculator webpage")
def step_given_user_navigates_to_bmi_calculator(context):
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)

@then('the table should contain the BMI range "less than 18.5" with data-testid "bmi-value-1"')
def step_then_bmi_range_less_than_18_5(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='bmi-value-1']"))
    )
    expected_text = "less than 18.5"
    assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the corresponding category "Underweight" should be displayed with data-testid "category-value-1"')
def step_then_category_underweight(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='category-value-1']"))
    )
    expected_text = "Underweight"
    assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the table should contain the BMI range "between 18.5 and 24.9" with data-testid "bmi-value-2"')
def step_then_bmi_range_between_18_5_and_24_9(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='bmi-value-2']"))
    )
    expected_text = "between 18.5 and 24.9"
    assert '18.5' in element.text.lower() and '24.9' in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the corresponding category "Ideal" should be displayed with data-testid "category-value-2"')
def step_then_category_ideal(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='category-value-2']"))
    )
    expected_text = "Ideal"
    assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the table should contain the BMI range "between 25 and 29.9" with data-testid "bmi-value-3"')
def step_then_bmi_range_between_25_and_29_9(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='bmi-value-3']"))
    )
    expected_text = "between 25 and 29.9"
    assert '25' in element.text.lower() and '29.9' in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the corresponding category "Overweight" should be displayed with data-testid "category-value-3"')
def step_then_category_overweight(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='category-value-3']"))
    )
    expected_text = "Overweight"
    assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the table should contain the BMI range "over 30" with data-testid "bmi-value-4"')
def step_then_bmi_range_over_30(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='bmi-value-4']"))
    )
    expected_text = "over 30"
    assert '30' in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

@then('the corresponding category "Obesity" should be displayed with data-testid "category-value-4"')
def step_then_category_obesity(context):
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='category-value-4']"))
    )
    expected_text = "Obesity"
    assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
    time.sleep(1)

def after_scenario(context, scenario):
    context.driver.quit()