from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

file_path = "/Users/lingyao/PycharmProjects/E2ESD_data_construct/E2EDev/For_Behave_Warehouse(TestOnly)/E2ESD_Bench_08/index.html"

@given("the local storage is empty")
def step_given_local_storage_empty(context):
    context.driver = webdriver.Chrome()
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/E2EDev/For_Behave_Warehouse(TestOnly)/E2ESD_Bench_08/index.html")
    context.driver.execute_script("localStorage.clear();")
    time.sleep(0.1)

@when("the user opens the Library Management System webpage")
def step_when_user_opens_webpage(context):
    context.driver.get(f"file:///Users/lingyao/PycharmProjects/E2ESD_data_construct/E2EDev/For_Behave_Warehouse(TestOnly)/E2ESD_Bench_08/index.html")
    time.sleep(0.1)

@then('the table body with data-testid "table-body" should be empty')
def step_then_table_body_should_be_empty(context):
    table_body = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='table-body']"))
    )
    assert table_body.text.strip() == "", "Expected table body to be empty"

def after_scenario(context, scenario):
    context.driver.quit()