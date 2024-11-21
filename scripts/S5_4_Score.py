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
try:
    from scripts.call_llm import get_response, init_llm, get_model_dict
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm, get_model_dict
    from pathfile import parse_path
torch.cuda.empty_cache()
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cuda"


def S5_4_Score(dir_paths):
    # Dict_Gene_Val_pth = r'D:\\Codes\\GeneExplorer\\results\\data_files\\Dict_Gene_Val.json'
    Dict_Gene_Val_pth = dir_paths["Dict_Gene_Val.json"]

    with open(Dict_Gene_Val_pth, 'r') as file:
        Dict_Gene_Val = json.load(file)

    model_type = "local"
    model_name = "numind/NuExtract-1.5"

    client, pipeline, tokenizer = init_llm(model_type, model_name)
    template = """{
        "Selected Options": ""
    }"""
    """

    """
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
            if gene_level == 3:
                gene_name = genes_name[g1]
                gene_num = genes_num[g1]
                val_web_urls = val_webs[g1]["urls"]
                val_web_texts = val_webs[g1]["texts"]
                val_web_types = val_webs[g1]["types"]
                val_web_texts_clean = val_webs[g1]["clean texts"]
                val_llms = val_webs[g1]["val llm"]
                val_scores = [""]*len(val_web_urls)

                print("→ " + " " * 4 + "GeneName:{}: GeneNum:{} GeneLevel:{}".format(gene_name,gene_num,gene_level) + "     " + "=" * 5)

                for u1, val_llm in enumerate(val_llms):
                    if len(val_llm)>1000:
                        prompt_str = val_llm[:1000]
                    else:
                        prompt_str = val_llm
                    system_content = ""
                    user_content = ""
                    response_str, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer,
                                                              prompt_str,system_content, user_content, template)
                    print(response_str)
                    val_scores[u1] = response_str

                val_webs[g1]["scores"] = val_scores

        Dict_Gene_Val[tissue] = {"genes_name": genes_name,
                                 "genes_level": genes_level,
                                 "genes_num": genes_num,
                                 "genes_index": genes_index,
                                 "genes_Score_CGC_GeneID": genes_Score_CGC_GeneID,
                                 "genes_Score_CGC_Tier": genes_Score_CGC_Tier,
                                 "genes_Score_CGC_Exist": genes_Score_CGC_Exist,
                                 "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                 "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                 "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max,
                                 "val_webs": val_webs}

        with open(dir_paths["Dict_Gene_Val.json"], 'w') as json_file:
            json.dump(Dict_Gene_Val, json_file, indent=4)



if __name__ == "__main__":
    from get_dir_paths import get_dir_paths
    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)
    S5_4_Score(dir_paths)



