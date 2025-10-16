import os
import re
import json
import math
import statistics

folder_path_base = '/Users/lingyao/PycharmProjects/E2ESD_data_construct'
method_lstt = ['gpt4o', 'gpt4omini', 'qwen7b', 'qwen70b', 'qwenmax']
# method_lstt = ['qwen7b']
method = method_lstt[4]
llm_base_path = os.path.join(folder_path_base, 'models', 'gpt-engineer', 'projects', method)
log_path = os.path.join(folder_path_base, 'gen_log', 'E2ESD_log', 'gpt-engineer', method)


# --- 参数 ---
PARAMETERS = {
    "gpt4o": 200e9,
    "gpt4omini": 8e9,
    "qwen-2.5-7b": 7e9,
    "qwen-2.5-70b": 70e9,
    "qwen-2.5-max": 1000e9 * 0.0551,  # 5.51% of 1000B
    "qwen-qwq-plus": 40e9,  # Estimated based on Qwen-qwq-32B
}

FLOPS_PER_WATT = {
    "A100": 624e12,  # FP16 with sparsity (example, needs clarification in paper)
    "H100": 1700e12,
}

PUE = {
    "qwen": 1.2,
    "gpt": 1.1,
}

CARBON_INTENSITY = {
    "qwen": 625 / 1000,  # kg CO2e per kWh
    "gpt": 407 / 1000,  # kg CO2e per kWh
}

PRICING = {
    'gpt4o': {'input': 0.0025, 'output': 0.01},
    'gpt4omini': {'input': 0.00015, 'output': 0.0006},
    'qwen7b': {'input': 0.000069, 'output': 0.00014},
    'qwen70b': {'input': 0.00055, 'output': 0.0016},
    'qwenmax': {'input': 0.00033, 'output': 0.0013},
}

method2PRAMETERS = {
    'gpt4o': PARAMETERS['gpt4o'],
    'gpt4omini': PARAMETERS['gpt4omini'],
    'qwen7b': PARAMETERS['qwen-2.5-7b'],
    'qwen70b': PARAMETERS['qwen-2.5-70b'],
    'qwenmax': PARAMETERS['qwen-2.5-max'],
}

method2PRICING = {
    'gpt4o': PRICING['gpt4o'],
    'gpt4omini': PRICING['gpt4omini'],
    'qwen7b': PRICING['qwen7b'],
    'qwen70b': PRICING['qwen70b'],
    'qwenmax': PRICING['qwenmax'],
}

def calculate_operational_carbon(model_name, input_tokens, output_tokens, flops_w, pue_value, carbon_intensity_value):
    if model_name not in method2PRAMETERS:
        raise ValueError(f"Model name '{model_name}' not in parameters.")
    params = method2PRAMETERS[model_name]
    total_flops = 2 * (input_tokens + output_tokens) * params
    power_seconds = total_flops / flops_w
    power_kwh = power_seconds / 3600 / 1000
    energy = power_kwh * pue_value
    return energy * carbon_intensity_value

def calculate_carbon_footprint(model_family, model_name, input_tokens, output_tokens, hardware="H100", output_unit="mg"):
    operational_carbon = calculate_operational_carbon(
        model_name, input_tokens, output_tokens, FLOPS_PER_WATT[hardware], PUE.get(model_family, 1.0), CARBON_INTENSITY.get(model_family, 0)
    )
    conversion = 1e6 if output_unit.lower() == "mg" else 1.0
    unit = "mg CO2e" if output_unit.lower() == "mg" else "kg CO2e"
    embodied = {"name": "Embodied Carbon (Qualitative)", "explanation": "Embodied carbon is challenging to quantify..."}
    return {"operational_carbon": operational_carbon * conversion, "embodied_carbon": embodied, "unit": unit}

def calculate_cost(model_name, input_tokens, output_tokens):
    if model_name not in method2PRICING:
        return None, f"Error: Model '{model_name}' pricing not found."
    price = PRICING[model_name]
    input_cost = (input_tokens / 1000) * price['input']
    output_cost = (output_tokens / 1000) * price['output']
    return input_cost + output_cost, None

def analyze_code_lines(folder_path):
    codelines_lst = []
    if os.path.isdir(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path) and item.startswith("E2ESD_Bench"):
                print(f"Processing code folder: {item_path}")
                total_lines = 0
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith(('.html', '.css', '.js')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines = len(f.readlines())
                                    total_lines += lines
                                    print(f"  File: {file_path}, Lines: {lines}")
                            except UnicodeDecodeError:
                                try:
                                    with open(file_path, 'r', encoding='latin-1') as f:
                                        lines = len(f.readlines())
                                        total_lines += lines
                                        print(f"  File (latin-1): {file_path}, Lines: {lines}")
                                except Exception as e:
                                    print(f"  Error reading {file_path}: {e}")
                            except Exception as e:
                                print(f"  Error opening {file_path}: {e}")
                codelines_lst.append(total_lines)
    else:
        print(f"Error: Code folder not found at {folder_path}")

    if codelines_lst:
        print(f"\nCode lines - Min: {min(codelines_lst)}, Max: {max(codelines_lst)}, Mean: {sum(codelines_lst) / len(codelines_lst):.2f}")
    # return json
    return {
        "min": min(codelines_lst),
        "max": max(codelines_lst),
        "mean": sum(codelines_lst) / len(codelines_lst)
    }

def analyze_logs(folder_path, model_name):
    during_ms_lst = []
    completion_tokens_lst = []
    prompt_tokens_lst = []
    total_tokens_lst = []
    costs = []
    carbon_footprints_A100 = []
    carbon_footprints_H100 = []
    turns =[]

    if os.path.isdir(folder_path):
        for log_file in os.listdir(folder_path):
            if log_file.startswith("E2ESD_Bench_") and log_file.endswith(".log") and 'behave' not in log_file:
                log_file_path = os.path.join(folder_path, log_file)
                try:
                    with open(log_file_path, 'r') as f:
                        log_string = f.read()

                    # content 有多少<->， 就交流了多少次
                    turns_match = re.findall(r'<->', log_string)
                    if turns_match:
                        turns.append(len(turns_match))
                    else:
                        turns.append(0)

                    time_match = re.search(r'\*\*duration\*\*=\s*([\d.]+)\s*s', log_string)
                    if time_match:
                        during_ms_lst.append(float(time_match.group(1))*1000)

                    prompt_matches = re.findall(r'\*\*num_prompt_tokens\*\*=\s*(\d+)', log_string)
                    completion_matches = re.findall(r'\*\*num_completion_tokens\*\*=\s*(\d+)', log_string)


                    if prompt_matches:
                        prompt_tokens = int(prompt_matches[-1])
                        prompt_tokens_lst.append(prompt_tokens)
                        if completion_matches:
                            completion_tokens = int(completion_matches[-1])
                            completion_tokens_lst.append(completion_tokens)
                            total_tokens_lst.append(prompt_tokens + completion_tokens)
                            cost, err = calculate_cost(method, prompt_tokens, completion_tokens) # Adjust model name for pricing
                            if cost is not None:
                                costs.append(cost)
                                model_family = "gpt" if "gpt" in model_name else "qwen"
                                carbon_A100 = calculate_carbon_footprint(model_family, method, prompt_tokens, completion_tokens,hardware="A100",output_unit="mg")
                                carbon_H100 = calculate_carbon_footprint(model_family, method, prompt_tokens, completion_tokens, hardware="H100", output_unit="mg")
                                carbon_footprints_A100.append(carbon_A100['operational_carbon'])
                                carbon_footprints_H100.append(carbon_H100['operational_carbon'])

                except Exception as e:
                    print(f"Error reading log file {log_file}: {e}")

    metrics = {
        "duration (ms)": during_ms_lst,
        "completion_tokens": completion_tokens_lst,
        "prompt_tokens": prompt_tokens_lst,
        "total_tokens": total_tokens_lst,
        "cost (USD)": costs,
        "operational_carbon_A100 (mg CO2e)": carbon_footprints_A100,
        "operational_carbon_H100 (mg CO2e)": carbon_footprints_H100,
        "turns": turns,
    }

    results = {}

    for name, values in metrics.items():
        if values:
            min_val = min(values)
            max_val = max(values)
            mean_val = statistics.mean(values)
            print(f"{name} - Min: {min_val:.6f}" if isinstance(min_val, float) else f"{name} - Min: {min_val}",
                  end=", ")
            print(f"Max: {max_val:.6f}" if isinstance(max_val, float) else f"Max: {max_val}", end=", ")
            print(f"Mean: {mean_val:.6f}" if isinstance(mean_val, float) else f"Mean: {mean_val}")
            results[name] = {
                "min": min_val,
                "max": max_val,
                "mean": mean_val
            }

    return results

def ana_ping_log(log_path):
    ping_log_path = os.path.join(log_path, 'e2esd_chatdev.log')
    if not os.path.exists(ping_log_path):
        print(f"Ping log file not found at {ping_log_path}")
        return

    with open(ping_log_path, "r") as f:
        ping_output = f.read()  # 注意：使用 read() 而非 readlines()

    # 提取 time=xxx.xxx 的浮点数值
    latencies = [float(match) for match in re.findall(r'time=(\d+\.\d+)', ping_output)]

    if not latencies:
        print("No latency data found in ping log.")
        return

    result = {
        "min": min(latencies),
        "max": max(latencies),
        "mean": statistics.mean(latencies)
    }

    print("Ping log analysis completed.")
    print(f"Min latency: {result['min']:.3f} ms")
    print(f"Max latency: {result['max']:.3f} ms")
    print(f"Mean latency: {result['mean']:.3f} ms")

    return result

if __name__ == "__main__":
    res_dict = {}
    for method in method_lstt:
        llm_base_path = os.path.join(folder_path_base, 'models', 'ChatDev', 'E2ESD_WareHouse', method)
        log_path = os.path.join(folder_path_base, 'gen_log', 'E2ESD_log', 'ChatDev', method)
        print(f"Analyzing method: {method}")
        code_info = analyze_code_lines(llm_base_path)
        other_info = analyze_logs(log_path, method)
        ping_info = ana_ping_log(log_path)
        # Combine results
        all_info = {'code': code_info, 'log': other_info ,'ping': ping_info}
        print(all_info)
        res_dict[method] = all_info
    # Save results to JSON
    save_path = 'JSON_FILE_PATH'
    with open(save_path, 'w') as f:
        json.dump(res_dict, f, indent=4)
    print(f"Results saved to {save_path}")
