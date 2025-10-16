from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html"

@given('the user navigates to the BMI Calculator webpage')
def step_given_user_navigates_to_bmi_calculator(context):
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/data/Ourdatas/LJY_TEST_NEW2/E2ESD_Bench_07/index.html")
    time.sleep(1)  # Allow time for the page to load

@when('the user resizes the browser window to a small screen size')
def step_when_user_resizes_browser_window(context):
    context.driver.set_window_size(480, 800)  # Example small screen size
    time.sleep(1)  # Allow time for the resize to take effect

@then('the table with BMI ranges and categories should remain visible and properly formatted')
def step_then_table_should_remain_visible(context):
    table = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.chart table"))
    )
    assert table.is_displayed(), "The BMI table is not visible"
    time.sleep(1)  # Allow time for any potential animations or transitions

def after_scenario(context, scenario):
    context.driver.quit()