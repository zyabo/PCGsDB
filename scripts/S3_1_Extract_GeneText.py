"""
从 病历中 提取 相关信息
使用 通义千问
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
import pprint

torch.cuda.empty_cache()

#     prompt_str = """
# Please fill in the dictionary below (3 questions) in python format based on the medical record of the following patient ({} {}).
# """.format(age, gender)
#
#     prompt_str = prompt_str + """
# Patient_medical_gene_record =
# {'What gene mutations does the patient have?(Please answer ['Not specified'], or list all mutated genes in list form)': [],
#     """
#
#     disease_str = "'Does the patient have {}?': 'yes, no, or unknown',".format(cancer_str)


def get_prompt(record, age, gender):
    user_content_1 = """Please answer the following questions based on the medical history of this patient ({} {}):
** 1. Personal medical history (including previous medical diagnoses, surgical experiences, etc.) **
Answer:
** 2. Family medical history (record whether there are genetic diseases or other important diseases in the family)**
Answer:
** 3. Social history (such as smoking, drinking habits, occupational exposure, etc.) **
Answer:
** 4. Chief complaint (the patient’s main symptoms or problems when seeing a doctor)**
Answer:
** 5. History of current illness (development process of current illness and changes in symptoms)**
Answer:
** 6. Physical examination records (including basic physical signs such as body temperature, blood pressure, and heart rate, as well as more detailed physical examination records) **
Answer:
** 7. Laboratory test results (such as blood tests, urine tests, imaging tests (X-ray, CT, MRI), etc.)**
Answer:
** 8. Genetic test results (name of gene, mutation type, mutation location, clinical relevance and inheritance pattern of these mutations, etc.) **
Answer:
** 9. Diagnosis (medical diagnosis based on symptoms and examination results) **
Answer:
""".format(age, gender)

    user_content = """Based on the medical record description of the patient ({} {}) above, answer what gene mutations the patient has, and fill in the answer in a dict in python format.
""".format(age, gender)

    if len(record) > 5000:
        record = record[0:5000]

    system_content = """
The following is the medical history of this patient ({} {}):
{} 
""".format(age, gender, record)

    prompt_str = user_content + system_content

    template = """{
        "The patient's mutated gene": []
    }"""

    return prompt_str, user_content, system_content, template


"""
1. init llm
"""
model_type = "local"
# model_type = "api"
# model_type = "qwen"

# model_dict = {"model name": "llama3",
#               "total_tokens_max": int('inf')}
# model_dict = {"model name": "medllama2",
#               "total_tokens_max": int('inf')}

model_dict = {"model name": "numind/NuExtract-1.5",
              "total_tokens_max": float('inf')}

# for gene extract
# model_dict = {"model name": "qwen-plus",
#               "total_tokens_max": 2690000}
# model_dict = {"model name": "qwen-max",
#               "total_tokens_max": 418316}

# model_dict = {"model name": "qwen-max-0428",
#               "total_tokens_max": 1000000}

# model_dict = {"model name": "qwen-max-longcontext",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "qwen-max-0403",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "qwen-max-0107",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "qwen-max-1201",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "qwen-long",
#               "total_tokens_max": 3995064}
# model_dict = {"model name": "qwen-turbo",
#               "total_tokens_max": 4000000}

# Open source
# model_dict = {"model name": "qwen1.5-110b-chat",
#               "total_tokens_max": 3989885}
# model_dict = {"model name": "qwen1.5-72b-chat",
#               "total_tokens_max": 4000000}
# model_dict = {"model name": "qwen-72b-chat",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "llama3-70b-instruct",
#               "total_tokens_max": 1000000}
# model_dict = {"model name": "llama3-8b-instruct",
#               "total_tokens_max": 1000000}

model_name = model_dict["model name"]

model_type = "api"
model_name = "chain-of-thoughts.q5"

def S3_1_Extract_GeneText(dir_paths):

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

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    with open(dir_paths["Dict_Records_GeneDict.json"], 'r') as file:
        Dict_Records_GeneDict = json.load(file)

    if os.path.exists(dir_paths["Dict_Extract_GeneText.json"]):
        with open(dir_paths["Dict_Extract_GeneText.json"], 'r') as json_file:
            Dict_Extract_GeneText = json.load(json_file)
    else:
        Dict_Extract_GeneText = {}

    total_tokens_used = 0


    # for index_cancer in range(len(SelectedTissue)):
    for index_cancer, tissue in enumerate(Dict_Records_GeneDict):

        # tissue = SelectedTissue[index_cancer]
        Dict_TissueCancerName_Full = Dict_TissueCancerNames_Full[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]
        Index_TissueRecord_Index_num = len(List_TissueRecord_Index)
        Dict_Records_GeneDict_Tissue = Dict_Records_GeneDict[tissue]

        print("*" * 100)
        print("-" * 20 + "     " + "{}:{}({})".format(index_cancer, tissue,
                                                      Index_TissueRecord_Index_num) + "     " + "-" * 20)


        # for GeneDict_key, GeneDict_value in Dict_Records_GeneDict.items():
        #     uu = 1

        start_time = time.time()

        if tissue in Dict_Extract_GeneText:
            Dict_Extract_GeneText_Tissue = Dict_Extract_GeneText[tissue]
        else:
            Dict_Extract_GeneText_Tissue = {}
        for indice_i, key in enumerate(Dict_Records_GeneDict_Tissue):
            if (Dict_Records_GeneDict_Tissue[key]["Has genetic testing?"] == "yes" and
                    key not in Dict_Extract_GeneText_Tissue):
                indice_s = Dict_Records_GeneDict_Tissue[key]["Index"]
                record = list_records[indice_s]
                part_char, file_name = parse_path(list_file_paths[indice_s])

                disease_str = ', '.join(List_TissueRecord_Subdisease[indice_i])
                age_list = eval(list_ages[indice_s])
                age = str(int(age_list[0][0])) + "-" + age_list[0][1] + "-old"
                if list_genders[indice_s] == "M":
                    gender = "Male"
                if list_genders[indice_s] == "F":
                    gender = "Female"

                prompt_str, user_content, system_content, template = get_prompt(record, age, gender)

                # list_prompts[indice_i] = prompt_str
                # pprint.pprint(prompt_str)

                try:
                    response_str, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer, prompt_str, system_content, user_content, template)

                    total_tokens_used = total_tokens_used + total_tokens
                    if total_tokens_used > model_dict["total_tokens_max"]:
                        raise SystemExit("Token consumed")

                except:
                    Dict_Extract_GeneText[tissue] = Dict_Extract_GeneText_Tissue
                    with open(dir_paths["Dict_Extract_GeneText.json"], 'w') as json_file:
                        json.dump(Dict_Extract_GeneText, json_file, indent=4)
                    raise SystemExit("There is a problem, please try again.")

                Dict_Extract_GeneText_Tissue[key] = {"prompt_str": prompt_str,
                                                     "user_content": user_content,
                                                     "system_content": system_content,
                                                     "response": response_str}
                # print(prompt_str)
                # print(response_str)

                current_time = time.time()
                elapsed_time = current_time - start_time
                average_time_per_iteration = elapsed_time / (indice_i + 1)
                remaining_iterations = Index_TissueRecord_Index_num - (indice_i + 1)
                estimated_remaining_time = remaining_iterations * average_time_per_iteration

                print("=" * 20)
                print(
                    "Cancer({})   ({}/{})  age({})  gender({})  file({})  Time required: {} min   token({} / {})".format(
                        tissue, indice_i,
                        Index_TissueRecord_Index_num,
                        list_ages[indice_s],
                        list_genders[
                            indice_s],
                        file_name,
                        int(estimated_remaining_time / 60),
                        total_tokens_used,
                        model_dict["total_tokens_max"]))
                print(response_str)


        Dict_Extract_GeneText[tissue] = Dict_Extract_GeneText_Tissue
        with open(dir_paths["Dict_Extract_GeneText.json"], 'w') as json_file:
            json.dump(Dict_Extract_GeneText, json_file, indent=4)
