import os
import shutil
from rewrite_MAS_new import MultiAgentSystem, Model_name


current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current Directory: {current_dir}")

# old_folder
old_folder = os.path.normpath(os.path.join(current_dir, '..','..', 'E2EDev_data'))
new_folder = os.path.normpath(os.path.join(current_dir, '..','..', 'E2EDev_data_withTestID'))

# Ensure the new folder exists
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

# Initialize MultiAgentSystem !!! For debugging use gpt-4o-mini, for official execution use gpt-4o
mas = MultiAgentSystem(model_name=Model_name)

# Traverse all projects under old_folder
for project in os.listdir(old_folder):
    if '2' not in project:
        continue
    old_project_path = os.path.join(old_folder, project,'source_projcet')

    # ✅ Only process folders
    if not os.path.isdir(old_project_path):
        print(f"❌ Skipping non-directory: {old_project_path}")
        continue
    # Print progress
    print(f"📂 Processing Project: {project}")

    new_project_path = os.path.join(new_folder, project)
    if not os.path.exists(new_project_path):
        os.makedirs(new_project_path)  # Ensure the new project folder exists

    html_files = []
    js_files = []
    css_files = []
    other_files = []  # For storing non-code files

    # ✅ Traverse the entire folder, including all subdirectories
    for root, dirs, files in os.walk(old_project_path):
        print(f"📂 Scanning: {root}")  # 🛠 Debug: Check whether all directories are entered

        for file in files:
            old_file_path = os.path.join(root, file)  # Full path of the old file
            relative_path = os.path.relpath(old_file_path, old_project_path)  # Only path after project
            new_file_path = os.path.join(new_project_path, relative_path)  # Full path of the new file

            # 🛠 Debug: See which files are being traversed
            print(f"📄 Found File: {relative_path}")

            # ✅ Read file content
            with open(old_file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # ✅ Classify HTML, JS, CSS files
            if file.endswith(".html"):
                html_files.append({"file_name": relative_path, "file_content": content})
            elif file.endswith(".js") and not file.endswith(".min.js"):
                js_files.append({"file_name": relative_path, "file_content": content})
            elif file.endswith(".css"):
                css_files.append({"file_name": relative_path, "file_content": content})
            else:
                other_files.append((old_file_path, new_file_path))  # Record non-code files

    # ✅ Call MAS to process HTML/JS/CSS code
    modified_html_files, modified_js_files, modified_css_files = mas.run(html_files, js_files, css_files)

    # ✅ Save modified files
    for file_name, file_content in modified_html_files.items():
        new_file_path = os.path.join(new_project_path, file_name)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    # Save modified JS files
    for file_name, file_content in modified_js_files.items():
        new_file_path = os.path.join(new_project_path, file_name)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)  # Ensure the directory exists
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    # Save modified CSS files
    for file_name, file_content in modified_css_files.items():
        new_file_path = os.path.join(new_project_path, file_name)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)  # Ensure the directory exists
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    # save naming_summary
    # with open(os.path.join(new_project_path, "naming_summary.txt"), "w") as f:
    #     f.write(naming_summary)

    # ✅ Copy non-code files
    for old_path, new_path in other_files:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)  # Ensure the parent directory exists
        shutil.copy2(old_path, new_path)


print("✅ All projects have been processed and saved to the new folder!")
