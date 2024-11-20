import pickle
import json
import pandas as pd
import ollama
import re
import time
import pickle
import os
import pandas as pd
import json
from scripts.call_llm import get_response, init_llm, get_model_dict
from scripts.pathfile import parse_path
import pprint
from collections import Counter
import matplotlib.pyplot as plt


def get_prompt_0(record, age, gender, gene, diseases):
    user_content = """
Based on the medical record description of the patient ({} {}), is the {} gene mutation strongly associated to {}?

""".format(age, gender, gene, diseases)
    user_content = user_content + """
Please fill in the dict in python format below.
degree_of_association = {"degree of association?": "strong, medium, or weak"}
Just output the above dict.
"""

    #     user_content = user_content + """
    # """
    system_content = """
The following is the medical history of this patient ({} {}):
{} 
""".format(age, gender, record)

    prompt_str = user_content + system_content

    return prompt_str, user_content, system_content


def get_prompt(record, age, gender, gene, diseases):
    user_content = """
According to the patient's ({} {}) medical record, 
if the patient has both {} gene mutation and disease {}, then answer yes; 
if not, answer no. 
Note that relatives should be excluded.
""".format(age, gender, gene, diseases)
    user_content = user_content + """
Please fill in the dict in python format below.
answer = {"choose": "yes or no"}
Just output the above dict.
"""
    #     user_content = user_content + """
    # """
    system_content = """
The following is the medical history of this patient ({} {}):
{} 
""".format(age, gender, record)

    prompt_str = user_content + system_content

    return prompt_str, user_content, system_content


def S5_1_Score_LLM(dir_paths,model_type,model_name):
    client, pipeline, tokenizer = init_llm(model_type, model_name)

    """
    2. Read the medical records of all cases and save them in list_records
    """
    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()
    list_ages = df['age'].tolist()
    list_genders = df['gender'].tolist()
    list_file_paths = df['file_path'].tolist()

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"], 'r') as file:
        Dict_Index_TissueRecord_Full = json.load(file)

    with open(dir_paths["SelectedTissue.json"], 'r') as json_file:
        SelectedTissue = json.load(json_file)

    with open(dir_paths["Dict_Gene_Score.json"], 'r') as file:
        Dict_Gene_Score = json.load(file)

    with open(dir_paths["Dict_Gene_Level.json"], 'r') as file:
        Dict_Gene_Level = json.load(file)


    Dict_Score_LLM = Dict_Gene_Level

    for index, (tissue, Dict_Gene_Level_Single) in enumerate(Dict_Gene_Level.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)
        uu=1
        Dict_Index_TissueRecord_Full_Single = Dict_Index_TissueRecord_Full[tissue]
        Dict_Index_TissueRecord_Single = Dict_Index_TissueRecord[tissue]
        Dict_Index_TissueRecord_Single_index = Dict_Index_TissueRecord_Single['index']
        Dict_Index_TissueRecord_Single_subdisease = Dict_Index_TissueRecord_Single['subdisease']

        genes_name = Dict_Gene_Level_Single["genes_name"]
        genes_level = Dict_Gene_Level_Single["genes_level"]
        genes_num = Dict_Gene_Level_Single["genes_num"]
        genes_index = Dict_Gene_Level_Single["genes_index"]
        genes_Score_DisGeNET_min = Dict_Gene_Level_Single["genes_Score_DisGeNET_min"]
        genes_Score_DisGeNET_max = Dict_Gene_Level_Single["genes_Score_DisGeNET_max"]
        genes_Score_DisGeNET_exist = Dict_Gene_Level_Single["genes_Score_DisGeNET_exist"]
        genes_Score_CGC_GeneID = Dict_Gene_Level_Single["genes_Score_CGC_GeneID"]
        genes_Score_CGC_Tier = Dict_Gene_Level_Single["genes_Score_CGC_Tier"]
        genes_Score_CGC_Exist = Dict_Gene_Level_Single["genes_Score_CGC_Exist"]

        genes_Score_LLM = [0.0] * len(genes_name)
        genes_Score_LLM_StrongAss_Num = [0] * len(genes_name)
        genes_Score_LLM_associations = [[]] * len(genes_name)
        for g1 in range(len(genes_name)):
            gene_name = genes_name[g1]
            gene_num = genes_num[g1]
            gene_index = genes_index[gene_name]

            degree_of_association = []
            for index_i in gene_index:
                record_s = list_records[index_i]
                age_list = eval(list_ages[index_i])
                age = str(int(age_list[0][0])) + "-" + age_list[0][1] + "-old"
                if list_genders[index_i] == "M":
                    gender = "Male"
                if list_genders[index_i] == "F":
                    gender = "Female"

                subdisease = Dict_Index_TissueRecord_Single_subdisease[
                    Dict_Index_TissueRecord_Single_index.index(index_i)]
                subdisease = list(set(subdisease))
                subdisease_str = ", ".join(subdisease)

                if gene_name not in record_s:
                    print(index_i)
                    uu = 1

                prompt_str, user_content, system_content = get_prompt(record_s, age, gender, gene_name, subdisease_str)
                # prompt_str, user_content, system_content = get_prompt(record_s, gene_name, age, gender)
                response_str, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer,
                                                          prompt_str, system_content, user_content)


                try:
                    dict_content = re.search(r'\{([^}]*)\}', response_str).group(0)
                    response_dict = eval(dict_content)
                    response_association = response_dict["degree of association?"]
                except:
                    response_dict = {}
                    response_association = ""

                degree_of_association.append(response_association)
                # print(response_association)
                uu = 1

            genes_Score_LLM_associations[g1] = degree_of_association

            Score_LLM_Num_weak = 0
            Score_LLM_Num_strong = 0
            Score_LLM_Value = 0.0
            for genes_Score_LLM_association in degree_of_association:
                if "weak" in genes_Score_LLM_association:
                    Score_LLM_Value = Score_LLM_Value + 0.0
                    Score_LLM_Num_weak = Score_LLM_Num_weak + 1
                if "medium" in genes_Score_LLM_association:
                    Score_LLM_Value = Score_LLM_Value + 0.5
                    # Score_LLM_Num = Score_LLM_Num + 1
                if "strong" in genes_Score_LLM_association:
                    Score_LLM_Value = Score_LLM_Value + 1.0
                    Score_LLM_Num_strong = Score_LLM_Num_strong + 1
                    genes_Score_LLM_StrongAss_Num[g1] = genes_Score_LLM_StrongAss_Num[g1] + 1
            if (Score_LLM_Num_weak+Score_LLM_Num_strong)>0:
                genes_Score_LLM[g1] = Score_LLM_Value / (Score_LLM_Num_weak+Score_LLM_Num_strong)

            print("{}({}) | {} | {}".format(gene_name, gene_num, genes_Score_LLM[g1], degree_of_association))

        Dict_Score_LLM[tissue] = {"genes_name": genes_name,
                                  "genes_num": genes_num,
                                  "genes_index": genes_index,
                                  "genes_Score_CGC_GeneID": genes_Score_CGC_GeneID,
                                  "genes_Score_CGC_Tier": genes_Score_CGC_Tier,
                                  "genes_Score_CGC_Exist": genes_Score_CGC_Exist,
                                  "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                  "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                  "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max,
                                  "genes_Score_LLM_associations": genes_Score_LLM_associations,
                                  "genes_Score_LLM_StrongAss_Num": genes_Score_LLM_StrongAss_Num,
                                  "genes_Score_LLM": genes_Score_LLM}

    with open(dir_paths["Dict_Score_LLM.json"], 'w') as json_file:
        json.dump(Dict_Score_LLM, json_file, indent=4)


if __name__ == "__main__":
    from get_dir_paths import get_dir_paths
    current_dir_path = r"D:\Codes\GeneExplorer"
    dir_paths = get_dir_paths(current_dir_path)

    """
    1. init llm
    """
    # model_type = "local"
    model_type = "api"

    # model_name = "qwen-long"
    # model_name = "llama3"
    # model_name = "numind/NuExtract-1.5"
    model_name = "chain-of-thoughts.q5"

    S5_1_Score_LLM(dir_paths, model_type, model_name)

    uu=1