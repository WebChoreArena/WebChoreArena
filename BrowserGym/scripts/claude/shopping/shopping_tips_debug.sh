TASK_IDS=(20020)
export CALC_AVAILABLE=False

source env_setup_wa.sh
TYPE="auto"
MODEL="claude-3-7-sonnet-20250219"

for task_id in "${TASK_IDS[@]}"
do
RESULT_DIR="results/shopping/${TYPE}/${MODEL}/webchorearena.${task_id}"

  if [ -d "$RESULT_DIR" ]; then
    echo "Skipping ${task_id} (already exists)"
    continue
  fi
python run.py --action_space webarena --tips True --observation_type ${TYPE} --task_name webchorearena.${task_id} --model_name claude-3-7-sonnet-20250219 --result_dir results/shopping/${TYPE}/claude-3-7-sonnet-20250219/
done
