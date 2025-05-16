import json
from browser_env import (
    create_id_based_action,
    create_id_based_actions,
    StateInfo,
    Trajectory,
    ActionTypes,
    ScriptBrowserEnv
)
from evaluation_harness.evaluators import evaluator_router
from AgentOccam.obs_opt import (
    prune_tree,
    translate_node_to_str,
)


class WebArenaEnvironmentWrapper():
    def __init__(self, config_file, max_browser_rows=300, max_steps=50, slow_mo=1, observation_type="accessibility_tree", current_viewport_only=False, viewport_size={"width": 1280, "height": 720}, headless=False, global_config=None):
        self.webarena_env = ScriptBrowserEnv(
                    headless=headless,
                    slow_mo=slow_mo,
                    observation_type=observation_type,
                    current_viewport_only=current_viewport_only,
                    viewport_size=viewport_size,
                    global_config=global_config
                )
        self.config_file = config_file
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
        self.global_config = global_config
        
        self.obs, self.info = self.webarena_env.reset(options={"config_file": self.config_file})
        self.terminated = False
        self.objective = self.config["intent"]
        self.url = self.config["start_url"]
        self.max_browser_rows = max_browser_rows
        self.max_steps = max_steps
        self.steps = 0
        self.is_done = False
        self.reward = 0.0
        
        self.trajectory: Trajectory = []
        self.update_webarena_metrics()
        
    def reset(self):
        self.obs, self.info = self.webarena_env.reset(options={"config_file": self.config_file})

    def close(self):
        self.webarena_env.close()
        
    def get_url(self):
        return self.url
    
    def get_objective(self):
        return self.objective 
    
    def get_sites(self):
        return self.config["sites"]
        
    def observation(self): 
        self.url = self.webarena_env.page.url
        if self.global_config and self.global_config.env.prune:
            root_node = self.obs["text"][1]
            DOM_root_node = prune_tree(objective=self.objective, root_node=root_node, mode="node")
            DOM_str = translate_node_to_str(node=DOM_root_node, mode="concise")
            return {"text": DOM_str, "image": self.obs["image"], "node": DOM_root_node}
        else:
            browser_content = self.obs["text"][0]
            browser_content = browser_content.split("\n")[:self.max_browser_rows] 
            browser_content = "\n".join(browser_content)
            return browser_content
    
    def done(self):
        if self.is_done:
            return True
        return False
    
    def status(self):
        return {'done': self.is_done, 'reward': self.reward, 'success': float(self.reward > 0), 'num_actions': self.steps}
    
    def step(self, action):
        self.steps = self.steps + 1
        print(f"[Step {self.steps}] {action}")
        print("*"*100)
        if self.steps > self.max_steps:
            print(f"Steps {self.steps} exceeded maximum {self.max_steps}")
            self.is_done = True
            action_cmd = create_id_based_action(f"stop [Trajectory failed: Steps {self.steps} exceeded maximum {self.max_steps}.]")
            self.update_webarena_metrics(action_cmd)
            return self.status()

        if action is None or action == "":
            action_cmds = []
        else:
            try:
                action_cmds = create_id_based_actions(action)
                if not action_cmds:
                    return False
            except Exception as e:
                print(f"Invalid action syntax: {e}")
                action_cmds = []

        for action_cmd in action_cmds:
            try:
                self.obs, _, self.terminated, _, self.info = self.webarena_env.step(action_cmd) 
                self.update_webarena_metrics(action_cmd)
            except Exception as e:
                print(f"Error occurred while taking step: {e}")
            
        return self.status()
    
    def update_webarena_metrics(self, action_cmd=None):
        # Append action (if any) and resulting sate
        if action_cmd:
            self.trajectory.append(action_cmd)
            if action_cmd["action_type"]== ActionTypes.STOP:
                self.is_done = True

        if not self.is_done: # If we are done, no need to append state
            state_info: StateInfo = {"observation": self.obs, "info": self.info}
            self.trajectory.append(state_info)
            
        if self.is_done:    
            try:
                evaluator = evaluator_router(self.config_file)
                self.reward = evaluator(trajectory=self.trajectory, config_file=self.config_file, page=self.webarena_env.page, client=self.webarena_env.get_page_client(self.webarena_env.page))
            except Exception as e:
                print(f"Got excepetion: {e}")
                self.reward = 0