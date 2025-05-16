import nltk
import os
from browsergym.core.registration import register_task

from . import config, task

# download necessary tokenizer resources
# note: deprecated punkt -> punkt_tab https://github.com/nltk/nltk/issues/3293
try:
    nltk.data.find("tokenizers/punkt_tab")
except:
    nltk.download("punkt_tab", quiet=True, raise_on_error=True)

ALL_WEBCHOREARENA_TASK_IDS = []

calc_available = os.environ.get("CALC_AVAILABLE", "False") == "True"


# register all WebArena benchmark
for task_id in config.TASK_IDS:
    if task_id >= 50000:
        task_kwargs = {"task_id": task_id, "with_homepage_hint": True}
    else:
        task_kwargs = {"task_id": task_id}

    if calc_available:
        task_kwargs["with_calc_hint"] = True

    gym_id = f"webchorearena.{task_id}"
    register_task(
        gym_id,
        task.GenericWebChoreArenaTask,
        task_kwargs=task_kwargs,
    )
    ALL_WEBCHOREARENA_TASK_IDS.append(gym_id)
