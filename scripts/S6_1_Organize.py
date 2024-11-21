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
import pprint
from collections import Counter
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import shutil
import torch
import csv

try:
    from scripts.call_llm import get_response, init_llm, get_model_dict
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm, get_model_dict
    from pathfile import parse_path
torch.cuda.empty_cache()
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cuda"


def S6_1_organize(dir_paths):
    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()
    PMIDs = df['PMID'].tolist()
    file_paths= df['file_path'].tolist()
    Dict_Gene_Val_pth = dir_paths["Dict_Gene_Val.json"]

    with open(Dict_Gene_Val_pth, 'r') as file:
        Dict_Gene_Val = json.load(file)

    headers = ["ID",
               "Tissue",
               "Mutant Gene",
               "Level",
               "DisGeNET: Exist",
               "DisGeNET: Min(Association Score)",
               "DisGeNET: Max(Association Score)",
               "CGC: Exist",
               "CGC: Tier",
               "CGC: GeneID",
               "Evidences: Total number of evidence",
               "Evidences: Total number of evidence(Associated)",
               "Evidences: Total number of evidence(Not Associated)",
               "Evidences: Total number of evidence(No Enough Information)",
               "Evidences: Urls",
               "Evidences: Scores(A:Ass., B: Not Ass., C: No Enough Information)",
               "Cases: Number of Cases",
               "Cases: Case No. of PMC-Patients",
               "Cases: PMC PMIDs",
               "Cases: PMC File Paths"
               ]

    db_list = []

    for index, (tissue, Dict_Gene_Val_Single) in enumerate(Dict_Gene_Val.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)

        genes_name = Dict_Gene_Val_Single["genes_name"]
        genes_level = Dict_Gene_Val_Single["genes_level"]
        genes_num = Dict_Gene_Val_Single["genes_num"]
        genes_index = Dict_Gene_Val_Single["genes_index"]
        genes_Score_CGC_GeneID = Dict_Gene_Val_Single["genes_Score_CGC_GeneID"]
        genes_Score_CGC_Tier = Dict_Gene_Val_Single["genes_Score_CGC_Tier"]
        genes_Score_CGC_Exist = Dict_Gene_Val_Single["genes_Score_CGC_Exist"]
        genes_Score_DisGeNET_exist = Dict_Gene_Val_Single["genes_Score_DisGeNET_exist"]
        genes_Score_DisGeNET_min = Dict_Gene_Val_Single["genes_Score_DisGeNET_min"]
        genes_Score_DisGeNET_max = Dict_Gene_Val_Single["genes_Score_DisGeNET_max"]
        val_webs = Dict_Gene_Val_Single["val_webs"]

        for g1, gene_level in enumerate(genes_level):
            gene_name = genes_name[g1]
            gene_num = genes_num[g1]
            gene_index = genes_index[gene_name]
            val_web = val_webs[g1]
            if gene_level == 3:
                val_web_urls = val_web["urls"]
                val_web_texts = val_web["texts"]
                val_web_types = val_web["types"]
                val_web_texts_clean = val_web["clean texts"]
                val_llms = val_web["val llm"]
                val_scores = val_web["scores"]
                val_scores_evidences = val_web["scores evidences"]

                print("→ " + " " * 4 + "GeneName:{}: GeneNum:{} GeneLevel:{}".format(gene_name, gene_num,
                                                                                     gene_level) + "     " + "=" * 5)
                print(" {} ".format(val_scores_evidences))
            else:
                val_scores_evidences = [0, 0, 0, 0]
                val_web_urls = []
                val_web_texts_clean = []
                val_scores = []

            PMC_file_paths = []
            PMC_PMIDs = []
            for gene_index_single in gene_index:
                PMC_PMIDs.append(PMIDs[gene_index_single])
                PMC_file_paths.append(file_paths[gene_index_single])

            db_list_single = {}
            db_list_single["ID"] = len(db_list)
            db_list_single["Tissue"] = tissue
            db_list_single["Mutant Gene"] = gene_name
            db_list_single["Level"] = gene_level
            db_list_single["DisGeNET: Exist"] = genes_Score_DisGeNET_exist[g1]
            db_list_single["DisGeNET: Min(Association Score)"] = genes_Score_DisGeNET_min[g1]
            db_list_single["DisGeNET: Max(Association Score)"] = genes_Score_DisGeNET_max[g1]
            db_list_single["CGC: Exist"] = genes_Score_CGC_Exist[g1]
            db_list_single["CGC: Tier"] = genes_Score_CGC_Tier[g1]
            db_list_single["CGC: GeneID"] = genes_Score_CGC_GeneID[g1]
            db_list_single["Evidences: Total number of evidence"] = val_scores_evidences[0]
            db_list_single["Evidences: Total number of evidence(Associated)"] = val_scores_evidences[1]
            db_list_single["Evidences: Total number of evidence(Not Associated)"] = val_scores_evidences[2]
            db_list_single["Evidences: Total number of evidence(No Enough Information)"] = val_scores_evidences[3]
            db_list_single["Evidences: Urls"] = val_web_urls
            db_list_single["Evidences: Scores(A:Ass., B: Not Ass., C: No Enough Information)"] = val_scores
            db_list_single["Cases: Number of Cases"] = gene_num
            db_list_single["Cases: Case No. of PMC-Patients"] = gene_index
            db_list_single["Cases: PMC PMIDs"] = PMC_PMIDs
            db_list_single["Cases: PMC File Paths"] = PMC_file_paths

            db_list.append(db_list_single)

    file_path = os.path.join(dir_paths["datasets_dir"], 'PCGsDB.csv')
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(db_list)
    uu = 1


if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)
    S6_1_organize(dir_paths)
