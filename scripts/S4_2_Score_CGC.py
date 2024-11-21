import json
import ollama
import re
import time
import pickle
import os
import re
import time
import json
import os
import ast
from transformers import AutoTokenizer
import transformers
import torch
import pprint
from collections import Counter
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from collections import Counter
import json
import requests
from bs4 import BeautifulSoup
import re
try:
    from scripts.call_llm import get_response, init_llm
    from scripts.pathfile import parse_path
    from scripts.scp_disgenet import list_tables_and_columns, check_if_gene_exists, get_diseases_for_gene, \
        Diseases_associated_gene, query_gene_disease_association, fetch_disease_nids, get_diseases_associated_with_gene
except:
    from call_llm import get_response, init_llm
    from pathfile import parse_path
    from scp_disgenet import list_tables_and_columns, check_if_gene_exists, get_diseases_for_gene, \
        Diseases_associated_gene, query_gene_disease_association, fetch_disease_nids, get_diseases_associated_with_gene
torch.cuda.empty_cache()


def replace_word(sentence, old_word, new_word):
    # Use regular expressions to match complete words, ignoring case when replacing
    if not isinstance(sentence, str):
        raise TypeError("sentence must be a string")
    return re.sub(r'\b{}\b'.format(re.escape(old_word)), new_word, sentence, flags=re.IGNORECASE)

def has_word(sentence, word):
    # Use regular expressions to match complete words
    pattern = r'\b{}\b'.format(re.escape(word))
    return bool(re.search(pattern, sentence))


def change_list_abb(TumourSomaticType_t, Census_abb_dict):
    TumourSomaticType_new = []
    for t in TumourSomaticType_t:
        modified_sentence = t
        for index, (abb, Census_abb_dict_Single) in enumerate(Census_abb_dict.items()):
            if has_word(modified_sentence, abb):
                modified_sentence = replace_word(modified_sentence, abb, Census_abb_dict_Single)
        TumourSomaticType_new.append(modified_sentence)
    # print("{} → {}".format(TumourSomaticType_t, TumourSomaticType_new))
    return TumourSomaticType_new

def S4_2_Score_CGC(dir_paths):
    # 2.Read the list of oncogene names, including their abbreviations
    data = pd.read_csv(dir_paths["Census_abbreviations.csv"])
    first_column = data.iloc[:, 0].tolist()
    second_column = data.iloc[:, 1].tolist()
    Census_abb_dict = {}
    for i1 in range(len(first_column)):
        Census_abb_dict[first_column[i1]] = second_column[i1]

    # 3.Read the list of oncogene names and save it in list_oncogenes
    data = pd.read_csv(dir_paths["Census_allTue May 14 09_10_51 2024.csv"])
    list_oncogenes = data.iloc[:, 0].tolist()
    list_oncogenesName = data.iloc[:, 1].tolist()
    list_oncogenesID = data.iloc[:, 2].tolist()
    list_tiers = data.iloc[:, 4].tolist()
    list_oncogenes_TumourSomaticTypes = data.iloc[:, 9].tolist()
    list_oncogenes_TumourGermlineTypes = data.iloc[:, 10].tolist()
    list_oncogenes_RoleInCancer = data.iloc[:, 14].tolist()
    list_oncogenes_Synonyms = data.iloc[:, 19].tolist()
    # ["fusion","oncogene","TSG"]
    list_TumourType = [[]] * len(list_oncogenes_TumourSomaticTypes)
    for T1 in range(len(list_oncogenes_TumourSomaticTypes)):
        TumourSomaticType = list_oncogenes_TumourSomaticTypes[T1]
        TumourGermlineType = list_oncogenes_TumourGermlineTypes[T1]
        if isinstance(TumourSomaticType, str):
            TumourSomaticType_t = [item.strip() for item in TumourSomaticType.split(',')]
            list_TumourType[T1] = change_list_abb(TumourSomaticType_t, Census_abb_dict)
        if isinstance(TumourGermlineType, str):
            TumourGermlineType_t = [item.strip() for item in TumourGermlineType.split(',')]
            list_TumourType[T1] = change_list_abb(TumourGermlineType_t, Census_abb_dict)

    dict_OncogenesNames = {}
    for index in range(len(list_oncogenes)):
        oncogenes_Synonyms = list_oncogenes_Synonyms[index]
        if isinstance(oncogenes_Synonyms, str):
            list_of_synonyms = [item.strip() for item in oncogenes_Synonyms.split(',')]
            dict_OncogenesNames[list_oncogenes[index]] = [list_oncogenes[index]] + list_of_synonyms
        else:
            dict_OncogenesNames[list_oncogenes[index]] = []

    with open(dir_paths["Dict_TissueCancerNames_Full.json"], 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    with open(dir_paths["Dict_Gene_Score.json"], 'r') as file:
        Dict_Gene_Score = json.load(file)


    Dict_Score_CGC = {}
    for index, (tissue, Dict_Gene_Score_Single) in enumerate(Dict_Gene_Score.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)

        Dict_TissueCancerNames_Single = Dict_TissueCancerNames[tissue]
        genes_name = Dict_Gene_Score_Single["genes_name"]
        genes_num = Dict_Gene_Score_Single["genes_num"]
        genes_index = Dict_Gene_Score_Single["genes_index"]
        genes_Score_DisGeNET_min = Dict_Gene_Score_Single["genes_Score_DisGeNET_min"]
        genes_Score_DisGeNET_max = Dict_Gene_Score_Single["genes_Score_DisGeNET_max"]
        genes_Score_DisGeNET_exist = Dict_Gene_Score_Single["genes_Score_DisGeNET_exist"]

        genes_Score_CGC_GeneID = [-1] * len(genes_name)
        genes_Score_CGC_Tier = [-1] * len(genes_name)
        genes_Score_CGC_Exist = [False] * len(genes_name)

        for g1 in range(len(genes_name)):
            gene_name = genes_name[g1]
            gene_num = genes_num[g1]
            gene_index = genes_index[gene_name]

            gene_Score_DisGeNET_min = genes_Score_DisGeNET_min[g1]
            gene_Score_DisGeNET_max = genes_Score_DisGeNET_max[g1]
            gene_Score_DisGeNET_exist = genes_Score_DisGeNET_exist[g1]

            """
            Check whether the gene exists in the table
            """
            find_gene_in_dict = False
            for index_g, (GeneSymbol, list_OncogenesNames) in enumerate(dict_OncogenesNames.items()):
                # print(f"Index {index}: Key {GeneSymbol}, Value {list_OncogenesNames}")
                if gene_name in list_OncogenesNames:
                    find_gene_in_dict = True
                    break

            """
            Check whether this gene is a related gene for this cancer
            """
            key_names = []
            if tissue == 'Breast':
                key_names = key_names + ["breast"]
            elif tissue == 'Myeloid':
                key_names = key_names + ["myeloid"]
            elif tissue == 'Lung':
                key_names = key_names + ["lung"]
            if tissue == 'Bowel':
                key_names = key_names + ["intestine"]
            elif tissue == 'CNS/Brain':
                # key_names = "no CNS"
                key_names = key_names + ["central nervous system"]
            elif tissue == 'Lymphoid':
                key_names = key_names + ["lymphoma", "lymphoid"]
            else:
                key_names = key_names + [tissue.lower()]

            for t1 in range(len(Dict_TissueCancerNames_Single)):
                Dict_TissueCancerNames_S = Dict_TissueCancerNames_Single[t1]
                # if isinstance(Dict_TissueCancerNames_S["name"], list):
                #     print("The variable is a list（list）")
                # elif isinstance(Dict_TissueCancerNames_S["name"], str):
                #     print("The variable is a str（str）")
                key_names = key_names + [Dict_TissueCancerNames_S["name"]]
                # try:
                #     key_names.append(Dict_TissueCancerNames_S["name"])
                # except:
                #     uu=1
            # for key_name in key_names:
            #     print(key_name)
            find_gene_is = False
            for key_name_s in list_TumourType[index_g]:
                for key_name in key_names:
                    if key_name.lower() in key_name_s.lower():
                        find_gene_is = True

            find_gene_is_Name = False
            if key_name.lower() in list_oncogenesName[index_g].lower():
                find_gene_is_Name = True

            if find_gene_is or find_gene_is_Name:
                genes_Score_CGC_Exist[g1] = True
            else:
                genes_Score_CGC_Exist[g1] = False
            genes_Score_CGC_GeneID[g1] = int(list_oncogenesID[index_g])
            genes_Score_CGC_Tier[g1] = list_tiers[index_g]

            output_str = ""
            if genes_Score_CGC_Exist[g1]:
                output_str = output_str + " √ "
            else:
                output_str = output_str + " x "
            print("({}) gene{}(Num. {}) - is or not oncogenes of - cancer{}(keyword{})".format(output_str, gene_name, gene_num, tissue,
                                                                                     key_name))

        Dict_Score_CGC[tissue] = {"genes_name": genes_name,
                                  "genes_num": genes_num,
                                  "genes_index": genes_index,
                                  "genes_Score_CGC_GeneID": genes_Score_CGC_GeneID,
                                  "genes_Score_CGC_Tier": genes_Score_CGC_Tier,
                                  "genes_Score_CGC_Exist": genes_Score_CGC_Exist,
                                  "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                  "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                  "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max}

    with open(dir_paths["Dict_Gene_Score.json"], 'w') as json_file:
        json.dump(Dict_Score_CGC, json_file, indent=4)

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S4_2_Score_CGC(dir_paths)