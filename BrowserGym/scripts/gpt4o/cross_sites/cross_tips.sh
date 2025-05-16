TASK_IDS=(50000 50001 50002 50010 50011 50012 50013 50014 50020 50021 50022 50023 50024 50030 50031 50032 50033 50034 50040 50050 50051 50052 50060 50061 50062 50063 50064 50070 50071 50072 50073 50074 50080 50081 50082 50083 50084 50090 50091 50092 50093 50100 50101 50102 50103 50104 50110 50111 50112 50113 50120 50121 50122 50123 50124 50130 50131 50132 50133 50134 50140 50141 50142 50143 50144)
export CALC_AVAILABLE=False

source env_setup_wa.sh
TYPE="auto"
MODEL="gpt-4o-2024-05-13-azure"

WAIT_LIST=(50000 50001 50002 50010 50011 50012 50013 50014 50020 50021 50022 50023 50024 50030 50031 50032 50033 50034 50040 50050 50051 50052 50060 50061 50062 50063 50064)

COUNT=0
for task_id in "${TASK_IDS[@]}"
do
RESULT_DIR="results/cross/${TYPE}/${MODEL}/webchorearena.${task_id}"

  if [ -d "$RESULT_DIR" ]; then
    echo "Skipping ${task_id} (already exists)"
    continue
  fi
  # Wait for post task
  if [[ " ${WAIT_LIST[@]} " =~ " ${task_id} " ]]; then
    COUNT=$((COUNT + 1))
    if (( COUNT % 3 == 0 )); then
      echo "Restart reddit...$task_id"
      source scripts/reset/reset_reddit.sh
      sleep 30
    fi
  fi
python run.py --action_space webarena --tips True --max_total_tokens 128000 --max_input_tokens 126000 --observation_type ${TYPE} --task_name webchorearena.${task_id} --model_name gpt-4o-2024-05-13-azure --result_dir results/cross/${TYPE}/gpt-4o-2024-05-13-azure/
done
