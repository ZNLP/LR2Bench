import os
import json
import argparse
import traceback
from collections import defaultdict

level_dict = {
    "crossword": ["5_5", "10_10", "15_15"],
    "acrostic": ["easy", "hard"],
    "logic": ["4_4", "4_5", "4_6", "4_7"],
    "cryptogram": ["easy", "hard"],
    "sudoku": ["4_4_easy", "4_4_hard", "9_9_easy", "9_9_hard"],
    "drop": ["easy", "hard"]
}


def norm_dict(d):
    if d:
        return {str(key).lower(): str(value).replace(" ", "").lower() for key, value in d.items()}
    else:
        return {}


def calculate_dict_correct(gold, prediction_text):
    try:
        prediction = eval(prediction_text)
        gold = norm_dict(gold)
        prediction = norm_dict(prediction)
                
        matching_dict = {}
        correct_cnt = 0
        
        for key, gold_value in gold.items():
            predicted_value = prediction.get(key, "MISSING")
            is_correct = (gold_value == predicted_value)
            correct_cnt += is_correct
            matching_dict[key] = {
                "gold": gold_value,
                "model": predicted_value,
                "correct": is_correct
            }

        correct_100 = (correct_cnt == len(gold))
        correct_50 = (correct_cnt / len(gold) >= 0.5)
        

    except Exception as e:
        print(prediction_text)
        print(f"Error: {e}")
        print(traceback.format_exc())
        
        correct_cnt = 0
        correct_100 = False
        correct_50 = False
        
        matching_dict = {
            key: {
                "gold": gold[key],
                "model": f"ERROR: {str(e)}",
                "correct": False
            }
            for key in gold.keys()
        }
    
    return correct_cnt, correct_100, correct_50, matching_dict


def calculate_logic_answer_correct(gold, prediction_text):
    def norm(ans):
        return [{str(key).lower(): str(value).lower() for key, value in d.items()} for d in ans]
    try:
        prediction = eval(prediction_text)
        gold = norm(gold)
        prediction = norm(prediction)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        prediction = [] 
    
    correct_cnt = 0
    all_cnt = 0
    for d_gold in gold:
        first_pair = list(d_gold.items())[0]
        d_prediction = [d for d in prediction if first_pair in list(d.items())]
        if not d_prediction:
            d_prediction = {}
        else:
            d_prediction = d_prediction[0]

        for key, gold_value in d_gold.items():
            if key == first_pair[0]:
                continue
            all_cnt += 1
            predicted_value = d_prediction.get(key, "")
            if gold_value == predicted_value:
                correct_cnt += 1
    
    correct_100 = (correct_cnt == all_cnt)
    correct_50 = (correct_cnt / all_cnt >= 0.5)

    return correct_cnt, all_cnt, correct_100, correct_50


def calculate_sudoku_answer_correct(grid, gold, prediction_text):
    try:
        prediction = eval(prediction_text)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        prediction = [[]]
    
    all_cnt = sum([row.count(0) for row in grid])
    correct_cnt = 0
    for i in range(min(len(gold), len(prediction))):
        for j in range(min(len(gold[i]), len(prediction[i]))):
            if gold[i][j] == prediction[i][j] and grid[i][j] == 0:
                correct_cnt += 1
    
    if correct_cnt > all_cnt:
        print("Error: correct_cnt > all_cnt")
        correct_cnt = all_cnt
    
    correct_100 = (correct_cnt == all_cnt)
    correct_50 = (correct_cnt / all_cnt >= 0.5)

    return correct_cnt, all_cnt, correct_100, correct_50


def calculate_drop_answer_correct(gold, prediction_text):
    try:
        prediction = eval(prediction_text)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
        prediction = [[]]
    
    all_cnt = len([x for row in gold for x in row if x != "#"])
    correct_cnt = 0
    for i in range(min(len(gold), len(prediction))):
        for j in range(min(len(gold[i]), len(prediction[i]))):
            if gold[i][j] != "#" and gold[i][j] == prediction[i][j]:
                correct_cnt += 1
    
    if correct_cnt > all_cnt:
        print("Error: correct_cnt > all_cnt")
        correct_cnt = all_cnt
    
    correct_100 = (correct_cnt == all_cnt)
    correct_50 = (correct_cnt / all_cnt >= 0.5)

    return correct_cnt, all_cnt, correct_100, correct_50



def eval_crossword(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["crossword"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            
            if model_answer != "{}":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_correct_100, curr_correct_50, matching_dict = calculate_dict_correct(gold, model_answer)

            subtask_cnt += len(gold)
            subtask_correct_cnt += curr_subtask_correct_cnt

            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def eval_acrostic(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["acrostic"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            
            if model_answer != "{}":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_correct_100, curr_correct_50, matching_dict = calculate_dict_correct(gold, model_answer)

            subtask_cnt += len(gold)
            subtask_correct_cnt += curr_subtask_correct_cnt

            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def eval_logic(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["logic"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            
            if model_answer != "[]":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_subtask_cnt, curr_correct_100, curr_correct_50 = calculate_logic_answer_correct(gold, model_answer)

            subtask_cnt += curr_subtask_cnt
            subtask_correct_cnt += curr_subtask_correct_cnt
            
            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def eval_cryptogram(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["cryptogram"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            
            if model_answer != "{}":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_correct_100, curr_correct_50, matching_dict = calculate_dict_correct(gold, model_answer)

            subtask_cnt += len(gold)
            subtask_correct_cnt += curr_subtask_correct_cnt

            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def eval_sudoku(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["sudoku"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            grid = gold["grid"]
            gold = gold["answer"]
            
            if model_answer != "[[]]":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_subtask_cnt, curr_correct_100, curr_correct_50 = calculate_sudoku_answer_correct(grid, gold, model_answer)

            subtask_cnt += curr_subtask_cnt
            subtask_correct_cnt += curr_subtask_correct_cnt

            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def eval_drop(data_list, golden_list):
    eval_dict = defaultdict(dict)
    for level in level_dict["drop"]:
        golden = [g for g in golden_list if g["level"] == level]
        golden_dict = {g["tag"]: g for g in golden}

        data = [d for d in data_list if d["level"] == level]
        
        answer_exist_cnt = 0
        subtask_cnt = 0
        subtask_correct_cnt = 0

        sample_correct_100_cnt = 0
        sample_correct_50_cnt = 0


        for d in data:
            tag = str(d["tag"])
            model_answer = d['answer']
            gold = json.loads(golden_dict[tag]['answer'])
            
            if model_answer != "[[]]":
                answer_exist_cnt += 1
            
            curr_subtask_correct_cnt, curr_subtask_cnt, curr_correct_100, curr_correct_50 = calculate_drop_answer_correct(gold, model_answer)

            subtask_cnt += curr_subtask_cnt
            subtask_correct_cnt += curr_subtask_correct_cnt

            sample_correct_100_cnt += curr_correct_100
            sample_correct_50_cnt += curr_correct_50
        
        eval_dict[level] = {
            "CR": answer_exist_cnt / len(data),
            "S-Acc": subtask_correct_cnt / subtask_cnt,
            "EM": sample_correct_100_cnt / len(data),
            "PM-0.5": sample_correct_50_cnt / len(data),
        }
    
    return eval_dict


def evaluate(data_list, golden_list, task):
    if task == "crossword":
        return eval_crossword(data_list, golden_list)
    elif task == "acrostic":
        return eval_acrostic(data_list, golden_list)
    elif task == "logic":
        return eval_logic(data_list, golden_list)
    elif task == "cryptogram":
        return eval_cryptogram(data_list, golden_list)
    elif task == "sudoku":
        return eval_sudoku(data_list, golden_list)
    elif task == "drop":
        return eval_drop(data_list, golden_list)
    else:
        raise ValueError(f"Invalid task: {task}")


def eval_overall(submission_dict):     
    tasks = ["crossword", "acrostic", "logic", "cryptogram", "sudoku", "drop"]
    
    eval_dict = {}
    
    for task in tasks:
        data_list = submission_dict["results"][task]
        golden_list = golden[task]
        result = evaluate(data_list, golden_list, task)
        eval_dict[task] = result
    
    return eval_dict



with open("./data/answer.json", "r", encoding='utf-8') as f:
    golden = json.load(f)
    


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default=None)
    parser.add_argument("--link", type=str, default=None)
    parser.add_argument("--params", type=int, default=None)
    parser.add_argument("--show_on_leaderboard", action="store_true")
    parser.add_argument("--path_template", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=None)

    return parser.parse_args()

args = arg_parser()

config_dict = {
    "model_name": args.model_name,
    "link": args.link,
    "Params": args.params,
    "show_on_leaderboard": args.show_on_leaderboard
}

setting_results_dict = defaultdict(lambda: defaultdict(list))

for i, task in enumerate(level_dict):
    for level in level_dict[task]:
        file_dir = args.path_template.format(task=f"{i}-{task}", level=level)
        for setting in os.listdir(file_dir):
            file_path = f"{file_dir}/{setting}/answer.json"
            with open(file_path, "r") as f:
                answer_list = json.load(f)
            setting_results_dict[setting][task].extend(answer_list)

for setting in setting_results_dict:
    results_dict = setting_results_dict[setting]
    submission_dict = {
        "config": config_dict,
        "results": results_dict
    }

    os.makedirs(f"{args.output_dir}/{setting}", exist_ok=True)

    with open(f"{args.output_dir}/{setting}/submission.json", "w") as f:
        json.dump(submission_dict, f, indent=4)

    performance_dict = eval_overall(submission_dict)
    with open(f"{args.output_dir}/{setting}/performance.json", "w") as f:
        json.dump(performance_dict, f, indent=4)