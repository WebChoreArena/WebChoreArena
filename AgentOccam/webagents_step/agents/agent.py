from typing import List
import os

class Agent:
    def __init__(
        self,
        max_actions,
        verbose=0,
        logging=False,
        # log_dir="logs",
        previous_actions: List = None,
        previous_reasons: List = None,
        previous_responses: List = None,
    ):
        self.previous_actions = [] if previous_actions is None else previous_actions 
        self.previous_reasons = [] if previous_reasons is None else previous_reasons
        self.previous_responses = [] if previous_responses is None else previous_responses
        self.max_actions = max_actions
        self.verbose = verbose
        self.logging = logging
        self.log_dir = log_dir  # ログディレクトリを保存
        self.trajectory = []
        self.data_to_log = {}

        # ログディレクトリとスクリーンショットディレクトリを作成
        os.makedirs(self.log_dir, exist_ok=True)
        self.screenshot_dir = os.path.join(self.log_dir, "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def reset(self):
        self.previous_actions = []
        self.previous_reasons = []
        self.previous_responses = []
        self.trajectory = []
        self.data_to_log = {}

    def get_trajectory(self):
        return self.trajectory
    
    def update_history(self, action, reason):
        if action:
            self.previous_actions += [action]
        if reason:
            self.previous_reasons += [reason]    

    def predict_action(self, objective, observation, url=None):
        pass

    def receive_response(self, response):
        self.previous_responses += [response]

    def act(self, objective, env):
        while not env.done():
            observation = env.observation()
            action, reason = self.predict_action(
                objective=objective, observation=observation, url=env.get_url()
            )
            status = env.step(action)

            if self.logging:
                self.log_step(
                    objective=objective,
                    url=env.get_url(),
                    observation=observation,
                    action=action,
                    reason=reason,
                    status=status,
                    env=env  # Playwrightの環境を渡す
                )

            if len(self.previous_actions) >= self.max_actions:
                print(f"Agent exceeded max actions: {self.max_actions}")
                break

        return status

    async def async_act(self, objective, env):
        while not env.done():
            observation = await env.observation()
            action, reason = self.predict_action(
                objective=objective, observation=observation, url=env.get_url()
            )
            status = await env.step(action)

            if self.logging:
                self.log_step(
                    objective=objective,
                    url=env.get_url(),
                    observation=observation,
                    action=action,
                    reason=reason,
                    status=status,
                    env=env  # Playwrightの環境を渡す
                )

            if len(self.previous_actions) >= self.max_actions:
                print(f"Agent exceeded max actions: {self.max_actions}")
                break

        return status

    def log_step(self, objective, url, observation, action, reason, status, env):
        self.data_to_log['objective'] = objective
        self.data_to_log['url'] = url
        self.data_to_log['observation'] = observation if isinstance(observation, str) else observation["text"]
        self.data_to_log['previous_actions'] = self.previous_actions[:-1]
        self.data_to_log['previous_responses'] = self.previous_responses[:-1]
        self.data_to_log['previous_reasons'] = self.previous_reasons[:-1]
        self.data_to_log['action'] = action
        self.data_to_log['reason'] = reason

        if status:
            for (k, v) in status.items():
                self.data_to_log[k] = v

        # スクリーンショットを `log_dir/screenshots/` に保存
        screenshot_path = os.path.join(self.screenshot_dir, f"step_{len(self.trajectory)}.png")
        env.page.screenshot(path=screenshot_path)  # Playwrightのページオブジェクトを使ってスクリーンショットを撮る
        self.data_to_log["screenshot"] = os.path.relpath(screenshot_path, self.log_dir)  # 相対パスを記録

        self.trajectory.append(self.data_to_log)
        self.data_to_log = {}

# from typing import List


# class Agent:
#     def __init__(
#         self,
#         max_actions,
#         verbose=0,
#         logging=False,
#         previous_actions: List = None,
#         previous_reasons: List = None,
#         previous_responses: List = None,
#     ):
#         self.previous_actions = [] if previous_actions is None else previous_actions 
#         self.previous_reasons = [] if previous_reasons is None else previous_reasons
#         self.previous_responses = [] if previous_responses is None else previous_responses
#         self.max_actions = max_actions
#         self.verbose = verbose
#         self.logging = logging
#         self.trajectory = []
#         self.data_to_log = {}

#     def reset(self):
#         self.previous_actions = []
#         self.previous_reasons = []
#         self.previous_responses = []
#         self.trajectory = []
#         self.data_to_log = {}

#     def get_trajectory(self):
#         return self.trajectory
    
#     def update_history(self, action, reason):
#         if action:
#             self.previous_actions += [action]
#         if reason:
#             self.previous_reasons += [reason]    

#     def predict_action(self, objective, observation, url=None):
#         pass

#     def receive_response(self, response):
#         self.previous_responses += [response]

#     def act(self, objective, env):
#         while not env.done():
#             observation = env.observation()
#             action, reason = self.predict_action(
#                 objective=objective, observation=observation, url=env.get_url()
#             )
#             status = env.step(action)

#             if self.logging:
#                 self.log_step(
#                     objective=objective,
#                     url=env.get_url(),
#                     observation=observation,
#                     action=action,
#                     reason=reason,
#                     status=status,
#                 )

#             if len(self.previous_actions) >= self.max_actions:
#                 print(f"Agent exceeded max actions: {self.max_actions}")
#                 break

#         return status

#     async def async_act(self, objective, env):
#         while not env.done():
#             observation = await env.observation()
#             action, reason = self.predict_action(
#                 objective=objective, observation=observation, url=env.get_url()
#             )
#             status = await env.step(action)

#             if self.logging:
#                 self.log_step(
#                     objective=objective,
#                     url=env.get_url(),
#                     observation=observation,
#                     action=action,
#                     reason=reason,
#                     status=status,
#                 )

#             if len(self.previous_actions) >= self.max_actions:
#                 print(f"Agent exceeded max actions: {self.max_actions}")
#                 break

#         return status

#     def log_step(self, objective, url, observation, action, reason, status):
#         self.data_to_log['objective'] = objective
#         self.data_to_log['url'] = url
#         self.data_to_log['observation'] = observation if isinstance(observation, str) else observation["text"]
#         self.data_to_log['previous_actions'] = self.previous_actions[:-1]
#         self.data_to_log['previous_responses'] = self.previous_responses[:-1]
#         self.data_to_log['previous_reasons'] = self.previous_reasons[:-1]
#         self.data_to_log['action'] = action
#         self.data_to_log['reason'] = reason
#         if status:
#             for (k, v) in status.items():
#                 self.data_to_log[k] = v
#         self.trajectory.append(self.data_to_log)
#         self.data_to_log = {}
