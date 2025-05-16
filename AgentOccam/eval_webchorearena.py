import os
import time
import re
import argparse
import shutil
import yaml
from AgentOccam.env import WebArenaEnvironmentWrapper
from AgentOccam.AgentOccam import AgentOccam
from webagents_step.utils.data_prep import *
from AgentOccam.prompts import AgentOccam_prompt
import subprocess

def run():
    parser = argparse.ArgumentParser(
        description="Only the config file argument should be passed"
    )
    parser.add_argument(
        "--config", type=str, required=True, help="yaml config file location"
    )
    args = parser.parse_args()
    print("Config file:", args.config)
    with open(args.config, "r") as file:
        config = DotDict(yaml.safe_load(file))

    if config.logging:
        if config.logname:
            dstdir = f"{config.logdir}/{config.logname}"
        else:
            dstdir = f"{config.logdir}/{time.strftime('%Y%m%d-%H%M%S')}"
        os.makedirs(dstdir, exist_ok=True)
        shutil.copyfile(args.config, os.path.join(dstdir, args.config.split("/")[-1]))
    random.seed(42)
    print(os.path.join(dstdir, args.config.split("/")[-1]))

    config_file_list = []

    task_ids = config.env.task_ids
    if hasattr(config.env, "relative_task_dir"):
        relative_task_dir = config.env.relative_task_dir
    else:
        relative_task_dir = "tasks"
    if task_ids == "all" or task_ids == ["all"]:
        task_ids = [filename[:-len(".json")] for filename in os.listdir(f"config_files/{relative_task_dir}") if filename.endswith(".json")]
    for task_id in task_ids:
        config_file_list.append(f"config_files/{relative_task_dir}/{task_id}.json")

    fullpage = config.env.fullpage if hasattr(config.env, "fullpage") else True
    current_viewport_only = not fullpage

    agent_init = lambda: AgentOccam(
        prompt_dict = {k: v for k, v in AgentOccam_prompt.__dict__.items() if isinstance(v, dict)},
        config = copy.deepcopy(config.agent),
    )

    count = 0

    for config_file in config_file_list:
        with open(config_file, "r") as f:
            task_config = json.load(f)
            print(f"Task {task_config['task_id']}.")
        if os.path.exists(os.path.join(dstdir, f"{task_config['task_id']}.json")):
            print(f"Skip {task_config['task_id']}.")
            continue
        subprocess.run("bash scripts/run_env_setup.sh", shell=True)
        if task_config['task_id'] in list(range(600, 650))+list(range(681, 689)):
            print("Reddit post task. Sleep 30 mins.")
            time.sleep(1800)
        if task_config['task_id'] in [30170, 30171, 30172, 30173, 30174, 50000, 50001, 50002, 50010, 50011, 50012, 50013, 50014, 50020, 50021, 50022, 50023, 50024, 50030, 50031, 50032, 50033, 50034, 50040, 50050, 50051, 50052, 50060, 50061, 50062, 50063, 50064]:
            count += 1
            if count % 3 == 0:
                print("Reddit post task. Restart.")
                subprocess.run("bash scripts/reset/reset_reddit.sh", shell=True)
                time.sleep(1800)
        if config.agent.actor.current_observation.auto == True:
            if task_config["required_obs"] == "image":
                config.agent.actor.current_observation.type = ["text", "image"]
            else:
                config.agent.actor.current_observation.type = ["text"]
                
        env = WebArenaEnvironmentWrapper(config_file=config_file,
                                         max_browser_rows=config.env.max_browser_rows,
                                         max_steps=config.max_steps,
                                         slow_mo=1,
                                         observation_type="accessibility_tree",
                                         current_viewport_only=current_viewport_only,
                                         viewport_size={"width": 1920, "height": 1080},
                                         headless=config.env.headless,
                                         global_config=config)

        website = task_config.get("sites", None)[0]
        if website == "wikipedia":
            website = task_config.get("sites", None)[1]

        agent = AgentOccam(
            prompt_dict={k: v for k, v in AgentOccam_prompt.__dict__.items() if isinstance(v, dict)},
            config=copy.deepcopy(config.agent),
            website=website
        )
        objective = env.get_objective()

        try:
            status = agent.act(objective=objective, env=env)
            env.close()
        except ValueError:
            env.close()
            status = {"done": False, "reward": 0, "success": 0, "num_actions": None}

        if config.logging:
            with open(config_file, "r") as f:
                task_config = json.load(f)
            log_file = os.path.join(dstdir, f"{task_config['task_id']}.json")
            log_data = {
                "task": config_file,
                "id": task_config['task_id'],
                "model": config.agent.actor.model if hasattr(config.agent, "actor") else config.agent.model_name,
                "type": config.agent.type,
                "trajectory": agent.get_trajectory(),
            }
            summary_file = os.path.join(dstdir, "summary.csv")
            summary_data = {
                "task": config_file,
                "task_id": task_config['task_id'],
                "model": config.agent.actor.model if hasattr(config.agent, "actor") else config.agent.model_name,
                "type": config.agent.type,
                "logfile": re.search(r"/([^/]+/[^/]+\.json)$", log_file).group(1),
            }

            if status:
                summary_data.update(status)
            log_run(
                log_file=log_file,
                log_data=log_data,
                summary_file=summary_file,
                summary_data=summary_data,
            )
    
if __name__ == "__main__":
    run()
