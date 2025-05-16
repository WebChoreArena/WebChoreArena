import json
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('result_path', type=str, default='/')
    args = parser.parse_args()
    return args

def get_result(base_dir):
    folder_paths = [base_dir + "/" + dir for dir in os.listdir(base_dir) if dir.startswith('web')]
    task_ids = [int(folder.split(".")[-1]) for folder in os.listdir(base_dir) if folder.startswith('web')]
    folder_score_dict = {}
    error_folder_dict = {}
    
    for folder in folder_paths:
        with open(folder + "/summary_info.json") as f:
            summary_info = json.load(f)
            score = summary_info["cum_reward"]
            folder_score_dict[folder] = score
            if summary_info["err_msg"]:
                error_folder_dict[folder] = summary_info["err_msg"]
    return folder_score_dict, error_folder_dict, task_ids


def calculate_mean_score(folder_score_dict, middle=None):
    if middle is None:
        mean_score = sum(list(folder_score_dict.values())) / len(folder_score_dict)
        return mean_score
    else:
        sum_value = sum(list(folder_score_dict.values())[:middle])
        mean_score = sum_value / middle
        return mean_score


def main(args):
    score_dict, error_folder_dict, done_task = get_result(args.result_path)
    print(calculate_mean_score(score_dict), len(score_dict))
    print("error_folder: ", error_folder_dict)
    
    config_mapping = {
        "shopping_admin": "config_files/test_shopping_admin.raw.json",
        "shopping": "config_files/test_shopping.raw.json",
        "gitlab": "config_files/test_gitlab.raw.json",
        "reddit": "config_files/test_reddit.raw.json",
        "cross": "config_files/test_cross.raw.json",
    }

    task_ids = []
    for key, config_file in config_mapping.items():
        if key in args.result_path:
            try:
                with open(config_file) as f:
                    all_configs = json.load(f)
                task_ids = [config["task_id"] for config in all_configs]
                break
            except FileNotFoundError:
                print(f"Warning: Config file {config_file} not found.")
                return
    if task_ids:
        for task in task_ids:
            if task not in done_task:
                print(f"{task} is not in the result folder.")
    else:
        print(f"Warning: No corresponding config file found for result_path '{args.result_path}'.")

    
if __name__ == '__main__':
    args = parse_args()
    main(args)