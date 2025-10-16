import copy
import os
from openai import OpenAI
import re
import subprocess
import sys
import shutil
import json
import ast
import tiktoken
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

class ChatContextManager:
    def __init__(self):
        self.context = []

    def add_message(self, role, content, name=None):
        """Store the complete context to distinguish different Agents"""
        if role not in ["user", "assistant", "system"]:
            raise ValueError("Invalid role: must be 'user', 'assistant', or 'system'")

        message = {"role": role, "content": content}
        if role == "assistant" and name:
            message["name"] = name

        self.context.append(message)

    def get_context(self):
        return self.context

    def clear_context(self):
        self.context = []


class BaseAgent:
    def __init__(self, context_manager, model_name, agent_name):
        self.context_manager = context_manager
        self.model_name = model_name
        self.agent_name = agent_name
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.encoding = tiktoken.encoding_for_model('gpt-4o')

    def count_message_tokens(self, messages):
        total_tokens = 0
        for message in messages:
            total_tokens += len(self.encoding.encode(message["content"]))
        return total_tokens

    def call_model_streaming(self, messages):
        """Use the fluent API for code modification"""
        try:
            print("🔹 Sending request to OpenAI API...")  # Debug Log
            prompt_tokens = self.count_message_tokens(messages)
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                top_p=1,
                stream=True  # Enable streaming response
            )

            completion_tokens = 0
            response_content = ""

            for chunk in completion:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        response_content += delta.content
                        print(delta.content, end="", flush=True)  # ✅ Make sure streaming output is visible
                        completion_tokens += len(self.encoding.encode(delta.content))


            print("\n✅ Response received!")  # Debug

            # Display token usage
            print("-------------- token usage --------------")
            print(f"🔠 Total Tokens: {completion_tokens + prompt_tokens}")  # Debug
            print(f"🔠 Prompt Tokens: {prompt_tokens}")
            print(f"🔠 Complete Tokens: {completion_tokens}")
            print("-------------- token usage --------------")
            return response_content
        except Exception as e:
            print(f"❌ Error: {str(e)}")  # Debug print error
            return f"Error: {str(e)}"


class CodeAnalysisAgent(BaseAgent):
    def __init__(self, context_manager, model_name):
        super().__init__(context_manager, model_name, "CodeAnalysisAgent")
        self.system_content_html = """
        You are an expert in analyzing HTML code from Web applications. Your task is to extract UI elements and their attributes.

Your analysis should include:
1. List of all UI elements (buttons, input fields, links, etc.) with their `id`, `class`, and role.
2. Any form-related elements and their expected interactions.
3. A concise summary of the UI structure.

Ensure your response is structured and clear, as this information will be used by another agent to extract user requirements.
        """

        self.system_content_js = """
        You are an expert in analyzing JavaScript code from Web applications. Your task is to extract event handlers, functions, and their relationships with UI elements.

Your analysis should include:
1. JavaScript functions that handle user interactions (e.g., `onclick`, `onchange`).
2. The `id` or `class` of the elements these functions interact with.
3. A concise summary of how JavaScript controls the page's behavior.

Ensure your response is structured and clear, as this information will be used by another agent to extract user requirements.
        """

    def analyze_html(self, html_code, content_manager_based):
        """Analyze a single HTML file"""
        prompt = f"""
        ### Provided HTML Code:
{html_code}

Extract:
- UI elements and their attributes (id, class, role).
- Form-related elements and interactions.
- A summary of the page structure.
        """
        messages = [{"role": "system", "content": self.system_content_html}]
        self.context_manager.add_message("user", prompt)
        content_manager_based.add_message("user", prompt)
        messages.extend(self.context_manager.get_context())
        response = self.call_model_streaming(messages)
        self.context_manager.add_message("assistant", response, self.agent_name)
        return response, content_manager_based

    def analyze_js(self, js_code, content_manager_based):
        """Analyze a single JavaScript file"""
        prompt = f"""
        ### Provided JavaScript Code:
{js_code}

Extract:
- Functions handling user interactions.
- UI elements linked to event handlers.
- A summary of how JavaScript affects the page.
        """
        messages = [{"role": "system", "content": self.system_content_js}]
        self.context_manager.add_message("user", prompt)
        content_manager_based.add_message("user", prompt)
        messages.extend(self.context_manager.get_context())
        response = self.call_model_streaming(messages)
        self.context_manager.add_message("assistant", response, self.agent_name)
        return response, content_manager_based

    def analyze_code(self, html_files, js_files, context_manager_based):
        """Analyze multiple HTML and JS files and combine the results"""
        self.context_manager.clear_context()
        html_results = []
        js_results = []

        print("[CodeAnalysisAgent] 🔍 Analyzing HTML...")
        for html_file in html_files:
            response, content_manager_based = self.analyze_html(html_file, context_manager_based)
            html_results.append(response)

        print("[CodeAnalysisAgent] 🔍 Analyzing JavaScript...")
        for js_file in js_files:
            response, content_manager_based = self.analyze_js(js_file, context_manager_based)
            js_results.append(response)

        final_result = {
            "html_analysis": html_results,
            "js_analysis": js_results
        }

        return final_result, context_manager_based


class RequirementExtractionAgent(BaseAgent):
    def __init__(self, context_manager, model_name):
        super().__init__(context_manager, model_name, "RequirementExtractionAgent")
        self.system_content = """
        You are an expert in extracting **functional** user requirements from web applications. Generate a **comprehensive and testable** list of user requirements that cover all user-facing functionalities.
        
        ### Functional Requirement Criteria
        Each requirement must include the following elements to ensure it is complete and testable:
        1. **ID**: A unique identifier (e.g., REQ-001).
        2. **Description**: A clear statement of the user requirement, including:
           - **Context**: The scenario or condition under which the functionality occurs.
           - **User Action**: What the user does (e.g., clicks, types, scrolls).
           - **System Response**: The expected outcome after the user action.
        
        ### **Rules**:
        - Only include **functional requirements** — i.e., observable behaviors triggered by user interaction via the front end (such as clicking a button, entering text, receiving visual feedback, etc.).
        - **Avoid including non-functional requirements** such as performance, security, or scalability unless they are visible or interactive on the UI.
        - Exclude backend logic unless it has a **direct effect on the UI** that is visible or interactive.

        ### **Output Format (JSON)**
        {
          "summary": {
            "overview": "Briefly describe the application's purpose and key functionalities.",
            "predefined_options": "Predefined options set by the system to standardize inputs and reduce manual configuration, such as default values and preset selections.",
            "external_resources": "External resources used by the application, including links, images, audio files, and other media. List the resource names and their sources (URLs or file paths).",
            "external_js_libraries": "External JavaScript libraries or packages used by the application, such as jQuery, React, Bootstrap, etc. Provide the library names and their sources (e.g., CDN links)."
        }
        ,
          "requirements": [
            {
              "id": "Unique identifier",
              "description": "User requirement description with context, user action, and system response."

            }
          ]
        }
        """
        self.user_content = "Based on the analysis on html and js code, extract and format the user requirements for this Web application. Ensure clarity and completeness.block with the language tag `json`."

    def extract_requirements(self):
        """Extract requirement information from the code"""
        messages = [{"role": "system", "content": self.system_content}]
        self.context_manager.add_message("user", self.user_content)
        messages.extend(self.context_manager.get_context())
        response = self.call_model_streaming(messages)
        self.context_manager.add_message("assistant", response, self.agent_name)
        # Extract the contents of the json block
        requirement_block = re.search(r'```json(.*?)```', response, re.DOTALL)
        if requirement_block:
            return json.loads(requirement_block.group(1))
        else:
            return []

    def refine_requirements(self):
        user_content = "Review and refine the previously extracted user requirements to ensure their completeness, accuracy, and clarity. "
        messages = [{"role": "system", "content": self.system_content}]
        self.context_manager.add_message("user", user_content)
        messages.extend(self.context_manager.get_context())
        response = self.call_model_streaming(messages)
        # Extract the contents of the json block
        requirement_block = re.search(r'```json(.*?)```', response, re.DOTALL)
        if requirement_block:
            return json.loads(requirement_block.group(1))
        else:
            return []

    def modify_req(self, requirement, content_manager_based):
        system_content = """
    You are an expert in software requirements refinement. Your task is to enhance and update user requirements based on Gherkin test cases.

    ### **Instructions**  
    - Carefully review all provided Gherkin scenarios and consolidate their logic into a single comprehensive and precise requirement.
    - Ensure the final requirement:
        - Captures all variations, including normal cases, edge cases, boundary conditions, and special scenarios.
        - Includes explicit UI details, such as:
            - Selectors or attributes used to locate elements (e.g., data-testid, id, class)
            - User interactions (e.g., click, hover, input)
            - Expected results (e.g., DOM updates, class changes, attribute changes)
        - If persistent storage (e.g., localStorage) is involved, specify:
            - The keys used
            - What data is stored or retrieved

    - Maintain the original intent of the functionality while improving clarity, completeness, and specificity.
    - Do not invent functionality not implied by the test cases.
    
    ### **Output Format (JSON)**
    Return the final requirement in the following JSON format, wrapped in a code block with the language tag `json`
    ```json
    {
  "description": "A refined and precise user requirement that explicitly includes variations across different scenarios, covering all relevant UI elements, interactions, expected results, and persistent data handling if applicable."
}

    ```
    """

        self.user_content = f"""
        Refine the following user requirement for this Web application based on the previous Gherkin test cases:  

**Original Requirement:**  
{requirement}  
        """
        messages = [{"role": "system", "content": system_content}]
        content_manager_based.add_message("user", self.user_content)
        messages.extend(content_manager_based.get_context())
        response = self.call_model_streaming(messages)
        # Extract the contents of the json block
        requirement_block = re.search(r'```json(.*?)```', response, re.DOTALL)
        if requirement_block:
            return json.loads(requirement_block.group(1))
            # return {'REQ':requirement_block}
        else:
            return []


class TestCaseGenerationAgent(BaseAgent):
    def __init__(self, model_name):
        super().__init__(None, model_name, "TestCaseGenerationAgent")
        self.system_content = """
You are an expert in software testing. Your task is to generate **comprehensive** Gherkin test cases based on the provided user requirement.

### **Instructions:**
1. **Mapping Requirements to Features**:
   - Each user requirement **must** be mapped to a corresponding `Feature`.
   - The `Feature` description should clearly summarize the purpose and scope of the requirement.

2. **Scenario Coverage**:  
   - Each `Feature` must include multiple `Scenario` blocks covering:  
     - **[Normal]** Expected behavior.  
     - **[Edge]** Unusual or extreme conditions.  
     - **[Error]** Invalid inputs or failures.  
   - **Label each Scenario** with `[Normal]`, `[Edge]`, or `[Error]`.  

3. **Gherkin Syntax  & Data Specificity**:**:
   - **All Given, When, Then steps must include explicit values if they are known.**  
      - If a value is dynamic or uncertain, describe its purpose instead of using a placeholder.  
      - Reference relevant UI elements (data-testid) for stable and precise element identification.
      - Clearly define user interactions, specifying actions like clicks, text input, or toggling switches.
      - State expected outcomes explicitly, verifying component properties such as displayed text, input values.
      
   - **DO NOT generate structured tables** (e.g., `| Column | Value |`).
        - Instead, describe inputs and outputs directly in the step definitions. For example:
       - Incorrect: Use a table to list inputs.
       - Correct: Write "When the user enters 'testuser' into the username field with data-testid 'username-input'."
   - Each `Scenario` **must** follow the **Given-When-Then** syntax:
     - `Given`: Defines the initial context (UI components, form fields, buttons, etc.) present in the application's HTML structure.
     - `When`: Specifies the user action (click, input, navigation) that is linked to an actual event handler in the JavaScript code.
     - `Then`: States the expected outcome, ensuring it matches the UI behavior as defined in the JavaScript logic.
     
4. **Scenario Independence & Page Initialization**:
   - Each `Scenario` **must** be **independent, complete, and executable on its own**.
   - **Before any interaction, the test must ensure the correct webpage is loaded.**

5. **Output Format**:
   - Wrap the entire Gherkin test cases in a single code block with the language tag `gherkin`. 
            """

        self.user_content_template = """
                Based on the provided HTML and JavaScript code, generate **Gherkin test cases** for the following user requirement:  

                **Requirement:** {requirement}  
            """

    def split_scenarios(self, gherkin_code):
        """Split the Feature header and each Scenario in the Gherkin code"""
        lines = gherkin_code.strip().split("\n")

        feature_header = []
        scenarios = []
        current_scenario = []

        for line in lines:
            if line.strip().startswith("Scenario:"):  
                if current_scenario:
                    scenarios.append("\n".join(current_scenario)) 
                current_scenario = [line]  
            elif current_scenario:
                current_scenario.append(line) 
            else:
                feature_header.append(line)  

        if current_scenario:
            scenarios.append("\n".join(current_scenario)) 

        return "\n".join(feature_header), scenarios

    def generate_test_cases(self, context_manager, requirement):
        """Generate test cases"""
        messages = [{"role": "system", "content": self.system_content}]
        user_content = self.user_content_template.format(requirement=requirement)
        context_manager.add_message("user", user_content)
        messages.extend(context_manager.get_context())
        response = self.call_model_streaming(messages)

        # Extract the contents of the ```gherkin``` code block
        gherkin_code_blocks = re.findall(r'```gherkin(.*?)```', response, re.DOTALL)
        gherkin_code_lst = [gherkin_code.strip() for gherkin_code in gherkin_code_blocks]
        # gherkin_code_lst = [gherkin_code.strip().replace("'", '"') for gherkin_code in gherkin_code_blocks]

        return gherkin_code_lst

    def validate_test_cases(self,context_manager,usr_content=None):
        """Verify whether the generated test cases are reasonable"""
        system_content = """
    You are an expert in software testing.  
    Your task is to validate the Gherkin test case's logic based on the application's UI structure, JavaScript logic, and user requirements.

    ## Guidelines:
    1. **Check Given**: Ensure the initial state (UI components, form fields, buttons, etc.) exists in the application's HTML structure.  
    2. **Check When**: Ensure the user action (click, input, navigation) corresponds to a real event handler in the JavaScript code.  
    3. **Check Then**: Ensure the expected outcome reflects the UI behavior as defined in the JavaScript logic.

    ## Constraints:
    - **Only validate** the logic of the current Gherkin scenario.
    - Do **NOT** add new scenarios.
    - If any step is incorrect, propose a **minimal correction** while keeping the test scenario structure intact.
    - Return the corrected **Gherkin test case** after applying corrections to the **existing steps**.

    ## Output Format:
    - Wrap the entire Gherkin test case in a single code block with the language tag `gherkin`. 
    """
        if usr_content == None:
            usr_content = f"""
            Validate the following Gherkin test cases based on the application's UI structure, JavaScript logic, and user requirements.
            """
        else :
            user_content = f"Please revise the Gherkin test case based on the user's suggestion: {usr_content}."
        if user_content == None:
            messages = [{"role": "system", "content": system_content}]
        else:
            messages = [{"role": "system", "content": self.system_content}]
        messages.extend(context_manager.get_context())
        context_manager.add_message("user", usr_content)
        response = self.call_model_streaming(messages)
        gherkin_code_blocks = re.findall(r'```gherkin(.*?)```', response, re.DOTALL)
        gherkin_code_lst = [gherkin_code.strip() for gherkin_code in gherkin_code_blocks]

        return gherkin_code_lst



class StepImplementationAgent(BaseAgent):
    def __init__(self, model_name):
        super().__init__(None, model_name, "StepImplementationAgent")
        self.system_content = """
You are an expert in implementing Selenium-based automated test scripts using Behave. Your task is to convert Gherkin test cases into Python step implementations that adhere to the following rules:

1. **Step Definitions**:
   - Each `Given`, `When`, and `Then` step must have a corresponding `@given`, `@when`, or `@then` function.
   - **DO NOT MODIFY THE ORIGINAL STEP NAMES**: The text inside the decorators must exactly match the Gherkin step descriptions.
   - If the Gherkin test case includes a `Background`, implement it first and ensure all `Scenario` steps reuse its setup without reinitializing `context` or `driver`.

2. **Selenium Best Practices**:
   1. Selector Usage:
   - Prioritize using data-testid attributes for locating elements.
     Example:
         driver.find_element(By.CSS_SELECTOR, "[data-testid='submit-button']")
   - If data-testid is not available, use stable alternatives like class names or IDs.
   - Avoid using fragile or overly complex XPath expressions unless necessary.

    2. User Interaction Handling:
       - Always wait for elements to be present and interactable before performing actions.
       - Use WebDriverWait to ensure visibility or clickability.
         Example:
             WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='submit-button']")))
       - Handle interactions like clicking, typing, and checking visibility with proper error handling.
    
    3. Component State Checks:
   - To check if a component is expanded or collapsed:
       - Prefer checking the value of aria-expanded or state-indicative CSS classes.
       - Check `data-*` attributes like `data-expanded`, or look at CSS properties (e.g., display).
       - Define a helper function to check expansion state robustly:
         Example:
             def is_expanded(element):
                 # Check aria-expanded first
                 aria = element.get_attribute("aria-expanded")
                 if aria is not None:
                     return aria == "true"

                 # Check CSS class for expanded state
                 class_list = element.get_attribute("class").split()
                 if any(cls in class_list for cls in ["expanded", "open", "show"]):
                     return True

                 # Check data-expanded attribute
                 data_expanded = element.get_attribute("data-expanded")
                 if data_expanded is not None:
                     return data_expanded == "true"

                 # Fallback: Use display property to check visibility
                 return element.is_displayed()

       - To check if a component is collapsed:
           - Collapse can typically be indicated by the absence of an "expanded" class or an "aria-expanded" value of "false".
           - Example:
             def is_collapsed(element):
                aria = element.get_attribute("aria-expanded")
                if aria is not None and aria.lower() == "false":
                    return True
            
                class_attr = element.get_attribute("class") or ""
                class_list = class_attr.split()
                if "collapsed" in class_list:
                    return True
            
                data_expanded = element.get_attribute("data-expanded")
                if data_expanded is not None and data_expanded.lower() == "false":
                    return True
            
                style = element.get_attribute("style") or ""
                if "display: none" in style or "visibility: hidden" in style or "height: 0" in style:
                    return True
            
                return not element.is_displayed()


   - To check visibility:
       - Use element.is_displayed() to determine if an element is visible.
       - Alternatively, check visibility with JavaScript or CSS properties like `visibility: hidden;` or `display: none;`.
       - You can also check for non-zero element size (`offsetWidth`, `offsetHeight`).
         Example:
             is_visible = driver.execute_script("return arguments[0].offsetWidth > 0 && arguments[0].offsetHeight > 0;", element)

   - To validate text content:
       - Use case-insensitive, partial match assertions.
         Example:
             expected_text = "submit"
             assert expected_text.lower() in element.text.lower(), f"Expected '{expected_text}' in '{element.text}'"
       - Consider dynamic content and validate after page updates.
       - Handle extra spaces or newline characters by trimming input.
         Example:
             assert expected_text.strip() in element.text.strip(), f"Expected '{expected_text}' in '{element.text}'"

   - To validate redirected URLs:
       - Strip off the hash (#) part before comparing.
         Example:
             base_url = driver.current_url.split("?")[0].split("#")[0]
             expected_base_url = expected_url.split("?")[0].split("#")[0]
             assert base_url == expected_base_url, f"Expected URL '{expected_base_url}', but got '{base_url}'"

3. **Test Setup and Teardown**:
   - Load the test page from a local file using `file_path`.
   - Ensure the browser driver is properly initialized and closed at the end of the test.
   - Include the placeholder `file_path = "file_path_placeholder"` in the implementation for dynamic file path handling.

4. **Code Quality**:
   - Follow best practices for maintainability:
     - Use explicit waits (`WebDriverWait`) instead of implicit waits.
     - **After each interaction with a web element (e.g., `.click()`, `.send_keys()`, `.get()`), insert `time.sleep(1)` to improve test robustness.**
     - Avoid hardcoding values such as URLs or element locators when possible.
     - Write clear and concise code with meaningful variable names.
     

5. **Output Format**:
   - Provide the corrected Python code wrapped in a code block with the language tag `python`.
        """
        self.user_content_template = """
Translate the provided Gherkin test cases into Selenium and Behave step implementations. Ensure each step is correctly translated into Python code while adhering to the following requirements:

1. **Test Page Loading**:
   - Use the placeholder `file_path = "file_path_placeholder"` to dynamically load the test page.
   - Initialize the Selenium WebDriver (e.g., `webdriver.Chrome()`) and navigate to the test page using:
     ```python
     context.driver.get(f"file://{file_path}")
     ```

2. **Driver Management**:
   - Ensure the browser driver is properly closed at the end of the test to prevent resource leaks.

3. **Step Implementation**:
   - Implement all steps (`Given`, `When`, `Then`) as described in the Gherkin test cases.
   - Do not modify the original step names; ensure they exactly match the provided descriptions.

Please wrap the Python code in a code block with the language tag `python`.
        """

    def implement_steps(self, index_path, context_manager):
        """Implement the steps in the test case"""
        messages = [{"role": "system", "content": self.system_content}]
        user_content = self.user_content_template.format(file_path=index_path)
        context_manager.add_message("user", user_content)
        messages.extend(context_manager.get_context())
        response = self.call_model_streaming(messages)

        # Extract the contents of the ```python``` code block
        python_code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
        python_code = '\n'.join(python_code_blocks).strip()

        # Make sure the generated code contains the file_path variable and replaces it
        if "file_path =" in python_code:
            python_code = re.sub(r'file_path\s*=\s*"[^"]*"', f'file_path = "{index_path}"', python_code)

        # context_manager.add_message("assistant", response, self.agent_name)
        return python_code

    def fix_steps(self, index_path, context_manager, behave_state=False):
        """Automatically fix step.py based on Behave runtime errors"""
        if behave_state == False:
            system_content = """
            You are an AI assistant that helps users fix issues in Behave step definitions (step.py). 
Your task is to analyze the errors reported during a Behave dry run and modify the code while adhering to the following rules:

1. **Step Definitions**:
   - Each `Given`, `When`, and `Then` step must have a corresponding `@given`, `@when`, or `@then` function.
   - Do not modify the content inside the decorators (e.g., step descriptions).

2. **Error Analysis**:
   - Analyze the errors reported during the dry run. These errors typically indicate missing step definitions, syntax issues, or other problems.
   - Ensure that all undefined steps are implemented correctly.

3. **Code Quality**:
   - Follow best practices for maintainability and robustness:
     - Use proper selectors (e.g., Selenium locators) where applicable.
     - Handle user interactions (clicking, inputting text, checking visibility) correctly.
     - Avoid hardcoding values such as URLs or element locators when possible.

4. **Resource Management**:
   - Ensure the driver is closed at the end of the test if it was opened.

5. **Code Block**:
   - Provide the corrected Python code wrapped in a code block with the language tag `python`.
            """
            fix_content = f"""
            Analyze the Behave test errors and modify the step.py code to ensure the test passes. Please wrap the corrected Python code in a code block with the language tag `python`.
            """
        else:
            system_content = """
            You are an AI assistant that helps users fix issues in Behave step definitions (step.py). 
            Your task is to analyze the failure logs and then modify the code while adhering to the following rules:

1. **Do not alter the structure or framework of the code**:
   - Do not modify the content inside the `@given`, `@when`, or `@then` decorators.
   - Ensure that the step definitions remain intact (e.g., function signatures and decorator mappings).

2. **Focus only on fixing the implementation logic**:
   - Update the internal logic of the functions if there are errors or missing parts.
   - Ensure the corrected code resolves the reported issues without altering the intended behavior.

3. **Provide the corrected Python code in a code block**:
   - Wrap the corrected Python code in a code block with the language tag `python`.
            """
            fix_content = f"""
         Analyze the behave log failure information and modify the step.py code to ensure the test passes. Please wrap the corrected Python code in a code block with the language tag `python`.
        """
        messages = [{"role": "system", "content": system_content}]
        context_manager.add_message("user", fix_content)
        messages.extend(context_manager.get_context())
        response = self.call_model_streaming(messages)

        # Extract the contents of the ```python``` code block
        python_code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
        python_code = '\n'.join(python_code_blocks).strip()

        # Make sure the corrected code contains the file_path variable and replaces it
        if "file_path =" in python_code:
            python_code = re.sub(r'file_path\s*=\s*"[^"]*"', f'file_path = "{index_path}"', python_code)

        # context_manager.add_message("assistant", response, self.agent_name)
        return python_code, context_manager

class StepComponentLocatorAgent(BaseAgent):
    def __init__(self, model_name):
        super().__init__(None, model_name, "StepComponentLocatorAgent")
        self.system_content = """
You are an expert in Selenium-based automated test scripts using Behave. Your task is to extract all relevant component locators from the provided Python step implementation.

For each locator, return a tuple in the format:
- `(Locator Method, Component Name, Purpose)`

Where:
- `Locator Method`: The Selenium method used.
- `Component Name`: The identifier of the component (e.g., `"user-name"`, `"submit-button"`).
- `Purpose`: The description of the component’s purpose (e.g., `"Input field for the user's name"`, `"Submit button for the form"`).

Ensure to handle all locators (e.g., `find_element_by_*`, `By.*`) and provide the correct purpose for each component.

Return the extracted locators in a **list** of tuples, wrapped in a code block with the language tag `python`
"""
        self.user_content = """
Extract all relevant component locators from the provided Python step implementation. Return the locators in a list of tuples with the format `(Locator Method, Component Name, Purpose)`. Wrap the output in a code block with the language tag `python`.
The step.py code is :
{step_py}
"""
    def extract_locators(self, step_py):
        messages = [{"role": "system", "content": self.system_content}]
        user_content = self.user_content.format(step_py=step_py)
        messages.append({"role": "user", "content": user_content})
        response = self.call_model_streaming(messages)

        # Extract the contents of the ```python``` code block
        pattern = r'```python\n(.*?)\n```'
        # Use re.DOTALL to make . match newline characters
        locators = re.findall(pattern, response, re.DOTALL)
        # locator_lst = ast.literal_eval(locators[0])
        pattern = r'\(([^)]+)\)'
        try:
            locator_lst = re.findall(pattern, locators[0])
            locator_lst = [f"({locator})" for locator in locator_lst]
        except Exception as e:
            print(f"Error parsing locators: {e}")
            locator_lst = []

        return locator_lst


class TestRunnerAgent(BaseAgent):
    def __init__(self, model_name):
        super().__init__(None, model_name, 'TestRunnerAgent')

    def save_test_files(self, test_cases_lst, step_code, project_root, requirement_id):
        """Save the generated Gherkin test case and step.py code to the project folder"""
        self.project_root = project_root
        self.features_folder = os.path.join(self.project_root, "features")
        self.steps_folder = os.path.join(self.features_folder, "steps")

        # delete features folder
        if os.path.exists(self.features_folder):
            shutil.rmtree(self.features_folder)
        # Make sure the features and steps directories exist
        os.makedirs(self.features_folder, exist_ok=True)
        os.makedirs(self.steps_folder, exist_ok=True)

        # Store Gherkin code one by one, with each Feature stored in a separate file
        gherkin_files = []
        for idx, gherkin_code in enumerate(test_cases_lst, start=1):
            feature_file_path = os.path.join(self.features_folder, f"{requirement_id}_test_case_{idx}.feature")
            with open(feature_file_path, "w", encoding="utf-8") as f:
                f.write(gherkin_code)
            gherkin_files.append(feature_file_path)

        # Store step.py file
        step_file_path = os.path.join(self.steps_folder, f"{requirement_id}_step.py")
        with open(step_file_path, "w", encoding="utf-8") as f:
            f.write(step_code)

        print(f"[TestRunnerAgent] ✅ The test file has been saved to:")
        for file in gherkin_files:
            print(f"   - {file}")
        print(f"   - {step_file_path}")

    def delete_test_files(self):
        """Delete the entire features directory to prevent test files from affecting each other"""
        if os.path.exists(self.features_folder):
            shutil.rmtree(self.features_folder)

    def read_test_files(self, requirement_id):
        """Read stored Gherkin test cases and step.py code"""
        features_folder = self.features_folder
        steps_folder = self.steps_folder

        # Read Gherkin test cases
        test_cases_lst = []
        feature_files = sorted([f for f in os.listdir(features_folder) if
                                f.startswith(f"{requirement_id}_test_case_") and f.endswith(".feature")])

        for feature_file in feature_files:
            feature_path = os.path.join(features_folder, feature_file)
            with open(feature_path, "r", encoding="utf-8") as f:
                test_cases_lst.append(f.read())

        # Read step.py code
        step_file_path = os.path.join(steps_folder, f"{requirement_id}_step.py")
        step_code = ""
        if os.path.exists(step_file_path):
            with open(step_file_path, "r", encoding="utf-8") as f:
                step_code = f.read()

        return test_cases_lst, step_code

    def run_dry_run(self, project_root):
        """Run Behave in dry-run mode to verify that the definition of step.py is correct."""
        try:
            print("[TestRunnerAgent] 🚀 Start Behave dry-run mode...")
            result = subprocess.run(
                [sys.executable, "-m", "behave", "--dry-run"],  
                cwd=project_root, 
                capture_output=True,
                text=True
            )

            # Print the output of dry-run
            print("[TestRunnerAgent] ✅ Dry-run completed with the following results:")
            print(result.stdout)

            # Extract and analyze error information
            error_message = self.extract_error_info(result.stdout, result.stderr)

            # Determine if there is a real error
            if error_message:
                print(f"[TestRunnerAgent] ❌ dry-run fails with the following error message:\n{error_message}")
                return error_message

            print("[TestRunnerAgent] ✅ dry-run succeeded! The definition of step.py is complete and correct.")
            return "No Faults"

        except Exception as e:
            print(f"[TestRunnerAgent] ❌ Running Behave dry-run fails: {str(e)}")
            return f"Error: {str(e)}"

    def extract_error_info(self, stdout, stderr):
        """
        Extract error messages from a dry-run, ignoring statistics and irrelevant content.
        """
        error_message = []

        # If stderr is not empty, use the content of stderr first
        if stderr.strip():
            error_message.append("STDERR:")
            error_message.append(stderr.strip())

        # If stdout contains undefined steps or error messages
        if stdout.strip():
            lines = stdout.splitlines()
            for line in lines:
                # Filter statistics rows
                if "steps passed" in line.lower() or "untested" in line.lower():
                    continue

                # Check for undefined steps
                if "undefined" in line.lower() or "snippet" in line.lower():
                    if "Undefined Steps Found:" not in error_message:
                        error_message.append("Undefined Steps Found:")
                    error_message.append(line.strip())

                ## Check for other error messages
                # elif "error" in line.lower() or "traceback" in line.lower():
                #     if "STDOUT Errors:" not in error_message:
                #         error_message.append("STDOUT Errors:")
                #     error_message.append(line.strip())

        # If no error messages are found, return an empty list
        return "\n".join(error_message) if error_message else None

    def run_tests(self, project_root, return_log=False):
        """Run Behave command, ensuring execution within the Conda environment"""
        try:
            print("[TestRunnerAgent] 🚀 Starting Behave tests...")
            result = subprocess.run(
                [sys.executable, "-m", "behave"],  # Run via Conda interpreter
                cwd=project_root,  # Ensure running in the correct directory
                capture_output=True,
                text=True
            )

            print("[TestRunnerAgent] ✅ Tests completed, results:")
            print(result.stdout)
            if return_log:
                # If you want to handle failures differently, uncomment below
                # if result.returncode != 0:
                #     print("[TestRunnerAgent] ❌ Tests failed, error output:")
                #     print(result.stderr)
                return result.stdout

            if result.returncode != 0:
                print("[TestRunnerAgent] ❌ Tests failed, error output:")
                print(result.stderr)
                return result.stderr  # Return error info for StepFixAgent handling

            return "No Faults"

        except Exception as e:
            print(f"[TestRunnerAgent] ❌ Failed to run Behave: {str(e)}")
            return f"Error: {str(e)}"



class BehaveLogAnalysisAgent(BaseAgent):
    def __init__(self, model_name):
        super().__init__(None, model_name, "BehaveLogAnalysisAgent")
        self.system_content = """
        You are an expert in analyzing Behave test logs. Your task is to extract and summarize errors from Behave test execution results.  

### **Instructions:**  
1. Identify failed scenarios in the log.  
2. Extract the specific step that failed.  
3. Identify and summarize the error message.  
4. Return the results in a structured format.  

### **Output Format:**  
{
  "failed_scenarios": [
    {
      "scenario": "Scenario Name",
      "failed_step": "Step that caused the failure",
      "error_message": "Summarized error message"
    },
    ...
  ]
}  
Ensure accuracy and completeness in summarizing the errors.
"""
        self.user_content = """
        Analyze the following Behave test execution log and extract all failed scenarios along with the specific step that failed and the corresponding error message.

### **Log:**  
{log_text}

### **Expected Output:**  
- List all failed scenarios.  
- Identify the failing step for each scenario.  
- Provide a concise summary of the error message.  

Please wrap the extracted information in a code block with the language tag `json`.
"""

    def analyze_log(self, log_text):
        """Analyze Behave test logs to extract failed scenarios and error messages"""
        messages = [{"role": "system", "content": self.system_content}]
        user_content = self.user_content.format(log_text=log_text)
        messages.append({"role": "user", "content": user_content})
        response = self.call_model_streaming(messages)

        # extract JSON block
        json_block = re.search(r'```json(.*?)```', response, re.DOTALL)

        return json.loads(json_block.group(1)) if json_block else {}

    def wether_all_passed(self, log_text):
        """Determine whether all tests have passed"""
        passed_scenarios = re.search(r'(\d+)\s+scenario\s+passed', log_text)
        failed_scenarios = re.search(r'(\d+)\s+scenario\s+failed', log_text)

        # Determine whether all scenarios have passed
        if passed_scenarios and not failed_scenarios:
            print("All scenes have passed")
            return True
        else:
            print("There are failure scenarios")
            return False


class MultiAgentSystem:
    def __init__(self, context_manager, model_name):
        self.context_manager = context_manager
        self.model_name = model_name

        self.code_analysis_agent = CodeAnalysisAgent(self.context_manager, model_name)
        self.requirement_extraction_agent = RequirementExtractionAgent(self.context_manager, model_name)
        self.test_case_generation_agent = TestCaseGenerationAgent(model_name)
        self.step_implementation_agent = StepImplementationAgent(model_name)
        self.test_runner_agent = TestRunnerAgent(model_name)
        self.behave_log_analysis_agent = BehaveLogAnalysisAgent(model_name)
        self.step_component_locator_agent = StepComponentLocatorAgent(model_name)

    def run(self, html_files, js_files, project_root, main_page_root):
        annotation_dict = {}
        context_manager_based = ChatContextManager()
        print("[CodeAnalysisAgent] 🚀 **Starting code analysis**...")
        print("✨🌟--------------------------------[CodeAnalysisAgent] begin --------------------------------🌟✨")
        self.context_manager.clear_context()
        analysis_result, context_manager_based = self.code_analysis_agent.analyze_code(html_files, js_files,
                                                                                       context_manager_based)
        print("✨🌟--------------------------------[CodeAnalysisAgent] end--------------------------------🌟✨")

        print('\n')
        print("[RequirementExtractionAgent] 📌 Code analysis complete, extracting requirements...")
        print("✨🌟--------------------------------[RequirementExtractionAgent] begin --------------------------------🌟✨")
        requirements = self.requirement_extraction_agent.extract_requirements()
        print("✨🌟--------------------------------[RequirementExtractionAgent] end --------------------------------🌟✨")
        print('\n')

        # print("[RequirementRefineAgent] 📌 Requirements think again...")
        # print("✨🌟--------------------------------[RequirementRefineAgent] begin --------------------------------🌟✨")
        # requirements = self.requirement_extraction_agent.refine_requirements()
        # print("✨🌟--------------------------------[RequirementRefineAgent] end --------------------------------🌟✨")
        # print('\n')
        json_path = os.path.join(project_root, "requirements.json")
        txt_path = os.path.join(project_root, "requirements.txt")

        # Delete existing files
        for path in [json_path, txt_path]:
            if os.path.exists(path):
                os.remove(path)
        # save as json
        with open(os.path.join(project_root, "requirements.json"), "w", encoding="utf-8") as f:
            json.dump(requirements, f, indent=4)
        # print('[RequirementExtractionAgent] 📌 Requirements extraction complete, results saved to requirements.json. If you want to add requirements, please directly edit the requirements.json file (press Enter to continue)')
        # input()
        # # read requirements from json
        # with open(os.path.join(project_root, "requirements.json"), "r", encoding="utf-8") as f:
        #     requirements = json.load(f)

        # save as txt
        # with open(os.path.join(project_root, "requirements.txt"), "w", encoding="utf-8") as f:
        #     f.write(json.dumps(requirements, indent=4))

        requirement_summary = requirements.get("summary", {})
        requirements = requirements.get("requirements", [])
        # context_manager_based.add_message("assistant", json.dumps(requirement_summary), "RequirementExtractionAgent")

        for req_idx, requirement in enumerate(requirements, start=1):
            # For each requirement, first decide if annotation is needed
            print("✨🌸--------------------------------[Human Interaction(requirements assessment)] begin--------------------------------🌸✨")
            print(f"[MultiAgentSystem] 📝 Processing requirement {req_idx}/{len(requirements)}: {requirement['description']}")
            print("✨🔍 Do you want to annotate this requirement? (y/n) ✨", end=" ")
            user_choice = input().strip().lower()
            if user_choice == "n":
                print("[Human Interaction(requirements assessment)]🌷 Please provide your reason:")
                reason = input().strip()
                print("[Human Interaction(requirements assessment)]🌷 Thank you for your feedback!")
                continue
            print("Do you want to modify the requirement? (y/n) ✨", end=" ")
            modify_choice = input().strip().lower()
            if modify_choice == "y":
                print("✍️ Please enter the modified requirement (press Enter to keep unchanged):")
                modified_requirement = input().strip()
                print('\n')
                if modified_requirement:
                    requirement['description'] = modified_requirement
            point_context_manager = copy.deepcopy(context_manager_based)
            # point_context_manager.add_message("assistant", json.dumps(requirement), "RequirementExtractionAgent")
            print("✨🌸--------------------------------[Human Interaction(requirements assessment)] end--------------------------------🌸✨")
            print('\n')

            print("[TestCaseGenerationAgent] 🏗️ Generating Gherkin test cases...")
            print("✨🌟--------------------------------[TestCaseGenerationAgent] begin --------------------------------🌟✨")
            gherkin_code_lst = self.test_case_generation_agent.generate_test_cases(point_context_manager, requirement)
            print("✨🌟--------------------------------[TestCaseGenerationAgent] end --------------------------------🌟✨")
            print('\n')
            # print(
            #     "✨🌸--------------------------------[Human Interaction(Test Case assessment-whole)] begin--------------------------------🌸✨")
            # print("🔧 Do you want to modify the test cases? Enter your advice (If no modification, type No): ✨", end=" ")
            # usr_advice = input().strip().lower()
            # if usr_advice.lower() == "no" or not usr_advice:
            #     print("[TestCaseGenerationAgent] 🌷 No modification needed.")
            # else:
            #     gherkin_code_lst = self.test_case_generation_agent.validate_test_cases(
            #         point_context_manager, usr_advice
            #     )
            # print(
            #     "✨🌸--------------------------------[Human Interaction(Test Case assessment-whole)] end--------------------------------🌸✨")

            final_gherkin_code = []
            test_info_lst =[]
            related_elements = []
            for idx, gherkin_code in enumerate(gherkin_code_lst, start=1):
                feature_header, scenarios = self.test_case_generation_agent.split_scenarios(gherkin_code)
                new_scenarios = []
                for scenario_idx, scenario in enumerate(scenarios, start=1):
                    point_context_manager = copy.deepcopy(context_manager_based)
                    print("✨🌸--------------------------------[Human Interaction(Test Case assessment)] begin--------------------------------🌸✨")
                    print(f"🎭 Scenario {scenario_idx}/{len(scenarios)} in Feature {idx}:")
                    test_cases = [feature_header + '\n\n' + scenario]
                    print(f"{test_cases[0]}")
                    print(f"📝 Do you want to annotate this scenario? (y/n) ✨\n", end=" ")
                    user_choice = input().strip().lower()
                    if user_choice == "n":
                        print("[Human Interaction(Test Case assessment)]🌷 Please provide your reason:")
                        reason = input().strip()
                        print("[Human Interaction(Test Case assessment)]🌷 Thank you for your feedback!")
                        continue
                    elif user_choice == "y":
                        # print("✨🌸 We begin validating the scenario test case 🌸✨")
                        # print("🔧 Do you want to modify the scenario? Enter your advice (If no modification, type No): ✨", end=" ")
                        # modify_content = input().strip().lower()
                        # print("✨🌸--------------------🌸✨")
                        # print("[TestCaseGenerationAgent] 🏗️ Validating modified Gherkin test cases...")
                        # if modify_content.lower() == "no" or not modify_content:
                        #     test_cases = self.test_case_generation_agent.validate_test_cases(
                        #         requirement['description'], scenario, point_context_manager
                        #     )
                        # else:
                        #     test_cases = self.test_case_generation_agent.validate_test_cases(
                        #         requirement['description'], scenario, point_context_manager, modify_content
                        #     )
                        # print("✨🌟--------------------🌟✨\n\n")
                        # _, scenarios = self.test_case_generation_agent.split_scenarios(test_cases)
                        # scenario = scenarios[0]
                        print("🔧 Do you want to modify the scenario? (y/n) ✨", end=" ")
                        modify_choice = input().strip().lower()

                        if modify_choice == "y":
                            print("✍️ Please enter the modified scenario, type 'END' to finish (multi-line supported):")
                            lines = []
                            while True:
                                line = input()
                                if line.strip().upper() == "END":
                                    break
                                lines.append(line)
                            modified_scenario = "\n".join(lines).strip()
                            if modified_scenario:
                                scenario = modified_scenario

                        new_scenarios.append(scenario)
                        test_cases = [feature_header + '\n\n' + scenario]
                        print("✨🌸--------------------------------[Human Interaction(Test Case assessment)] end--------------------------------🌸✨")
                        print('\n')

                    point_context_manager.add_message("assistant", '\n\n'.join(test_cases), "TestCaseGenerationAgent")


                    print("[StepImplementationAgent] ⚙️ Generating step.py implementation...")
                    print("✨🌟--------------------------------[StepImplementationAgent] begin --------------------------------🌟✨")
                    steps = self.step_implementation_agent.implement_steps(main_page_root, point_context_manager)
                    point_context_manager.add_message("assistant", steps, "StepImplementationAgent")
                    print("✨🌟--------------------------------[StepImplementationAgent] end --------------------------------🌟✨")
                    print('\n')

                    # test runner agent
                    print("✨🌟--------------------------------[TestRunnerAgent(dry-run)] begin --------------------------------🌟✨")
                    for attempt in range(3):
                        print(f"[TestRunnerAgent(dry-run)] ✨🚀 **unning tests (attempt {attempt + 1}/3)...**")
                        self.test_runner_agent.save_test_files(test_cases, steps, project_root, idx)
                        test_result = self.test_runner_agent.run_dry_run(project_root)
                        print('\n')
                        point_context_manager.add_message("assistant", test_result, "TestRunnerAgent")

                        if "No Faults" in test_result:
                            print("[TestRunnerAgent(dry-run)] 🎉 Tests passed!")
                            break
                        else:
                            print("❌[StepImplementationAgent(fix1)] ** Tests failed , fix step.py... 😕**")
                            print("✨🌟--------------------------------[StepImplementationAgent(fix1)] begin --------------------------------🌟✨")
                            steps, point_context_manager = self.step_implementation_agent.fix_steps(main_page_root,
                                                                                                    point_context_manager)
                            print(
                                "✨🌟--------------------------------[StepImplementationAgent(fix1)] end --------------------------------🌟✨")
                            print('\n')

                    print(f"[TestRunnerAgent(dry-run)]✨🚀 **Attempted to run tests {attempt + 1} times.**")
                    print("✨🌟--------------------------------[TestRunnerAgent(dry-run)] end --------------------------------🌟✨")


                    point_context_manager_2 = copy.deepcopy(context_manager_based)
                    point_context_manager_2.add_message("assistant", json.dumps(test_cases), "TestCaseGenerationAgent")
                    point_context_manager_2.add_message("assistant", steps, "StepImplementationAgent")

                    print("✨🌟--------------------------------[TestRunnerAgent(run-behave)] begin --------------------------------🌟✨")
                    for attempt in range(6):
                        print(f"[TestRunnerAgent(run-behave)] ✨🛠 **Behave log analyze post-test fix (run tests) (try {attempt + 1}/6)...**")
                        self.test_runner_agent.save_test_files(test_cases, steps, project_root, idx)
                        behave_log = self.test_runner_agent.run_tests(project_root, return_log=True)
                        print('\n')
                        print('[BehaveLogAnalysisAgent]✨📑 **Start analyzing Behave test logs...**')
                        print(
                            "✨🌟--------------------------------[BehaveLogAnalysisAgent] begin --------------------------------🌟✨")
                        if self.behave_log_analysis_agent.wether_all_passed(behave_log):
                            print("✅ **All tests passed!** 🎉")
                            break
                        print("[BehaveLogAnalysisAgent] ❌ **Test failed, analyze the error message...**")
                        failed_scenarios = self.behave_log_analysis_agent.analyze_log(behave_log)
                        print(
                            "✨🌟--------------------------------[BehaveLogAnalysisAgent] end --------------------------------🌟✨")
                        print('\n')
                        point_context_manager_2.add_message("assistant", 'The behave log fail information is: \n' + json.dumps(
                            failed_scenarios), "BehaveLogAnalysisAgent")

                        print("✨🌸--------------------------------[Human Interaction(Step.py Assessment)] begin--------------------------------🌸✨")
                        print("⚠️ **Do you want to keep this step.py? It is a defect of the original project, but there is no problem with the test case (y/n)✨**\n", end=" ")
                        user_choice = input().strip().lower()  
                        if user_choice == "y":
                            print("✅ Selected to keep step.py file. \n")
                            break  
                        print("⚠️ **Do you need to manually fix step.py and feature files? (y/n) ✨**", end=" ")
                        user_choice = input().strip().lower()
                        if user_choice == "y":
                            print("📝 **Please modify step.py manually, and press Enter to continue...**")
                            input()
                            test_cases, steps = self.test_runner_agent.read_test_files(idx)
                            print("✨🌸--------------------------------[Human Interaction(Step.py Assessment)] end--------------------------------🌸✨")
                            print('\n')
                        else:
                            print("[StepImplementationAgent(fix2)] Fix step.py... 😕**")
                            print(
                                "✨🌟--------------------------------[StepImplementationAgent(fix2)] begin --------------------------------🌟✨")
                            steps, point_context_manager_2 = self.step_implementation_agent.fix_steps(main_page_root,
                                                                                                      point_context_manager_2,
                                                                                                      behave_state=True)
                            print(
                                "✨🌟--------------------------------[StepImplementationAgent(fix2)] end --------------------------------🌟✨")
                            print('\n')

                    print(f"✨🚀 [TestRunnerAgent(run-behave)] Test passed in {attempt + 1} attempts.**")
                    print(
                        "✨🌟--------------------------------[TestRunnerAgent(run-behave)] end --------------------------------🌟✨")
                    print('\n')
                    tmp_test_dict={
                        'test_case': test_cases,
                        'step_code': steps
                    }
                    test_info_lst.append(tmp_test_dict)
                    print('[StepComponentLocatorAgent]✨🦋 **Start extracting components from step.py...**')
                    print(
                        "✨🌟--------------------------------[StepComponentLocatorAgent] begin --------------------------------🌟✨")
                    tmp_related_elements = self.step_component_locator_agent.extract_locators(steps)
                    print(
                        "✨🌟--------------------------------[StepComponentLocatorAgent] end --------------------------------🌟✨")
                    print('\n')
                    related_elements.extend(tmp_related_elements)

            related_elements = list(set(related_elements))
            tmp_context_manager = copy.deepcopy(context_manager_based)
            tmp_context_manager.add_message("assistant", feature_header+'\n\n'+'\n\n'.join(new_scenarios), "TestCaseGenerationAgent")
            # tmp_context_manager.add_message("assistant", steps, "StepImplementationAgent")
            print("✨[RequirementAgent] 🚀 **Correction needs to start...**")
            print(
                "✨🌟--------------------------------[RequirementAgent] begin --------------------------------🌟✨")
            concise_req = requirement['description']
            requirement = self.requirement_extraction_agent.modify_req(requirement['description'], tmp_context_manager)
            print(
                "✨🌟--------------------------------[RequirementAgent] end --------------------------------🌟✨")
            print('\n')
            requirement['related_elements'] = related_elements
            print("✨🌸--------------------------------[Human Interaction(Rewrite Requirement)] begin--------------------------------🌸✨")
            print("⚠️ **Do you need to manually modify the requirement? (y/n) ✨**", end=" ")

            user_choice = input().strip().lower()
            if user_choice == "y":
                print("📝 **Please enter the revised requirement (press Enter to remain unchanged):**\n")
                modified_req = input().strip()
                if modified_req:
                    try:
                        requirement['description'] = json.loads(modified_req)['description']  
                    except json.JSONDecodeError:
                        print("❌ **The input format is incorrect! Keep the original requirement unchanged.**")
                else:
                    print("✅ **Keep the original requirement unchanged. **")
            else:
                print("✅ **Keep the original requirement unchanged. **")
            print("✨🌸--------------------------------[Human Interaction(Rewrite Requirement)] end--------------------------------🌸✨")
            print('\n')
            print('The final requirement is:')
            print(requirement)
            print('\n')

            annotation_dict[req_idx] = {
                'requirement': requirement,
                'concise_requirement': concise_req,
                'test_cases': test_info_lst
            }

            # save annotation_dict in project_root as json
            with open(os.path.join(project_root, "annotation.json"), "w", encoding="utf-8") as f:
                json.dump(annotation_dict, f, indent=4)
            print("[MultiAgentSystem] 📂 annotation.json The file is saved to the project directory.")

        print("[MultiAgentSystem] 🎉 Complete the testing process for all requirements!")


# example
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current Directory: {current_dir}")
    project_up_folder = os.path.normpath(os.path.join(current_dir, '..','..', 'E2EDev_data_withTestID'))
    # Initialize the multi-agent system
    chat_context_manager = ChatContextManager()
    data_gen_MAS = MultiAgentSystem(chat_context_manager, config.MODEL)

    # Make sure the top-level directory exists
    if not os.path.exists(project_up_folder):
        print(f"❌ Directory does not exist: {project_up_folder}")
        exit()

    for entry in os.scandir(project_up_folder):
        if not entry.is_dir():  
            continue

        # if '_06' not in entry.name:
        #     continue

        project_root = entry.path
        print(f"📂 Processing Project: {entry.name}")

        # Read all HTML and JS files
        html_files = []
        js_files = []
        main_page_path = None  #Store the path to index.html

        for root, _, files in os.walk(project_root):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        if file.endswith(".html"):
                            html_files.append(f.read())
                            if file == "index.html": 
                                main_page_path = file_path
                        elif file.endswith(".js") and "min.js" not in file:
                            js_files.append(f.read())
                except Exception as e:
                    print(f"⚠️ Unable to read file {file_path}: {e}")

        if main_page_path:
            print(f"✅ Found main page: {main_page_path}")
        else:
            print("❌ No index.html found in this project.")

        data_gen_MAS.run(html_files, js_files, project_root, main_page_path)

        # 打印或存储结果
        print(f"✅ Processing completed: {entry.name}")



