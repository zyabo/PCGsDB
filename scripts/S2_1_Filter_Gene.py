"""
Determine whether there is a gene mutation and all gene mutations
"""

import json
import pandas as pd
import ollama
import re
import time
import pickle
import os
import pandas as pd
import re
import time
import pickle
import json
import os
import ast
from transformers import AutoTokenizer
import transformers
import torch
from scripts.call_llm import get_response, init_llm
from scripts.pathfile import parse_path

torch.cuda.empty_cache()
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cuda"


def get_prompt_text(record, age, gender):
    prompt_str = """
Based on the medical records of patients ({}, {}), answer the following questions:

**Question A: If genetic testing is mentioned in the medical record, please list complete sentences referring to genetic testing. **
Answer:
* xxx
* xxx

**[Question B: If gene-related biomarkers are mentioned in the medical record, please list complete sentences referring to the gene-related biomarkers. **
Answer:
* xxx


The following is the patient's medical record:
{} 
""".format(gender, age, record)

    #     prompt_str = prompt_str + """
    # """
    return prompt_str


def get_prompt(record):
    prompt_str = """
Please fill in the dict in python format below based on the content of genetic testing and gene-related biomarkers in the patient medical record description below (2 questions).
Patient_medical_gene_record = {"is there genetic testing?": "yes, no, or unknown", 
"is there gene-related biomarker?": "yes, no, or unknown"}
"""

    prompt_str = prompt_str + """
The patient medical record describes the following:
{} 

""".format(record)

    return prompt_str



def S2_1_Filter_Gene(dir_paths,model_type,model_name):

    client, pipeline, tokenizer = init_llm(model_type, model_name)

    """
    2. Read the medical records of all cases and save them in list_records
    """
    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()
    list_ages = df['age'].tolist()
    list_genders = df['gender'].tolist()
    list_file_paths = df['file_path'].tolist()

    with open(dir_paths["SelectedTissue.json"], 'r') as json_file:
        SelectedTissue = json.load(json_file)

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"], 'r') as file:
        Dict_TissueCancerNames_Full = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord.json"] , 'r') as file:
        Dict_Index_TissueRecord = json.load(file)


    with open(dir_paths["Dict_Records_Gene_kw_indice.json"] , 'r') as file:
        Dict_Records_Gene_kw_indice = json.load(file)



    if os.path.exists(dir_paths["Dict_Records_Gene.json"]):
        with open(dir_paths["Dict_Records_Gene.json"], 'r') as json_file:
            Dict_Records_Gene = json.load(json_file)
    else:
        Dict_Records_Gene = {}

    if os.path.exists(dir_paths["Dict_Records_Gene_prompts.json"]):
        with open(dir_paths["Dict_Records_Gene_prompts.json"], 'r') as json_file:
            Dict_Records_Gene_prompts = json.load(json_file)
    else:
        Dict_Records_Gene_prompts = {}

    if os.path.exists(dir_paths["Dict_Records_GeneText.json"]):
        with open(dir_paths["Dict_Records_GeneText.json"], 'r') as json_file:
            Dict_Records_GeneText = json.load(json_file)
    else:
        Dict_Records_GeneText = {}

    if os.path.exists(dir_paths["Dict_Records_GeneText_prompts.json"]):
        with open(dir_paths["Dict_Records_GeneText_prompts.json"], 'r') as json_file:
            Dict_Records_GeneText_prompts = json.load(json_file)
    else:
        Dict_Records_GeneText_prompts = {}

    if model_name not in Dict_Records_GeneText.keys():
        Dict_Records_GeneText[model_name] = {}
        Dict_Records_GeneText_prompts[model_name] = {}
        Dict_Records_Gene[model_name] = {}
        Dict_Records_Gene_prompts[model_name] = {}

    # for index_cancer in range(len(SelectedTissue)):
    for index_cancer, tissue in enumerate(Dict_TissueCancerNames_Full):
        # tissue = SelectedTissue[index_cancer]
        Dict_TissueCancerName_Full = Dict_TissueCancerNames_Full[tissue]
        List_Record_Gene_kw_indice = Dict_Records_Gene_kw_indice[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]
        Index_TissueRecord_Index_num = len(List_TissueRecord_Index)
        List_Record_Gene_kw_indice_num = len(List_Record_Gene_kw_indice)

        print("*" * 100)
        print("-" * 20 + "     " + "{}:{}({})".format(index_cancer, tissue,
                                                      List_Record_Gene_kw_indice_num) + "     " + "-" * 20)
        print("*" * 100)

        if model_name in Dict_Records_GeneText.keys():
            if tissue in Dict_Records_GeneText[model_name].keys():
                print(model_name)
                print("Has done!" )
                continue

        # if tissue in Dict_Records_GeneText:
        #     continue

        # if tissue != "Breast":
        #     continue
        # if tissue not in SelectedTissue:
        #     continue
        # if Index_TissueRecord_Index_num < 1000 or Index_TissueRecord_Index_num > 5000:
        #     continue

        start_time = time.time()
        yes_n, no_n = 0, 0

        dict_Records_Gene_single = {}
        list_Records_Gene_prompts = [""] * List_Record_Gene_kw_indice_num

        list_Records_GeneText = [""] * List_Record_Gene_kw_indice_num
        list_Records_GeneText_prompts = [""] * List_Record_Gene_kw_indice_num

        for indice_i in range(List_Record_Gene_kw_indice_num):
            indice_s = List_Record_Gene_kw_indice[indice_i]
            record = list_records[indice_s]

            disease_str = ', '.join(List_TissueRecord_Subdisease[indice_i])
            age_list = eval(list_ages[indice_s])
            age = str(int(age_list[0][0])) + "-" + age_list[0][1] + "-old"
            if list_genders[indice_s] == "M":
                gender = "Male"
            if list_genders[indice_s] == "F":
                gender = "Female"

            prompt_str = get_prompt_text(record, age, gender)
            part_char, file_name = parse_path(list_file_paths[indice_s])

            response_str, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer, prompt_str)

            list_Records_GeneText_prompts[indice_i] = prompt_str
            list_Records_GeneText[indice_i] = response_str

            if False:
                try_times = 5
                Succ_io = False
                for t1 in range(try_times):
                    # while Succ_io:
                    prompt_str_dict = get_prompt(response_str)
                    response_str_dict, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer, prompt_str_dict)

                    try:
                        dict_content = re.search(r'\{([^}]*)\}', response_str_dict).group(0)
                        response_dict = eval(dict_content)
                        if "is there genetic testing?" in response_dict.keys() and "is there gene-related biomarker?" in response_dict.keys():
                            response_dict["index"] = indice_s
                            Succ_io = True
                    except:
                        response_dict = {}

                    if Succ_io:
                        break

            prompt_str_dict = get_prompt(response_str)
            response_str_dict, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer, prompt_str_dict)

            list_Records_Gene_prompts[indice_i] = prompt_str_dict
            dict_Records_Gene_single[indice_s] = response_str_dict
            # dict_Records_Gene_single[indice_s] = response_dict

            current_time = time.time()
            elapsed_time = current_time - start_time
            average_time_per_iteration = elapsed_time / (indice_i + 1)
            remaining_iterations = List_Record_Gene_kw_indice_num - (indice_i + 1)
            estimated_remaining_time = remaining_iterations * average_time_per_iteration

            print("=" * 20)
            print(
                "Cancer({})   ({}/{})  age({})  gender({})  file({})  Time required: {} min {}".format(tissue, indice_i,
                                                                                                    len(List_Record_Gene_kw_indice),
                                                                                                    list_ages[indice_s],
                                                                                                    list_genders[indice_s],
                                                                                                    file_name,
                                                                                                    int(estimated_remaining_time / 60),
                                                                                                    model_name))
            # print(list_Records_Gene[indice_i], yes_n, no_n, indice_i, response_str)
            # print(response_str)
            # print("-" * 20)
            # print(response_dict)


        Dict_Records_GeneText[model_name][tissue] = list_Records_GeneText
        Dict_Records_GeneText_prompts[model_name][tissue] = list_Records_GeneText_prompts
        Dict_Records_Gene[model_name][tissue] = dict_Records_Gene_single
        Dict_Records_Gene_prompts[model_name][tissue] = list_Records_Gene_prompts

        with open(dir_paths["Dict_Records_GeneText.json"], 'w') as json_file:
            json.dump(Dict_Records_GeneText, json_file, indent=4)
        with open(dir_paths["Dict_Records_GeneText_prompts.json"], 'w') as json_file:
            json.dump(Dict_Records_GeneText_prompts, json_file, indent=4)
        with open(dir_paths["Dict_Records_Gene.json"], 'w') as json_file:
            json.dump(Dict_Records_Gene, json_file, indent=4)
        with open(dir_paths["Dict_Records_Gene_prompts.json"], 'w') as json_file:
            json.dump(Dict_Records_Gene_prompts, json_file, indent=4)

if __name__ == '__main__':
    """
    1. init llm
    """
    model_type = "local"
    # model_type = "api"

    # model_name = "llama3"
    # model_name = "medllama2"
    model_name = "Llama-3.1-8B-Instruct"
    # model_name = "Qwen2.5-7B-Instruct"

    S2_1_Filter_Gene(dir_paths, model_type, model_name)

