"""Replace the website placeholders with website domains from env_config
Generate the test data"""

import os
import json


def main() -> None:
    with open("test_shopping.raw.json", "r") as f:
        raw = f.read()
    raw = raw.replace("__GITLAB__", os.environ.get("GITLAB"))
    raw = raw.replace("__REDDIT__", os.environ.get("REDDIT"))
    raw = raw.replace("__SHOPPING__", os.environ.get("SHOPPING"))
    raw = raw.replace("__SHOPPING_ADMIN__", os.environ.get("SHOPPING_ADMIN"))
    raw = raw.replace("__WIKIPEDIA__", os.environ.get("WIKIPEDIA"))
    raw = raw.replace("__MAP__", os.environ.get("MAP"))
    with open("test_shopping.json", "w") as f:
        f.write(raw)
    # split to multiple files
    data = json.loads(raw)
    for idx, item in enumerate(data):
        sites = item["sites"]
        task_id = item["task_id"]
        if len(sites) > 1:
            dir = "cross_sites"
        else:
            dir = sites[0]
        if not os.path.exists(f"new_tasks/{dir}"):
            os.makedirs(f"new_tasks/{dir}/image")
            os.makedirs(f"new_tasks/{dir}/text")
        with open(f"new_tasks/{dir}/{task_id}.json", "w") as f:
            json.dump(item, f, indent=2)
        print(f"new_tasks/{dir}/{task_id}.json saved")
        if item["required_obs"] == "image":
            with open(f"new_tasks/{dir}/image/{task_id}.json", "w") as f:
                json.dump(item, f, indent=2)
        else:
            with open(f"new_tasks/{dir}/text/{task_id}.json", "w") as f:
                json.dump(item, f, indent=2)

if __name__ == "__main__":
    main()