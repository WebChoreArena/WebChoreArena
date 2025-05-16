import pandas as pd
import argparse


def ArgParse():
    parser = argparse.ArgumentParser(description="Calculate success rate from summary.csv")
    parser.add_argument(
        "csv_path",
        type=str,
        help="Path to the summary.csv file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = ArgParse()
    result = pd.read_csv(args.csv_path)
    success_rate = result["success"].sum() / len(result) * 100
    print(f"Success Rate: {success_rate:.2f}%")
