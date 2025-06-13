model_name=qwen-2.5-7b
prompt_name=prompt.json


python 2-merge_answer.py \
    --model_name $model_name \
    --path_template ./data/{task}/{level}/outputs/$prompt_name/$model_name \
    --output_dir ./submission/$prompt_name/$model_name
