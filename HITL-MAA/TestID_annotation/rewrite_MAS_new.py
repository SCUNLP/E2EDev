import os
from openai import OpenAI
import tiktoken
from bs4 import BeautifulSoup
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config
Model_name = config.MODEL


def add_data_testid_to_html(html_content):
    """
    Add corresponding `data-testid` attributes to all elements with an `id` attribute in the HTML content.

    Args:
        html_content (str): Original HTML content.

    Returns:
        str: Modified HTML content.
    """
    try:
         # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Traverse all elements with an id attribute
        modified = False
        for element in soup.find_all(attrs={"id": True}):
            id_value = element["id"]
            if "data-testid" not in element.attrs:  # Avoid duplicate additions
                element["data-testid"] = id_value  # Add data-testid
                modified = True

        # Return the modified HTML content
        return str(soup), modified

    except Exception as e:
        print(f"An error occurred: {e}")
        return html_content, False

def extract_code_blocks(text, language):
    """
    Extract code block content of the specified language.
    
    :param text: String containing code blocks
    :param language: Code language, such as 'html', 'js', 'css'
    :return: Extracted code string
    """
    pattern = rf"```{language}\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    return "\n".join(matches) if matches else None

class ChatContextManager:
    def __init__(self):
        self.context = []

    def add_message(self, role, content, name=None):
        """Store the full context, distinguishing different Agents"""
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



class CodeModificationAgent:
    def __init__(self,context_manager,model_name):
        self.context_manager = context_manager
        self.model_name = model_name
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.encoding = tiktoken.encoding_for_model('gpt-4o')

        self.system_prompt = """
        You are an automation tool tasked with adding `data-testid` attributes in the provided HTML and JavaScript files. Your job is to ensure that all interactive and display components have unique, meaningful identifiers while preserving the original code's functionality, structure, and behavior. When making changes, you must adhere to the following rules:

        1. **Preserve Original Code Logic & Structure**:
           - Only add `data-testid` attributes to components without modifying the original code.
           - Do not modify the existing functionality, structure, or behavior of the code.

        2. **Interactive Components (`data-testid` Assignment)**:
           - Assign a `data-testid` to any interactive component that lacks one, including `button`, `input`, `select`, `textarea`, `a`, `label`, `link`, etc.
           - **If an element already has an `id`, it must also have a `data-testid` with the same value or an appropriate variation**.
           - If an element **already has a `data-testid`**, modify it only if it does **not** conform to the naming convention.

        3. **Naming Convention for `data-testid`s**:
           - Use clear and meaningful names that describe the element's purpose or role.
           - Example:
             - `submit-button`: A button used to submit a form.
             - `active-menu-item`: A menu item that is currently active.
             - `close-modal-button`: A button used to close a modal.

        4. **Ensure Unique `data-testid`s**:
           - If multiple similar elements exist, append an increasing number (e.g., `menu-item-1`, `menu-item-2`).

        5. **Output**:
           - Provide the rewritten HTML and JavaScript files with correctly assigned `data-testid`s.
           - Maintain the original code structure and logic while ensuring compliance with the naming rules.
           - **No modifications to the CSS files are required**.

        **Limitations**:
        - Do not change the code structure: Only add `data-testid` attributes. Do not refactor JavaScript logic or HTML structure.
        - Do not change functionality: Ensure that the original functionality and behavior remain unaffected; the only change should be the addition of the `data-testid`.
        - Maintain logical consistency: Even for dynamically generated elements, ensure that the addition of the `data-testid` does not impact JavaScript logic or event handling.
        """

    def modify_code(self, code, modification_type):
        """
        Modify the provided code by following specific rules.
        :param code: The input HTML/JS/CSS code to be modified
        :param modification_type: 'js_html' or 'css' to define the modification type
        :return: Modified code
        """
        if modification_type == 'js_html':
            return self.fill_user_prompt_for_js_html(code)
        elif modification_type == 'css':
            return self.fill_user_prompt_for_css(code)
        else:
            return "Invalid modification type."

    def fill_user_prompt_for_html(self, code, file_name):
        filled_prompt = f"""
        Please analyze the following HTML code and add `data-testid` attributes for all necessary components based on the rules provided in the system content.

        - If an element lacks a `data-testid`, generate one following the naming convention.
        - If an element already has a `data-testid`, rename it only if it does not conform to the convention.
        - Do not modify the structure, styles, or other attributes of the HTML.

        Here is the HTML code to analyze:

        **Original Code from {file_name}:**
        {code}

        **Modified Code:**
        ```html
        (Your modified HTML code here)
        ```
        """
        return filled_prompt

    def fill_user_prompt_for_js(self, code, file_name):
        filled_prompt = f"""
        Please analyze the following JavaScript code and ensure that all referenced components have a proper `data-testid`, while preserving functionality.

        - **Assign `data-testid` only if necessary:** 
          - If an element is accessed in JavaScript, ensure it has a valid `data-testid`.
          - **For dynamically created elements:**
            - **Single Instance**: If only one instance of a dynamically created element exists at a time, assign a unique `data-testid`.
            - **Multiple Instances**: If multiple elements of the same type are generated dynamically, use a unique identifier (e.g., `data-id`) instead of `data-testid` to avoid conflicts.
        - **Ensure consistency with HTML:** If an element's `data-testid` was modified in HTML, update all references in JavaScript to match.
        - **ABSOLUTELY NO CHANGES TO LOGIC OR STRUCTURE:** The script must function **EXACTLY** the same way after modifications.

        Here is the JavaScript code to analyze:

        **Original Code from {file_name}:**
        {code}

        **Modified Code:**
        ```javascript
        (Your modified JavaScript code here)
        ```
        """
        return filled_prompt

    def fill_user_prompt_for_css(self, code, file_name):
        filled_prompt = f"""
        Below is the CSS code. Your task is to modify **only the `id` names** while ensuring they are consistent with the corresponding `id`s in the HTML and JavaScript.

        - Verify that the updated `id` names are consistent with any related `class` names used in the associated HTML and JavaScript.

        **Original Code from {file_name}:**
        {code}

        **Modified Code:**
        ```css
        (Your modified CSS code here)
        ```
        """
        return filled_prompt

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

            modified_code = ""
            completion_tokens = 0

            for chunk in completion:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        modified_code += delta.content
                        print(delta.content, end="", flush=True)  # ✅ Make sure streaming output is visible
                        completion_tokens += len(self.encoding.encode(delta.content))

            print("\n✅ Response received!")  # Debug

            # Display token usage
            print("-------------- token usage --------------")
            print(f"🔠 Total Tokens: {completion_tokens + prompt_tokens}")  # Debug
            print(f"🔠 Prompt Tokens: {prompt_tokens}")
            print(f"🔠 Complete Tokens: {completion_tokens}")
            print("-------------- token usage --------------")

            return modified_code

        except Exception as e:
            print(f"❌ Error: {str(e)}")  # Debug Print Error
            return f"Error: {str(e)}"


# Subclass for JS/HTML modification
class HTMLCodeModificationAgent(CodeModificationAgent):
    def __init__(self, context_manager, model_name):
        super().__init__(context_manager, model_name)

    def modify_code(self, code, file_name):
        code = add_data_testid_to_html(code)[0]  # Add data-testid attribute
        user_prompt = self.fill_user_prompt_for_html(code, file_name)

        # 1️⃣ Store `user` message
        self.context_manager.add_message("user", user_prompt)

        # 2️⃣ Construct full context
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.context_manager.get_context())

        # 3️⃣ Call OpenAI to generate code
        modified_code = self.call_model_streaming(messages)

        # 4️⃣ Store reply from `js_html_agent`
        self.context_manager.add_message("assistant", modified_code, name="html_agent")

        return modified_code

class JSCodeModificationAgent(CodeModificationAgent):
    def __init__(self, context_manager, model_name):
        super().__init__(context_manager, model_name)

    def modify_code(self, code, file_name):
        user_prompt = self.fill_user_prompt_for_js(code, file_name)

        # 1️⃣ Store `user` message
        self.context_manager.add_message("user", user_prompt)

        # 2️⃣ Construct full context (including HTML modification result)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.context_manager.get_context())

        # 3️⃣ Call OpenAI to generate code
        modified_code = self.call_model_streaming(messages)

        # 4️⃣ Store reply from `js_agent`
        self.context_manager.add_message("assistant", modified_code, name="js_agent")

        return modified_code


# Subclass for CSS modification
class CSSCodeModificationAgent(CodeModificationAgent):
    def __init__(self, context_manager, model_name):
        super().__init__(context_manager, model_name)

    def modify_code(self, code, file_name):
        user_prompt = self.fill_user_prompt_for_css(code, file_name)

        # 1️⃣ Store `user` message
        self.context_manager.add_message("user", user_prompt)

        # 2️⃣ Construct full context (including JS/HTML modification result)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.context_manager.get_context())

        # 3️⃣ Call OpenAI to generate code
        modified_code = self.call_model_streaming(messages)

        # 4️⃣ Store reply from `css_agent`
        self.context_manager.add_message("assistant", modified_code, name="css_agent")

        return modified_code


class NamingConventionAgent:
    def __init__(self, context_manager,model_name):
        self.context_manager = context_manager
        self.model_name = model_name
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.system_prompt = """
        You are an expert in frontend architecture and naming conventions. Your task is to analyze the provided HTML, and JavaScript, which has already been modified to include `data-testid` attributes for testing purposes. Based on the modified code, summarize the naming conventions used for `data-testid` attributes and describe how elements are located in cases where `data-id` is used as an auxiliary attribute.

        ### **Task Instructions**
        1. **Analyze the Code**:
           - Review the provided code and identify the patterns used in naming `data-testid` attributes.
           - Determine whether `data-id` is used as an auxiliary attribute to locate dynamically generated elements.

        2. **Summarize Naming Rules**:
           - Extract and summarize the **`data-testid` naming rules** based on the patterns observed in the modified code.
           - If `data-id` is used, explain its role and how it complements `data-testid`.

        3. **Provide Structured Output**:
           - Return a structured JSON output that describes the naming rules and the purpose of each `data-testid` or `data-id` attribute.

        ### **Output Format**
        You must return the following JSON structure:
        ```json
        {
            "naming_rules": {
                "data_testid": "Summary of `data-testid` naming convention observed in the provided code.",
                "data_id": "Explanation of when and why `data-id` is used, if applicable."
            },
            "element_purpose": [
                {
                    "element": "The `data-testid` or `data-id` name",
                    "purpose": "Description of what this attribute is used for",
                    "element_type": "data-testid/data-id"
                },
                ...
            ]
        }
        """

    def call_model_streaming(self, messages):
        """Modify code using the streaming API"""
        try:
            print("🔹 Sending request to OpenAI API...")  # Debug log

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                top_p=1,
                stream=True  # Enable streaming response
            )

            modified_code = ""

            for chunk in completion:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        modified_code += delta.content
                        print(delta.content, end="", flush=True)  # ✅ Ensure streaming output is visible

            print("\n✅ Response received!")  # Debug
            return modified_code

        except Exception as e:
            print(f"❌ Error: {str(e)}")  # Debug print error
            return f"Error: {str(e)}"

    def naming_convention_summary(self):
        user_prompt = "Summarize the naming conventions used for `data-testid` attributes."

        # 1️⃣ Store the `user` message
        self.context_manager.add_message("user", user_prompt)

        # 2️⃣ Compose full context (including HTML/JS and CSS results)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.context_manager.get_context())

        # 3️⃣ Call OpenAI to generate the summary
        summary = self.call_model_streaming(messages)

        # 4️⃣ Store the response from `naming_agent`
        self.context_manager.add_message("assistant", summary, name="naming_agent")

        return summary

class MultiAgentSystem:
    def __init__(self, model_name):
        self.context_manager = ChatContextManager()
        self.html_agent = HTMLCodeModificationAgent(self.context_manager, model_name)
        self.js_agent = JSCodeModificationAgent(self.context_manager, model_name)
        self.css_agent = CSSCodeModificationAgent(self.context_manager, model_name)
        self.naming_agent = NamingConventionAgent(self.context_manager, model_name)

    def run(self, html_files, js_files, css_files):
        """Run the entire multi-agent system, supporting multiple HTML, JS, and CSS files"""

        modified_html_files = {}
        modified_js_files = {}
        modified_css_files = {}
        self.context_manager.clear_context()

        print("Step 1: Modifying HTML Files...")
        for file in html_files:
            file_name, file_content = file["file_name"], file["file_content"]
            print(f"\nProcessing HTML File: {file_name}...")
            modified_html = self.html_agent.modify_code(file_content, file_name)
            modified_html = extract_code_blocks(modified_html, "html")
            modified_html_files[file_name] = modified_html

        print("\nStep 2: Modifying JS Files...")
        for file in js_files:
            file_name, file_content = file["file_name"], file["file_content"]
            print(f"\nProcessing JS File: {file_name}...")
            modified_js = self.js_agent.modify_code(file_content, file_name)
            modified_js = extract_code_blocks(modified_js, "javascript")
            modified_js_files[file_name] = modified_js

        print("\nStep 3: Modifying CSS Files...")
        for file in css_files:
            file_name, file_content = file["file_name"], file["file_content"]
            print(f"\nProcessing CSS File: {file_name}...")
            # CSS modification is currently skipped
            # modified_css = self.css_agent.modify_code(file_content, file_name)
            # modified_css = extract_code_blocks(modified_css, "css")
            # modified_css_files[file_name] = modified_css
            modified_css_files[file_name] = file_content

        # print("\nStep 4: Summarizing Naming Conventions...")
        # naming_summary = self.naming_agent.naming_convention_summary()

        return modified_html_files, modified_js_files, modified_css_files


# === Test code ===
if __name__ == "__main__":
    html_files = [
        {"file_name": "index.html", "file_content": """
        <html>
            <head><title>Page 1</title></head>
            <body>
                <div id="header">Header</div>
                <button class="btn-primary">Click Me</button>
                <script src="script1.js"></script>
            </body>
        </html>
        """},
        {"file_name": "about.html", "file_content": """
        <html>
            <head><title>About Us</title></head>
            <body>
                <div id="footer">Footer</div>
                <button class="btn-secondary">Submit</button>
                <script src="script2.js"></script>
            </body>
        </html>
        """}
    ]

    js_files = [
        {"file_name": "script1.js", "file_content": """
        document.addEventListener("DOMContentLoaded", function() {
            var btn = document.querySelector('.btn-primary');
            btn.addEventListener('click', function() {
                alert('Button clicked!');
            });
        });
        """},
        {"file_name": "script2.js", "file_content": """
        document.addEventListener("DOMContentLoaded", function() {
            var btn = document.querySelector('.btn-secondary');
            btn.addEventListener('click', function() {
                alert('Form submitted!');
            });
        });
        """}
    ]

    css_files = [
        {"file_name": "styles1.css", "file_content": """
        #header { font-size: 20px; }
        .btn-primary { background-color: blue; }
        """},
        {"file_name": "styles2.css", "file_content": """
        #footer { font-size: 18px; }
        .btn-secondary { background-color: green; }
        """}
    ]

    mas = MultiAgentSystem(model_name='gpt-4o-mini')
    modified_html_files, modified_js_files, modified_css_files= mas.run(html_files, js_files, css_files)
    print('debug')
