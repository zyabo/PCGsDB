
"""
基于基因-疾病关联性的基因排除
"""
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

torch.cuda.empty_cache()

def S4_1_Score_DisGeNET(dir_paths):
    with open(dir_paths["Dict_TissueCancerNames_Full.json"], 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    with open(dir_paths["Dict_Gene_Statis_Rename.json"], 'r') as file:
        Dict_Gene_Statis = json.load(file)


    Dict_Score_DisGeNET = {}

    for index, (tissue, Dict_Gene_Statis_Single) in enumerate(Dict_Gene_Statis.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)
        Dict_TissueCancerNames_Single = Dict_TissueCancerNames[tissue]
        genes_name = Dict_Gene_Statis_Single["genes_name"]
        genes_num = Dict_Gene_Statis_Single["genes_num"]
        genes_index = Dict_Gene_Statis_Single["genes_index"]

        genes_Score_DisGeNET_min = [-1.0] * len(genes_name)
        genes_Score_DisGeNET_max = [-1.0] * len(genes_name)
        genes_Score_DisGeNET_exist = [False] * len(genes_name)

        for g1 in range(len(genes_name)):
            gene_name = genes_name[g1]
            gene_num = genes_num[g1]
            gene_index = genes_index[gene_name]
            if check_if_gene_exists(dir_paths["disgenet_2020.db"], gene_name):
                associations = get_diseases_associated_with_gene(dir_paths["disgenet_2020.db"], gene_name, tissue, gene_num)

                list_disease = []
                list_score = []
                list_association_type = []
                for disease, score, association_type, sentence in associations:
                    for Dict_TissueCancerNames_S in Dict_TissueCancerNames_Single:
                        TissueCancerName = Dict_TissueCancerNames_S["name"]
                        if TissueCancerName in disease.lower():
                            list_disease.append(disease)
                            list_score.append(score)
                            list_association_type.append(association_type)
                            # print("Disease: ", disease)
                            # print("Score: ", score)
                            # print("Association Type: ", association_type)
                            # print("Evidence Sentence: ", sentence)
                            # print("-" * 30)

                if len(list_score) > 0:
                    genes_Score_DisGeNET_min[g1] = min(list_score)
                    genes_Score_DisGeNET_max[g1] = max(list_score)
                    genes_Score_DisGeNET_exist[g1] = True
                    if genes_Score_DisGeNET_max[g1] == 0:
                        print("++ {} ({})   {}-{}".format(gene_name, gene_num, genes_Score_DisGeNET_min[g1], genes_Score_DisGeNET_max[g1]))

                else:
                    print("   -- {} ({})".format(gene_name, gene_num))

            else:
                print("   <<  {} ({})".format(gene_name, gene_num))
            uu=1

        Dict_Score_DisGeNET[tissue] = {"genes_name": genes_name,
                                       "genes_num": genes_num,
                                       "genes_index": genes_index,
                                       "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                       "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                       "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max}

    with open(dir_paths["Dict_Gene_Score.json"], 'w') as json_file:
        json.dump(Dict_Score_DisGeNET, json_file, indent=4)

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S4_1_Score_DisGeNET(dir_paths)