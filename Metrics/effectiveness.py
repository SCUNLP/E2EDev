import json
import os

def main(folder_path):
    req_right_rate = []
    test_case_right_rate = []
    final_score_lst =[]
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            all_req_num = len(data)
            all_test_cases_num = 0
            all_true_req_num = 0
            all_true_test_cases_num = 0

            for req_id, req_data in data.items():
                all_test_cases_num += len(req_data)
                req_passed = True
                for test_result in req_data.values():
                    if test_result == 'pass':
                        all_true_test_cases_num += 1
                    else:
                        req_passed = False
                if req_passed:
                    all_true_req_num += 1

            req_right_rate.append(all_true_req_num / all_req_num)
            test_case_right_rate.append(all_true_test_cases_num / all_test_cases_num)
            # 计算最终得分
            final_score = (all_true_req_num / all_req_num) * 0.6 + (all_true_test_cases_num / all_test_cases_num) * 0.4
            final_score_lst.append(final_score)

    req_pass  = sum(req_right_rate) / len(req_right_rate)
    test_case_pass = sum(test_case_right_rate) / len(test_case_right_rate)
    final_score = sum(final_score_lst) / len(final_score_lst)
    return sum(req_right_rate) / len(req_right_rate), sum(test_case_right_rate) / len(test_case_right_rate) , final_score

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current Directory: {current_dir}")
    res_folder_path = os.path.normpath(os.path.join(current_dir, '..', 'For_Behave_Warehouse(TestOnly)/behave_results'))
    req_acc, case_acc, final_score = main(res_folder_path)
    all_results = {
        "req_accuracy": f"{req_acc:.4f}",
        "test_case_accuracy": f"{case_acc:.4f}",
        "final_score": f"{final_score:.4f}"
    }
    print(f"Results: {all_results}")

