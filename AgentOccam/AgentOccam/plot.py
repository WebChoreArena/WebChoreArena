import os
import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from AgentOccam.utils import COLOR_DICT, TASK_ID_DICT, MERGED_SITE_TASK_ID_DICT, EVELUATOR_RECTIFICATIONS, RUN_NAME_DICT, TASK_LABELS_MULTISITE, TRAJECTORY_DIR_DICT, OUTPUT_DIR, TOTAL_TASK_NUM_DICT


def random_color_generator():
    import random
    random.seed(65)
    while True:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        yield f'#{r:02X}{g:02X}{b:02X}'

def generate_random_colors(color_num):
    colors = [next(random_color_generator) for _ in range(color_num)]
    return colors

def get_colors(trajectory_key_list):
    return [COLOR_DICT[k] if k in COLOR_DICT else next(random_color_generator) for k in trajectory_key_list]

def parse_summary_csv_files(root_dir, site_list, mode="single_site"):
    total_reward = 0
    total_tasks = 0
    net_total_reward = 0

    id_list = []
    for site in site_list:
        if mode == "multiple_site":
            id_list += TASK_ID_DICT[site]
        elif mode == "single_site":
            id_list += MERGED_SITE_TASK_ID_DICT[site]

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file == 'summary.csv':
                filepath = os.path.join(subdir, file)
                with open(filepath, 'r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        task_id = int(row['task_id'])
                        if task_id in id_list:
                            total_tasks += 1
                            total_reward += float(row['reward'])
                            net_total_reward += 1 if float(row['reward']) == 1. else 0

    if total_tasks > 0:
        return total_reward, net_total_reward, total_tasks
    else:
        return 0.0, 0.0, 0.0 

def parse_json_files(root_dir, site_list, evaluator="after", mode="single_site"):
    total_reward = 0
    total_tasks = 0
    net_total_reward = 0

    id_list = []
    for site in site_list:
        if mode == "multiple_site":
            id_list += TASK_ID_DICT[site]
        elif mode == "single_site":
            id_list += MERGED_SITE_TASK_ID_DICT[site]

    for filename in os.listdir(root_dir):
        if filename.endswith(".json"):
            try:
                trajectory_obj = json.load(open(os.path.join(root_dir, filename), "r"))
                if trajectory_obj["id"] in id_list:
                    if (evaluator=="before" and trajectory_obj["id"] not in EVELUATOR_RECTIFICATIONS) or evaluator=="after":
                        if "trajectory" in trajectory_obj.keys():
                            last_step = trajectory_obj["trajectory"][-1]
                            reward = float(last_step['reward']) if "reward" in last_step.keys() else last_step['success']
                        else:
                            reward = trajectory_obj["score"]
                        total_tasks += 1
                        total_reward += reward
                        net_total_reward += 1 if reward == 1. else 0
            except Exception as e:
                print(os.path.join(root_dir, filename))
                print(e)

    if total_tasks > 0:
        return total_reward, net_total_reward, total_tasks
    else:
        return 0.0, 0.0, 0.0

def find_summary_csv_files(directories):
    summary_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file == 'summary.csv':
                    summary_files.append(os.path.join(root, file))
    return summary_files

def read_rewards_with_dir_names(summary_files):
    rewards_with_dirs = {}
    for file in summary_files:
        directory_name = os.path.basename(os.path.dirname(file))
        df = pd.read_csv(file)
        if 'reward' in df.columns:
            rewards_with_dirs[directory_name] = df['reward'].tolist()
    return rewards_with_dirs

def write_rewards_to_csv(rewards, output_file):
    with open(output_file, 'w') as f:
        f.write('reward\n')
        for reward in rewards:
            f.write(f'{reward}\n')

def load_reward(root_dir, evaluator="after"):
    reward_dict = {}
    net_reward_dict = {}
    for filename in os.listdir(root_dir):
        if filename.endswith(".json"):
            trajectory_obj = json.load(open(os.path.join(root_dir, filename), "r"))
            trajectory_id = trajectory_obj["id"]
            if (evaluator=="before" and trajectory_obj["id"] not in EVELUATOR_RECTIFICATIONS) or evaluator=="after":
                if "trajectory" in trajectory_obj.keys():
                    last_step = trajectory_obj["trajectory"][-1]
                    reward_dict[trajectory_id] = float(last_step['reward']) if "reward" in last_step.keys() else last_step['success']
                else:
                    reward_dict[trajectory_id] = float(trajectory_obj["score"])
                net_reward_dict[trajectory_id] = 1. if reward_dict[trajectory_id] == 1. else 0.
    reward_list = []
    net_reward_list = []
    print("\n"+root_dir)
    for i in range(812):
        if i in reward_dict.keys():
            reward_list.append(reward_dict[i])
        else:
            print(f"{i},", end="")
            # reward_list.append(-1)
            reward_list.append(0)
        if i in net_reward_dict.keys():
            net_reward_list.append(net_reward_dict[i])
        else:
            # net_reward_list.append(-1)
            net_reward_list.append(0)
    return reward_list, net_reward_list

def compare_rewards(trajectory_key_list=None, evaluator="after"):
    import pandas as pd

    basenames = [RUN_NAME_DICT[k] for k in trajectory_key_list]

    tasks = list(range(812))
    labels = TASK_LABELS_MULTISITE
    rewards = [load_reward(TRAJECTORY_DIR_DICT[k], evaluator=evaluator)[1] for k in trajectory_key_list]

    label_list = []
    label_index_dict = {}
    for i, label in enumerate(labels):
        if label not in label_list:
            label_list.append(label)
            label_index_dict[label] = []
        label_index_dict[label].append(i)
    sorted_index_list = []
    for label in label_list:
        sorted_index_list += label_index_dict[label]
    tasks = [tasks[i] for i in sorted_index_list]
    labels = [labels[i] for i in sorted_index_list]
    for i in range(len(rewards)):
        rewards[i] = [int(rewards[i][j]) for j in sorted_index_list]

    data = {
        'Task': tasks,
        'Site': labels,
        **{basename: reward for basename, reward in zip(basenames, rewards)}
    }

    df = pd.DataFrame(data)

    csvfile = open(os.path.join(OUTPUT_DIR, "compare.csv"), "w")
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["task", "site"]+basenames)
    for i, reward in enumerate(zip(*tuple(rewards))):
        csv_writer.writerow([df['Task'][i], df['Site'][i]]+list(reward))

def plot_comparative_heatmap():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    file_path = os.path.join(OUTPUT_DIR, 'compare.csv') 
    data = pd.read_csv(file_path)

    for site in ["shopping_admin", "shopping", "reddit", "gitlab", "map", "multisite"]:
        site_data = data[data['site'] == site]
        approach_keys = [k for k in site_data.keys() if k not in ["task", "site"]]

        heatmap_data = pd.DataFrame({
            k: site_data[k] for k in approach_keys
        })

        heatmap_values = heatmap_data.values

        colors = ['#EFEFEF', '#2A786C']
        cmap = mcolors.LinearSegmentedColormap.from_list("CustomCmap", colors)
        plt.figure(figsize=(10, 20))
        plt.imshow(heatmap_values, cmap=cmap, aspect='auto')

        plt.xticks(ticks=[0.5 + k for k in list(range(len(approach_keys)))], labels=[]*len(approach_keys))
        plt.yticks([])

        ax = plt.gca()

        ax.set_yticks([])

        ax_left = plt.gca().twinx()
        ax_left.set_yticks(np.arange(len(site_data))+1)
        ax_left.set_yticklabels(site_data.iloc[::-1]["task"], fontsize=3)

        ax_right = plt.gca().twinx()
        ax_right.set_yticks(np.arange(len(site_data))+1)
        ax_right.set_yticklabels(site_data.iloc[::-1]["task"], fontsize=3)
        ax_right.yaxis.set_label_position("right")

        plt.grid(color='white', linestyle='-', linewidth=5)

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"figures/{site}_{len(approach_keys)}.png"), dpi=256)

def plot_comparative_bar_chart(categories, data_list, labels, colors, title="Comparative Bar Chart", ylabel="Values", figure_name="bar"):
    os.makedirs(os.path.join(OUTPUT_DIR, "figures"), exist_ok=True)

    bar_width = 1/(len(labels)+1)
    x = np.arange(len(categories))

    plt.rc('font', family='serif')
    plt.figure(figsize=(9, 2))

    for i, (data, label, color) in enumerate(zip(data_list, labels, colors)):
        plt.bar(x + i * bar_width, data, width=bar_width, label=label, color=color)

    for i, (data, label) in enumerate(zip(data_list, labels)):
        for j, value in enumerate(data):
            plt.text(x[j] + i * bar_width, value, f"{value:.1f}" if isinstance(value, float) else f"{value}", ha='center', va='bottom', fontsize=5)

    if title:
        plt.title(title)
    plt.ylabel(ylabel, fontsize=11)
    plt.xticks(x + bar_width * (len(labels) - 1) / 2, [c.replace("_", " ").capitalize() for c in categories], fontsize=11)
    plt.legend(loc='lower center', fontsize=11, bbox_to_anchor=(0.5, 1.05), ncol=3)
    plt.grid(axis='y')

    plt.ylim(0, 65)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"figures/{figure_name}.pdf"), dpi=256)
    plt.close()

def compute_success_rate(trajectory_key_list=None, evaluator="after"):
    site_lists = ["ALL", "SHOPPING", "SHOPPING_ADMIN", "GITLAB", "MAP", "REDDIT", "MULTISITE"]
    csvfile = open(os.path.join(OUTPUT_DIR, "result.csv"), "w")
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["basename", "site", "total_reward", "net_total_reward", "total_tasks"])

    categories = site_lists

    trajectory_key_list = trajectory_key_list if trajectory_key_list else [k for k in sorted(list(TRAJECTORY_DIR_DICT.keys()), reverse=False)]
    labels = [RUN_NAME_DICT[i] for i in trajectory_key_list]

    colors = get_colors(trajectory_key_list)

    reward_percentage_list = {l:[] for l in labels}
    net_reward_percentage_list = {l:[] for l in labels}
    
    for i, key in enumerate(trajectory_key_list):
        root_directory = TRAJECTORY_DIR_DICT[key]
        basename = labels[i]
        for site_list in site_lists:
            total_reward, net_total_reward, total_tasks = parse_json_files(root_directory, [site_list], evaluator=evaluator, mode="multiple_site")
            total_tasks = TOTAL_TASK_NUM_DICT[site_list]
            reward_percentage_list[basename].append(total_reward/total_tasks*100)
            net_reward_percentage_list[basename].append(net_total_reward/total_tasks*100)
            csv_writer.writerow([basename, site_list, total_reward, net_total_reward, total_tasks])
    csvfile.close()
    plot_comparative_bar_chart(categories=categories, data_list=[reward_percentage_list[l] for l in labels], labels=labels, colors=colors, title="Reward Percentage", figure_name="reward_percentage")
    plot_comparative_bar_chart(categories=categories, data_list=[net_reward_percentage_list[l] for l in labels], labels=labels, colors=colors, title="", ylabel="Success Rate", figure_name="net_reward_percentage")

if __name__ == "__main__":
    ablation_study_key_list = [7, 3, 4, 5, 6, 0]
    compute_success_rate(ablation_study_key_list)