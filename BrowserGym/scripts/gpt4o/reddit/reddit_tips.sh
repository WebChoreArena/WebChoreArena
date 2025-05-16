TASK_IDS=(30000 30001 30010 30020 30021 30022 30023 30024 30030 30031 30032 30033 30034 30040 30041 30042 30043 30050 30051 30052 30053 30054 30060 30061 30062 30063 30070 30071 30072 30073 30074 30080 30081 30082 30083 30084 30090 30091 30092 30093 30094 30100 30101 30102 30103 30104 30110 30111 30112 30113 30114 30120 30121 30122 30123 30124 30130 30131 30132 30133 30134 30140 30141 30142 30143 30144 30150 30151 30152 30153 30154 30160 30161 30162 30163 30164 30170 30171 30172 30173 30174 30180 30181 30182 30183 30184 30190 30191 30192 30193 30194)
export CALC_AVAILABLE=False

source env_setup_wa.sh
TYPE="auto"
MODEL="gpt-4o-2024-05-13-azure"


for task_id in "${TASK_IDS[@]}"
do
RESULT_DIR="results/reddit/${TYPE}/${MODEL}/webchorearena.${task_id}"

  if [ -d "$RESULT_DIR" ]; then
    echo "Skipping ${task_id} (already exists)"
    continue
  fi
  if [[ "$task_id" == 30170 || "$task_id" == 30171 || "$task_id" == 30172 || "$task_id" == 30173 || "$task_id" == 30174 ]]; then
    echo "Restart reddit...$task_id"
    source scripts/reset/reset_reddit.sh
    sleep 30
  fi
python run.py --action_space webarena --tips True --max_total_tokens 128000 --max_input_tokens 126000 --observation_type ${TYPE} --task_name webchorearena.${task_id} --model_name gpt-4o-2024-05-13-azure --result_dir results/reddit/${TYPE}/gpt-4o-2024-05-13-azure/
done
