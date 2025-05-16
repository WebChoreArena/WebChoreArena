# load_config
import json
import os
import argparse


def ArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_dir", type=str)
    args = parser.parse_args()
    return args


def main(args):
    base_dir = args.base_dir
    dir_list = [base_dir + "/" + _dir for _dir in os.listdir(base_dir) if _dir.startswith("web")]
    dir_summary_list = [base_dir + "/" + _dir + "/summary_info.json" for _dir in os.listdir(base_dir) if _dir.startswith("web")]
    summary_infos = [json.load(open(_dir)) for _dir in dir_summary_list]

    for ind, summary_info in enumerate(summary_infos):
        if summary_info["err_msg"] is not None:
            print(f"Error in {dir_summary_list[ind]}: {summary_info['err_msg']}")
            if "Could not parse a valid value after 4 retries" not in summary_info["err_msg"]:
                target_path = dir_list[ind].replace("results", "trash/results")
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                save_path = dir_list[ind].replace("results", "trash/results")
                if not os.path.exists(save_path):
                    os.rename(dir_list[ind], save_path)
                else:
                    count = 2
                    while os.path.exists(save_path):
                        save_path += f"_{count}"
                        count += 1
                    print(f"{save_path} already exists. change the foldernames")
                    os.rename(dir_list[ind], save_path)
                print(f"Moved to {save_path}")


if __name__ == "__main__":
    args = ArgParser()
    main(args)
