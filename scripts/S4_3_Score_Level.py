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
try:
    from scripts.call_llm import get_response, init_llm
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm
    from pathfile import parse_path
import pprint
from collections import Counter
import matplotlib.pyplot as plt


def S4_3_Score_Level(dir_paths):
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

    with open(dir_paths["Dict_Gene_Score.json"], 'r') as file:
        Dict_Gene_Score = json.load(file)

    genes_n_all = [0,0,0,0,0]
    genes_num_n_all = [0, 0, 0, 0, 0]
    Dict_Gene_Level = Dict_Gene_Score
    for index, (tissue, Dict_Gene_Score_Single) in enumerate(Dict_Gene_Score.items()):
        # print("*" * 100)
        # print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)

        # ['genes_name', 'genes_num', 'genes_index',
        # 'genes_Score_CGC_GeneID', 'genes_Score_CGC_Tier', 'genes_Score_CGC_Exist',
        # 'genes_Score_DisGeNET_exist', 'genes_Score_DisGeNET_min', 'genes_Score_DisGeNET_max']

        genes_name = Dict_Gene_Score_Single["genes_name"]
        genes_num = Dict_Gene_Score_Single["genes_num"]
        genes_index = Dict_Gene_Score_Single["genes_index"]
        genes_Score_CGC_GeneID = Dict_Gene_Score_Single["genes_Score_CGC_GeneID"]
        genes_Score_CGC_Tier = Dict_Gene_Score_Single["genes_Score_CGC_Tier"]
        genes_Score_CGC_Exist = Dict_Gene_Score_Single["genes_Score_CGC_Exist"]
        genes_Score_DisGeNET_exist = Dict_Gene_Score_Single["genes_Score_DisGeNET_exist"]
        genes_Score_DisGeNET_min = Dict_Gene_Score_Single["genes_Score_DisGeNET_min"]
        genes_Score_DisGeNET_max = Dict_Gene_Score_Single["genes_Score_DisGeNET_max"]

        genes_level = [0] * len(genes_name)
        genes_level_n_1 = 0
        genes_level_n_2 = 0
        genes_level_n_3 = 0

        genes_level_num_n_1 = 0
        genes_level_num_n_2 = 0
        genes_level_num_n_3 = 0

        for g1, gene_name in enumerate(genes_name):
            """
            3. Not CGC, not DisGeNET
            2. Yes CGC, not DisGeNET
            1. Not CGC, yes DisGeNET (low score)
            0. Yes DisGeNET (high score)
            """
            if (not genes_Score_CGC_Exist[g1]) and (not genes_Score_DisGeNET_exist[g1]):
                genes_level[g1] = 3
                genes_level_n_3 = genes_level_n_3 + 1
                genes_level_num_n_3 = genes_level_num_n_3 + genes_num[g1]

            if (genes_Score_CGC_Exist[g1]) and (not genes_Score_DisGeNET_exist[g1]):
                genes_level[g1] = 2
                genes_level_n_2 = genes_level_n_2 + 1
                genes_level_num_n_2 = genes_level_num_n_2 + genes_num[g1]

            if (not genes_Score_CGC_Exist[g1]) and (genes_Score_DisGeNET_exist[g1]) and (
                    genes_Score_DisGeNET_max[g1] < 0.1):
                genes_level[g1] = 1
                genes_level_n_1 = genes_level_n_1 + 1
                genes_level_num_n_1 = genes_level_num_n_1 + genes_num[g1]

            # print("genes_level:{} | genes_num:{} gene_name:{} CGC_Exist:{} DisGeNET_exist:{} DisGeNET_max:{}".format(
            #     genes_level[g1], genes_num[g1], gene_name, genes_Score_CGC_Exist[g1], genes_Score_DisGeNET_exist[g1],
            #     genes_Score_DisGeNET_max[g1]))

            # print("{} {} {}".format(genes_Score_CGC_Exist[g1],genes_Score_DisGeNET_exist[g1],genes_Score_DisGeNET_max[g1]))

            # if not(genes_Score_CGC_Exist[g1] and genes_Score_DisGeNET_exist[g1]):
            #     print("{} {}".format(gene_name,genes_num[g1]))

        genes_level_n_0 = len(genes_name) - genes_level_n_1-genes_level_n_2 - genes_level_n_3
        genes_level_num_n_0 = sum(genes_num) - genes_level_num_n_1-genes_level_num_n_2 - genes_level_num_n_3

        genes_n_all[0] = genes_n_all[0] + genes_level_n_0
        genes_n_all[1] = genes_n_all[1] + genes_level_n_1
        genes_n_all[2] = genes_n_all[2] + genes_level_n_2
        genes_n_all[3] = genes_n_all[3] + genes_level_n_3
        genes_n_all[4] = genes_n_all[4] + len(genes_name)

        genes_num_n_all[0] = genes_num_n_all[0] + genes_level_num_n_0
        genes_num_n_all[1] = genes_num_n_all[1] + genes_level_num_n_1
        genes_num_n_all[2] = genes_num_n_all[2] + genes_level_num_n_2
        genes_num_n_all[3] = genes_num_n_all[3] + genes_level_num_n_3
        genes_num_n_all[4] = genes_num_n_all[4] + sum(genes_num)


        print("{} + {} + {} + {} + {} + {}".format(len(genes_name) ,genes_level_n_0 ,genes_level_n_1 ,genes_level_n_2 , genes_level_n_3 ,tissue ))

        Dict_Gene_Level[tissue] = {"genes_name": genes_name,
                                   "genes_level": genes_level,
                                   "genes_num": genes_num,
                                   "genes_index": genes_index,
                                   "genes_Score_CGC_GeneID": genes_Score_CGC_GeneID,
                                   "genes_Score_CGC_Tier": genes_Score_CGC_Tier,
                                   "genes_Score_CGC_Exist": genes_Score_CGC_Exist,
                                   "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                   "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                   "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max}

    with open(dir_paths["Dict_Gene_Level.json"], 'w') as json_file:
        json.dump(Dict_Gene_Level, json_file, indent=4)

    print(genes_n_all)
    print(genes_num_n_all)


if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S4_3_Score_Level(dir_paths)