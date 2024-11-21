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
from scripts.call_llm import get_response, init_llm
from scripts.pathfile import parse_path
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
    from scripts.scp_disgenet import fetch_gene_name, list_tables_and_columns, check_if_gene_exists, \
        get_diseases_for_gene, \
        Diseases_associated_gene, query_gene_disease_association, fetch_disease_nids, get_diseases_associated_with_gene
except:
    from scp_disgenet import fetch_gene_name, list_tables_and_columns, check_if_gene_exists, \
        get_diseases_for_gene, \
        Diseases_associated_gene, query_gene_disease_association, fetch_disease_nids, get_diseases_associated_with_gene

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

torch.cuda.empty_cache()

def has_uppercase(s):
    return any(char.isupper() for char in s)
def has_no_lowercase(s):
    return all(char.isupper() or not char.isalpha() for char in s)
def has_letter(s):
    return any(char.isalpha() for char in s)


def S3_4_Gene_Rename(dir_paths):
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)

    with open(dir_paths["Dict_Gene_Statis.json"], 'r') as file:
        Dict_Gene_Statis = json.load(file)

    for index, (tissue, Dict_Gene_Statis_Single) in enumerate(Dict_Gene_Statis.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)

        genes_name = Dict_Gene_Statis_Single["genes_name"]
        genes_num = Dict_Gene_Statis_Single["genes_num"]
        genes_index = Dict_Gene_Statis_Single["genes_index"]

        genes_exists = [False] * len(genes_name)
        genes_name_new = genes_name.copy()

        for g1 in range(len(genes_name)):
            gene_name = genes_name[g1]
            gene_num = genes_num[g1]
            gene_exists = check_if_gene_exists(dir_paths["disgenet_2020.db"], gene_name)
            genes_exists[g1] = gene_exists
            if not gene_exists:
                # gene_name_list_orig = gene_name.split()
                gene_name_list_orig = re.split(r'\s|/', gene_name)

                gene_name_list = []
                for gene_name_s in gene_name_list_orig:
                    if len(gene_name_s) >= 2:
                        if gene_name_s[0] == "(" and gene_name_s[-1] == ")":
                            gene_name_s = gene_name_s[1:-1]
                        if gene_name_s[-1] == "+":
                            gene_name_s = gene_name_s[:-1]

                        if gene_name_s[-1] == "-":
                            pass
                        elif "-positive" in gene_name_s:
                            segs = gene_name_s.split("-positive")
                            if has_uppercase(segs[0]) and has_no_lowercase(segs[0]) and has_letter(segs[0]):
                                gene_name_list.append(segs[0])
                        elif "-" in gene_name_s[0:-2]:
                            if has_uppercase(gene_name_s) and has_no_lowercase(gene_name_s) and has_letter(gene_name_s):
                                gene_name_list.append(gene_name_s)
                                gene_name_list.append(gene_name_s.replace("-", ""))
                        else:
                            if has_uppercase(gene_name_s) and has_no_lowercase(gene_name_s) and has_letter(gene_name_s):
                                gene_name_list.append(gene_name_s)
                    else:
                        if has_uppercase(gene_name_s) and has_no_lowercase(gene_name_s) and has_letter(gene_name_s):
                            gene_name_list.append(gene_name_s)

                for gene_name_s in gene_name_list:
                    if gene_name_s == "7/8":
                        ssu=1
                    print("-"*5)
                    print(gene_name_s)

                Find_io = False
                print("[({}): {}]".format(gene_name, gene_name_list))
                for gene_name_s in gene_name_list:
                    if any(char.islower() for char in gene_name_s):
                        pass
                    else:
                        print("  ({})  →  ({})".format(gene_name, gene_name_s))
                        gene_exists_s = check_if_gene_exists(dir_paths["disgenet_2020.db"], gene_name_s)
                        if gene_exists_s:
                            genes_name_new[g1] = gene_name_s
                            print("  √  DisGeNET  ({})({})Change to new name({})  ".format(gene_name, gene_num, gene_name_s))
                            Find_io = True
                            uu = 1
                        else:
                            gene_name_new = fetch_gene_name(dir_paths,gene_name_s, browser)
                            if len(gene_name_new)>0:
                                Find_io = True
                                genes_name_new[g1] = gene_name_new
                                print("  √  NCBI  {}({})Change to new name{}".format(gene_name, gene_num, gene_name_new))
                                uu=1
                            else:
                                print("  x   {}({}) Does not exist".format(gene_name, gene_num))
                    if Find_io:
                        break

                genes_exists[g1] = Find_io

            else:
                try:
                    print("  --  {}({}) ".format(genes_name[g1], genes_num[g1]))
                except:
                    uu=1

        genes_name_s = []
        for g1 in range(len(genes_exists)):
            gene_name = genes_name[g1]
            gene_name_new = genes_name_new[g1]
            gene_exists = genes_exists[g1]
            if gene_exists and gene_name_new not in genes_name_s:
                genes_name_s.append(gene_name_new)


        genes_num_s = [0]* len(genes_name_s)
        genes_index_s = {}
        for g1 in range(len(genes_name_s)):
            gene_name_s = genes_name_s[g1]
            indices = [index for index, element in enumerate(genes_name) if element == gene_name_s]
            genes_index_full = []

            if len(indices)>1:
                uu=1

            for index in indices:
                gene_num = genes_num[index]
                gene_name = genes_name[index]
                gene_index = genes_index[gene_name]
                gene_exists = genes_exists[index]
                if gene_exists:
                    genes_num_s[g1] = genes_num_s[g1] + gene_num
                    genes_index_full = genes_index_full + gene_index

                    list(set(genes_index_full))

            genes_index_s[gene_name_s] = genes_index_full

        # Pack genes_name_s and genes_num_s into a list of tuples and sort them by the value of genes_num_s
        sorted_genes = sorted(zip(genes_name_s, genes_num_s), key=lambda x: x[1], reverse=True)
        # Separate genes_name_s and genes_num_s from the sorted list of tuples
        sorted_genes_name_s = []
        sorted_genes_num_s = []
        for gene in sorted_genes:
            if gene[1]>0:
                sorted_genes_name_s.append(gene[0])
                sorted_genes_num_s.append(gene[1])


        Dict_Gene_Statis[tissue] = {"genes_name": sorted_genes_name_s,
                                    "genes_num": sorted_genes_num_s,
                                    "genes_index":genes_index_s}

    with open(dir_paths["Dict_Gene_Statis_Rename.json"], 'w') as json_file:
        json.dump(Dict_Gene_Statis, json_file, indent=4)

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S3_4_Gene_Rename(dir_paths)