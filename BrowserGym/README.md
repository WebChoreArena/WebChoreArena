# BrowserGym for WebChoreArena

## Install

*Install `browsergym`*: Follow the instructions in [this README](https://github.com/ServiceNow/BrowserGym) to install `browsergym`.

```bash
pip install browsergym
pip install playwright==1.50.0
playwright install chromium
```

*Setup the `webarena` specifics*:

```bash
pip install browsergym-webarena
python -c "import nltk; nltk.download('punkt')"
make install
```


Set up the web servers and environment URLs (find more details in the [webarena readme](https://github.com/web-arena-x/webarena/blob/main/environment_docker/README.md)).

You need to replace <your_base_url> in `env_setup_wa.sh` with your actual URL (for AWS, it typically starts with ec2-).

```bash
BASE_URL="<your_base_url>"
export WA_SHOPPING="$BASE_URL:7770/"
export WA_SHOPPING_ADMIN="$BASE_URL:7780/admin"
export WA_REDDIT="$BASE_URL:9999"
export WA_GITLAB="$BASE_URL:8023"
export WA_WIKIPEDIA="$BASE_URL:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="$BASE_URL:3000"
export WA_HOMEPAGE="$BASE_URL:4399"
```

*Install agent and evaluation requirements*:

```bash
pip install -r requirements.txt  # agent
```

## Run Agent

※ When creating the GPT-4o deployment on Azure, we named the model `gpt-4o-2024-05-13-azure`. By using the same name, you should be able to run the model without any issues. This code use GPT-4o for both inference and evaluation. 

```bash
export AZURE_OPENAI_API_KEY='your-api-key-here'
export AZURE_OPENAI_ENDPOINT="your-azure-endpoint-here"
export ANTHROPIC_API_KEY='your-api-key-here'
export GEMINI_API_KEY='your-api-key-here'
```

Next, you can implement the following command to produce the result.
```bash
bash scripts/claude/shopping/shopping_tips.sh
```

You can check the results in `./results/`.

Then, you can show the score by the following command:
```python
python utils/calc_score.py <result_path>
```


## Notes and Recommendations
### 1. Environment Reset
After evaluating each website, reset the environment to the initial state following the instructions [here](https://github.com/web-arena-x/webarena/blob/main/environment_docker/README.md#environment-reset). After the reset, run the inference for cross-site tasks.

We do not recommend changing the order of tasks, as some tasks later in the list may alter the environment (i.e., `affect_environment=True`).
However, resetting the environment more frequently than instructed is perfectly acceptable if needed.


### 2. Error Checking
Agents may encounter errors due to various reasons such as API failures or environmental issues.
Error logs will be recorded in the `summary_info.json` file inside each result folder.

We recommend running the `utils/error_check.py` script after completing the evaluation to identify how many errors occurred in the result directory.
You can use the script as follows:

```python
python utils/error_check.py <result_dir>
```

Then, remove the erroneous result files by moving them to the `trash` directory using the following command:

```python
python utils/move2trash.py <result_dir>
```
When re-running the evaluation for failed tasks, make sure to restart the environment beforehand.
