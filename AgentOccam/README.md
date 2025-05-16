# AgentOccam for WebChoreArena

## Install

```bash
git clone https://github.com/web-arena-x/webarena.git
cd webarena
conda create -n agentoccam python=3.10; conda activate agentoccam
pip install -r requirements.txt
pip install --upgrade transformers
pip install --upgrade openai
pip install numpy==1.26.4
playwright install
pip install -e .
cd ~/AgentOccam
pip install -r requirements.txt
mkdir .auth
```

Set up the web servers and environment URLs (find more details in the [webarena readme](https://github.com/web-arena-x/webarena/blob/main/environment_docker/README.md)).


## Replace URLs
You need to replace <your_base_url> in files (e.g., `scripts/env_setup.sh`) with your actual URL (for AWS, it typically starts with ec2-). To achieve this, run the following command:

```bash
python utils/replace_script.py --your_url "your url (e.g., ec2..)"
```

## Create Tasks
Run the following command to create the task JSON file.

```bash
source scripts/env_setup.sh
cd config_files
python generate_test_data_new_shopping_admin.py
python generate_test_data_new_shopping.py
python generate_test_data_new_reddit.py
python generate_test_data_new_gitlab.py
python generate_test_data_new_cross.py
cd ../
```


## Run Agent
First, please set API keys.

※ When creating the GPT-4o deployment on Azure, we named the model `gpt-4o-2024-05-13-azure`. By using the same name, you should be able to run the model without any issues. This code use GPT-4o for both inference and evaluation. 

```bash
export AZURE_OPENAI_API_KEY='your-api-key-here'
export AZURE_OPENAI_ENDPOINT="your-azure-endpoint-here"
export ANTHROPIC_API_KEY='your-api-key-here'
export GEMINI_API_KEY='your-api-key-here'
```

Next, implement the following command for auto-login.
```bash
source scripts/login_setup.sh
```

Next, you can implement the following command to produce the result.

```bash
bash scripts/claude/shopping/shopping_tips.sh
```

When you finish the inference, please implement the following command to get the result.

```bash
python utils/calc_score.py <your_result_csv>
```


## Notes and Recommendations
### 1. Environment Reset
After evaluating each website, reset the environment to the initial state following the instructions [here](https://github.com/web-arena-x/webarena/blob/main/environment_docker/README.md#environment-reset). After the reset, run the inference for cross-site tasks.

We do not recommend changing the order of tasks, as some tasks later in the list may alter the environment (i.e., `affect_environment=True`).
However, resetting the environment more frequently than instructed is perfectly acceptable if needed.


### 2. Checking of Login
If a task is stuck on the admin or login page, it likely means that auto-login has failed.
Please try running:
```bash
source scripts/login_setup.sh
```
or investigate other possible reasons why the login might be failing.