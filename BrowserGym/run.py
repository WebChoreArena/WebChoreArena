"""
WARNING DEPRECATED WILL BE REMOVED SOON
"""

import os
import argparse
from pathlib import Path

from browsergym.experiments import ExpArgs, EnvArgs

from agents.legacy.agent import GenericAgentArgs
from agents.legacy.dynamic_prompting import Flags
from agents.legacy.utils.chat_api import ChatModelArgs


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_args():
    parser = argparse.ArgumentParser(description="Run experiment with hyperparameters.")
    parser.add_argument(
        "--model_name",
        type=str,
        default="openai/gpt-4o",
        help="Model name for the chat model.",
    )
    parser.add_argument(
        "--task_name",
        type=str,
        default="openended",
        help="Name of the Browsergym task to run. If 'openended', you need to specify a 'start_url'",
    )
    parser.add_argument(
        "--start_url",
        type=str,
        default="https://www.google.com",
        help="Starting URL (only for the openended task).",
    )
    parser.add_argument(
        "--slow_mo", type=int, default=30, help="Slow motion delay for the playwright actions."
    )
    parser.add_argument(
        "--headless",
        type=str2bool,
        default=True,
        help="Run the experiment in headless mode (hides the browser windows).",
    )
    parser.add_argument(
        "--demo_mode",
        type=str2bool,
        default=True,
        help="Add visual effects when the agents performs actions.",
    )
    parser.add_argument(
        "--use_html", type=str2bool, default=False, help="Use HTML in the agent's observation space."
    )
    parser.add_argument(
        "--use_ax_tree",
        type=str2bool,
        default=True,
        help="Use AX tree in the agent's observation space.",
    )
    parser.add_argument(
        "--use_screenshot",
        type=str2bool,
        default=True,
        help="Use screenshot in the agent's observation space.",
    )
    parser.add_argument(
        "--multi_actions", type=str2bool, default=True, help="Allow multi-actions in the agent."
    )
    parser.add_argument(
        "--action_space",
        type=str,
        default="webarena",
        choices=["python", "bid", "coord", "bid+coord", "bid+nav", "coord+nav", "bid+coord+nav", "webarena"],
        help="",
    )
    parser.add_argument(
        "--use_history",
        type=str2bool,
        default=True,
        help="Use history in the agent's observation space.",
    )
    parser.add_argument(
        "--use_thinking",
        type=str2bool,
        default=True,
        help="Use thinking in the agent (chain-of-thought prompting).",
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=50,
        help="Maximum number of steps to take for each task.",
    )
    parser.add_argument(
        "--workflow_path",
        type=str,
        default=None,
        help="Path to the memory file to load for the agent.",
    )
    parser.add_argument(
        "--result_dir",
        type=str,
        default="results",
        help="Directory to save the results of the experiment.",
    )
    parser.add_argument(
        "--memory_flag",
        type=str2bool,
        default=True,
        help="Use thinking in the agent (chain-of-thought prompting).",
    )
    parser.add_argument(
        "--tips",
        type=str2bool,
        default=False,
        help="Use thinking in the agent (chain-of-thought prompting).",
    )
    parser.add_argument(
        "--observation_type",
        type=str,
        default="auto",
        choices=["auto", "image", "text"],
        help="",
    )
    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=2000,
        help="Maximum number of steps to take for each task.",
    )
    parser.add_argument(
        "--max_total_tokens",
        type=int,
        default=None,
        help="Maximum total tokens for the chat model.",
    )
    parser.add_argument(
        "--max_input_tokens",
        type=int,
        default=None,
        help="Maximum tokens for the input to the chat model.",
    )

    return parser.parse_args()


def main():
    print(
        """\
WARNING this demo agent will soon be moved elsewhere. Expect it to be removed at some point."""
    )

    args = parse_args()
    if (args.workflow_path is not None) and (not os.path.exists(args.workflow_path)):
        open(args.workflow_path, "w").close()


    env_args = EnvArgs(
        task_name=args.task_name,
        task_seed=None,
        max_steps=50,
        headless=args.headless,
        viewport={"width": 1500, "height": 1280},
        slow_mo=args.slow_mo,
    )

    task_id = args.task_name.split(".")[-1]
    task_id_int = int(task_id)
    
    if args.observation_type == "auto":
        if task_id_int in [10110, 10111, 10280, 10281, 10282, 10283, 10284, 50120, 50121, 50122, 50123, 50124]:
            args.use_screenshot = True
        else:
            args.use_screenshot = False
    elif args.observation_type == "image":
        args.use_screenshot = True
    elif args.observation_type == "text":
        args.use_screenshot = False
    else:
        raise ValueError("Invalid observation type")

    print("type(task_id):", type(task_id))
    if args.task_name == "openended":
        env_args.wait_for_user_message = True
        env_args.task_kwargs = {"start_url": args.start_url}
    
    save_dir = f"{args.result_dir}/{args.task_name}"
    if os.path.exists(save_dir):
        print(f"Directory {save_dir} already exists. Skip.")
        return
    
    assert args.memory_flag == True, "Memory flag must be True"

    website_dict = {1: "shopping_admin", 2: "shopping", 3: "reddit", 4: "gitlab", 5: "cross_site", 6: "debug"}
    website = website_dict[int(task_id) // 10000]

    if website == "cross_site":
        import pickle
        with open("newtask_cross_site_mapping.pkl", "rb") as f:
            websites_all = pickle.load(f)

        websites = websites_all[task_id_int]

        website = websites[0]

        if "wikipedia" in website:
            website = websites[1]
        if "gitlab" in websites:
            args.multi_actions = False
            args.demo_mode = False

    if args.tips:
        tips_path = f"agents/legacy/utils/tips/{website}.txt"
    else:
        tips_path = None

    exp_args = ExpArgs(
        env_args=env_args,
        agent_args=GenericAgentArgs(
            chat_model_args=ChatModelArgs(
                model_name=args.model_name,
                max_total_tokens=args.max_total_tokens,  # "Maximum total tokens for the chat model."
                max_input_tokens=args.max_input_tokens,  # "Maximum tokens for the input to the chat model."
                max_new_tokens=args.max_new_tokens,  # "Maximum total tokens for the chat model."
            ),
            flags=Flags(
                action_space=args.action_space, # add action_space (new)
                use_html=args.use_html,
                use_ax_tree=args.use_ax_tree,
                use_thinking=args.use_thinking,  # "Enable the agent with a memory (scratchpad)."
                use_error_logs=True,  # "Prompt the agent with the error logs."
                use_memory=args.memory_flag,  # "Enables the agent with a memory (scratchpad)."
                use_history=args.use_history,
                use_diff=False,  # "Prompt the agent with the difference between the current and past observation."
                use_past_error_logs=True,  # "Prompt the agent with the past error logs."
                use_action_history=True,  # "Prompt the agent with the action history."
                multi_actions=args.multi_actions,
                use_abstract_example=True,  # "Prompt the agent with an abstract example."
                use_concrete_example=True,  # "Prompt the agent with a concrete example."
                use_screenshot=args.use_screenshot,
                enable_chat=True,
                demo_mode="default" if args.demo_mode else "off",
                workflow_path=args.workflow_path,
                tips_path=tips_path,
            ),
        ),
    )

    exp_args.prepare(Path(args.result_dir))
    exp_args.run()

    os.rename(exp_args.exp_dir, f"{args.result_dir}/{args.task_name}")


if __name__ == "__main__":
    main()
