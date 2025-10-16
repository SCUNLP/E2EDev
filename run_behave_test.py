import os
import json
import shutil
import subprocess
import sys
import re
import psutil
from datetime import datetime



def main(project_folder,log_folder,save_res_folder):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    WAREHOUSE_PATH = os.path.normpath(os.path.join(current_dir, 'E2EDev_data'))

    # Get all project names (folder names)
    program_idx_lst = [
        d for d in os.listdir(WAREHOUSE_PATH)
        if os.path.isdir(os.path.join(WAREHOUSE_PATH, d))
    ]

    # Iterate through each project
    for program_idx in program_idx_lst:
        print(f"\n=== 🚀 Start the test project:{program_idx} ===")

        test_case_path = os.path.join(WAREHOUSE_PATH, program_idx, 'requirment_with_tests.json')
        test_case_project_path = os.path.join(WAREHOUSE_PATH, program_idx,'source_projcet')

        project_root = os.path.join(project_folder, program_idx)
        # if not exist then continue
        if not os.path.exists(project_root):
            print(f"[⚠️] {project_root} not exist, skip")
            continue
        features_dir = os.path.join(project_root, 'features')
        steps_dir = os.path.join(features_dir, 'steps')

        log_path =os.path.join(log_folder, f'{program_idx}_behave.log')
        if not os.path.exists(log_path):
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        save_res_path = os.path.join(save_res_folder, f'{program_idx}_behave.json')

        # Clear the features directory
        if os.path.exists(features_dir):
            shutil.rmtree(features_dir)
        os.makedirs(steps_dir, exist_ok=True)

        # Reading JSON File
        try:
            with open(test_case_path, 'r', encoding='utf-8') as f:
                test_info_dict = json.load(f)
        except FileNotFoundError:
            print(f"[⚠️] annotation.json not found in {program_idx}, skip this item")
            continue

        # Find the HTML file path
        html_path = None
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith(".html"):
                    html_path = os.path.join(root, file)
                    break
            if html_path:
                break

        if not html_path:
            print(f"[❌] HTML file not found, skipping item {program_idx}")
            continue

        # Copy all files except js/html/css/log/json files
        excluded_exts = {'.js', '.html', '.css', '.log'}
        excluded_files = {'annotation.json', 'annotation_o.json', 'requirements.json'}
        excluded_dirs = {'info', 'features'}

        for root, dirs, files in os.walk(test_case_project_path):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in excluded_exts or file in excluded_files:
                    continue

                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, test_case_project_path)
                dst_path = os.path.join(project_root, rel_path)

                if not os.path.exists(dst_path):
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied: {src_path} -> {dst_path}")

        behave_log_summary = {}

        for req_id, value in test_info_dict['finegrained_rewith_test'].items():
            test_cases = value['test_cases']
            behave_log_summary[req_id] = {}

            for idx, test_case in enumerate(test_cases):
                gherkin = test_case['test_case'][0]
                step_code = test_case['step_code']

                step_code = re.sub(r'file_path\s*=\s*"[^"]*"', f'file_path = "{html_path}"', step_code)
                step_code = re.sub(r'file://[^"\']+', f'file://{html_path}', step_code)
                step_code = re.sub(r'file_path_placeholder\s*=\s*\'[^\']*\'', f'file_path = "{html_path}"', step_code)
                need_time_projects = ['E2ESD_Bench_27', 'E2ESD_Bench_37', 'E2ESD_Bench_21', 'E2ESD_Bench_05']
                if program_idx not in need_time_projects:
                    step_code = re.sub(r'time\.sleep\s*\(\s*\d+(\.\d+)?\s*\)', 'time.sleep(0.5)', step_code)
                feature_file = os.path.join(features_dir, 'features.feature')
                step_file = os.path.join(steps_dir, 'steps.py')

                with open(feature_file, 'w', encoding='utf-8') as f:
                    f.write(gherkin)
                with open(step_file, 'w', encoding='utf-8') as f:
                    f.write(step_code)

                # Search Chrome PID
                existing_pids = {p.info['pid'] for p in psutil.process_iter(['pid', 'name']) if
                                 'chrome' in p.info['name'].lower() or 'chromedriver' in p.info['name'].lower()}

                print(f"[TestRunnerAgent] 🚀 Executing the test {req_id}_{idx}")
                result = subprocess.run(
                    [sys.executable, "-m", "behave"],
                    cwd=project_root,
                    capture_output=True,
                    text=True
                )

                print(result.stdout)
                behave_log_summary[req_id][idx] = 'pass' if '1 feature passed' in result.stdout else 'fail'

                new_pids = {
                    p.info['pid'] for p in psutil.process_iter(['pid', 'name'])
                    if ('chrome' in p.info['name'].lower() or 'chromedriver' in p.info['name'].lower()) and p.info[
                        'pid'] not in existing_pids
                }

                for pid in new_pids:
                    try:
                        psutil.Process(pid).kill()
                        print(f"[TestRunnerAgent] 🔒 Chrome process closed: PID {pid}")
                    except Exception as e:
                        print(f"[TestRunnerAgent] ⚠️ Unable to close process {pid}: {e}")

                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"\n=== Testing {req_id}_{idx} at {datetime.now()} ===\n")
                    log_file.write(result.stdout)
                    log_file.write("\n=== End ===\n")

        with open(save_res_path, 'w', encoding='utf-8') as f:
            json.dump(behave_log_summary, f, ensure_ascii=False, indent=4)

        print(f"✅ Project {program_idx} Test completed, results saved to {save_res_path}")

if __name__=='__main__':

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(current_dir, 'For_Behave_Warehouse(TestOnly)'))
    log_folder = os.path.join(project_root,'behave_logs')
    save_res_folder = os.path.join(project_root,'behave_results')
    # if not exist mkdir
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    if not os.path.exists(save_res_folder):
        os.makedirs(save_res_folder)
    main(project_root, log_folder, save_res_folder)

    # project_root = f'{data_path}/models/gpt-engineer/projects/qwen70b'
    # log_path = f'{data_path}/gen_log/E2ESD_log/gpt-engineer/qwen70b_behave.log'
    # save_res_path = f'{data_path}/data/Ourdatas/Result/gpt4o/gpt-engineer/qwen70b_behave.json'
    # main(project_root, log_path, save_res_path)

    # llm_models = ["gpt4o","gpt4omini","qwen7b","qwen70b","qwenmax"]
    # llm_based_project_root= f'{data_path}/models/LLM_base/E2ESD_data"
    # for llm_model in llm_models:
    #     print(f"=== 🚀 Start a test project LLM_Based : {llm_model} ===")
    #     project_root = os.path.join(llm_based_project_root, llm_model)
    #     # if not exists then continue
    #     if not os.path.exists(project_root):
    #         print(f"[⚠️] {project_root} not exist, skip")
    #         continue
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result/",llm_model,"llmbased")
    #     # if not exists then mkdir
    #     if not os.path.exists(save_res_folder):
    #         os.makedirs(save_res_folder)
    #     log_folder = os.path.join(f'{data_path}/gen_log/E2ESD_log/LLMBase",llm_model)
    #     main(project_root, log_folder, save_res_folder)

    # self collaboration
    # llm_models_self =['gpt-4o','gpt-4o-mini','qwen2.5-7b-instruct','qwen2.5-72b-instruct','qwen-max-2025-01-25']
    # # map to llm_models
    # llm_models_self2llm_models={
    #     'gpt-4o':'gpt4o',
    #     'gpt-4o-mini':'gpt4omini',
    #     'qwen2.5-7b-instruct':'qwen7b',
    #     'qwen2.5-72b-instruct':'qwen70b',
    #     'qwen-max-2025-01-25':'qwenmax'
    # }
    #
    # self_colla_project_root = f'{data_path}/models/Self-collaboration-Code-Generation/data/E2ESD"
    # for llm_model in llm_models_self:
    #     print(f"=== 🚀 Start a test project Self-Collaboration :{llm_model} ===")
    #     project_root = os.path.join(self_colla_project_root, llm_model)
    #     # if not exist then continue
    #     if not os.path.exists(project_root):
    #         print(f"[⚠️] {project_root} not exist, skip")
    #         continue
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result/",llm_models_self2llm_models[llm_model],"Self-collaboration-Code-Generation")
    #     # if not exists then mkdir
    #     if not os.path.exists(save_res_folder):
    #         os.makedirs(save_res_folder)
    #     log_folder = os.path.join(f'{data_path}/gen_log/E2ESD_log/self-collaboration",llm_models_self2llm_models[llm_model])
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result",llm_models_self2llm_models[llm_model],"Self-collaboration-Code-Generation")
    #     main(project_root, log_folder, save_res_folder)

    # mapcoder
    # llm_models = ["qwen7b", "qwen70b", "qwenmax"]
    # llm_models = ["gpt4o","gpt4omini"]
    # mapcoder_project_root = f'{data_path}/models/MapCoder/outputs/E2ESD"
    # for llm_model in llm_models:
    #     print(f"=== 🚀 Start a test project MapCoder :{llm_model} ===")
    #     project_root = os.path.join(mapcoder_project_root, llm_model)
    #     # if not exist then continue
    #     if not os.path.exists(project_root):
    #         print(f"[⚠️] {project_root} not exist, skip")
    #         continue
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result/",llm_model,"MapCoder")
    #     # if not exists then mkdir
    #     if not os.path.exists(save_res_folder):
    #         os.makedirs(save_res_folder)
    #     log_folder = os.path.join(f'{data_path}/gen_log/E2ESD_log/MapCoder",llm_model)
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result",llm_model,"MapCoder")
    #     main(project_root, log_folder, save_res_folder)

    # # chatdev
    # llm_models = ["gpt4o","gpt4omini","qwen70b","qwenmax","qwen7b"]
    # chatdev_project_root = f'{data_path}/models/ChatDev/E2ESD_WareHouse"
    # for llm_model in llm_models:
    #     print(f"=== 🚀 Start a test project ChatDev :{llm_model} ===")
    #     project_root = os.path.join(chatdev_project_root, llm_model)
    #     # if not exist then continue
    #     if not os.path.exists(project_root):
    #         print(f"[⚠️] {project_root} not exist, skip")
    #         continue
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result/",llm_model,"ChatDev")
    #     # if not exists then mkdir
    #     if not os.path.exists(save_res_folder):
    #         os.makedirs(save_res_folder)
    #     log_folder = os.path.join(f'{data_path}/gen_log/E2ESD_log/Chatdev",llm_model)
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result",llm_model,"ChatDev")
    #     main(project_root, log_folder, save_res_folder)
    #
    # # metagpt
    # llm_models = ["qwenmax","gpt4o","gpt4omini","qwen7b","qwen70b"]
    # metagpt_project_root = f'{data_path}/models/MetaGPT/warehouse_e2esd"
    # for llm_model in llm_models:
    #     print(f"=== 🚀 Start a test project MetaGPT :{llm_model} ===")
    #     project_root = os.path.join(metagpt_project_root, llm_model)
    #     # if not exist then continue
    #     if not os.path.exists(project_root):
    #         print(f"[⚠️] {project_root} not exist, skip")
    #         continue
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result/",llm_model,"MetaGPT")
    #     # if not exists then mkdir
    #     if not os.path.exists(save_res_folder):
    #         os.makedirs(save_res_folder)
    #     log_folder = os.path.join(f'{data_path}/gen_log/E2ESD_log/metagpt",llm_model)
    #     save_res_folder = os.path.join(f'{data_path}/data/Ourdatas/Result",llm_model,"MetaGPT")
    #     main(project_root, log_folder, save_res_folder)

