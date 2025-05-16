import json
import os
import argparse


def ArgParser():
    parser = argparse.ArgumentParser(description="Error check for the results")
    parser.add_argument("base_dir", type=str, default=None, help="Base directory for the results")
    return parser.parse_args()


def main(args):
    base_dir = args.base_dir

    dir_list = [base_dir + "/" + _dir + "/summary_info.json" for _dir in os.listdir(base_dir) if _dir.startswith("web")]
    summary_infos = [json.load(open(_dir)) for _dir in dir_list]
    print(summary_infos[0])

    error_list = [info["err_msg"] for info in summary_infos if info["err_msg"] is not None]
    memory_error_list = [error for error in error_list if "memory" in error]
    response_error_list = [error for error in error_list if "response" in error]
    crash_error_list = [error for error in error_list if "crash" in error]
    after_4_retries_list = [error for error in error_list if "Could not parse a valid value after 4 retries" in error]

    for ind, summary_info in enumerate(summary_infos):
        if summary_info["err_msg"] is not None:
            print(f"Error in {dir_list[ind]}: {summary_info['err_msg']}")

    print("Number of errors: ", len(error_list))
    print("Number of memory errors: ", len(memory_error_list))
    print("Number of response errors: ", len(response_error_list))
    print("Number of crash errors: ", len(crash_error_list))
    print("Number of after 4 retries errors: ", len(after_4_retries_list))


if __name__ == "__main__":
    args = ArgParser()
    main(args)
