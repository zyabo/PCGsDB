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

def get_prompt_text(val_web_text, tissue, gene_name):
    prompt_str = """
According to the text below, can we conclude from the text above that {} cancer is related to {} gene mutation?：
Original text:{} 


According to the above text, can we conclude from the text above that {} cancer is related to {} gene mutation? Please select an option.
Option A:"yes"
Option B:"no"
Option C:"not enough information"
Selected option:
""".format(tissue, gene_name,val_web_text, tissue, gene_name)
    return prompt_str

def S5_2_Val_Text(dir_paths):
    # Dict_Gene_Val_pth = r'D:\\Codes\\GeneExplorer\\results\\data_files\\Dict_Gene_Val.json'
    Dict_Gene_Val_pth = dir_paths["Dict_Gene_Val.json"]

    with open(Dict_Gene_Val_pth, 'r') as file:
        Dict_Gene_Val = json.load(file)

    # model_type = "api"
    # model_name = "llama3.1:8b"

    # client, pipeline, tokenizer = init_llm(model_type, model_name)

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
                print("→ " + " " * 10 + "     " + "{}".format(gene_name) + "     " + " " * 10)

                val_web_urls = val_webs[g1]["urls"]
                val_web_texts = val_webs[g1]["texts"]
                val_web_types = val_webs[g1]["types"]
                val_web_texts_clean = val_web_texts

                for u1, val_web_type in enumerate(val_web_types):
                    if val_web_type == "html":
                        val_web_text = val_web_texts[u1]

                        soup = BeautifulSoup(val_web_text, 'html.parser')
                        # Extract the desired data from the parsed HTML
                        # For example, to extract all the text from the page:
                        text = soup.get_text()
                        text = text.replace("\n","")
                        text = text.replace("  ", " ")
                        val_web_texts_clean[u1] = text

                        # # llm 解析
                        # prompt_str = get_prompt_text(text,tissue, gene_name)
                        # response_str, total_tokens = get_response(model_type, model_name, client, pipeline, tokenizer,
                        #                                           prompt_str)
                        #
                        # print(response_str)
                        # val_web_texts_clean[u1] = response_str

                val_webs[g1]["clean texts"] = val_web_texts_clean

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
    S5_2_Val_Text(dir_paths)


