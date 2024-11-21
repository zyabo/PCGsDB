"""
Gene statistics
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
try:
    from scripts.call_llm import get_response, init_llm
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm
    from pathfile import parse_path
import pprint
from collections import Counter
import matplotlib.pyplot as plt

torch.cuda.empty_cache()


def plt_hist_genes(dir_paths,List_dict_genes, gene_type, do_plt):
    # Count the number of occurrences of each string
    counter = Counter(List_dict_genes)

    # 获取最常见的前10个元素
    top_ten_items = counter.most_common(10)

    # 创建一个新的Counter，仅包含这10个元素
    top_ten_counter = Counter(dict(top_ten_items))

    # Filter out strings that appear more than 2 times and sort them from most to least
    filtered_counter = {k: v for k, v in top_ten_counter.items() if v >= 1}
    sorted_counter = dict(sorted(filtered_counter.items(), key=lambda item: item[1], reverse=True))
    # Get the strings and their counts separately
    try:
        genes, genes_num = zip(*sorted_counter.items())
    except:
        ss=1
    # if gene_type == "Oncogenes":
    #     print(genes)

    if do_plt:
        gene_type = gene_type.replace("/", "_")
        # 设置绘图
        plt.figure(figsize=(6, 22))
        bars = plt.barh(genes, genes_num)
        plt.ylabel('Gene')
        plt.xlabel('Frequency')
        plt.title('{}'.format(gene_type))
        # plt.xticks(rotation=90)
        for bar in bars:
            yval = bar.get_width()
            plt.text(yval, bar.get_y() + bar.get_height() / 2.0, int(yval),
                     va='bottom')  # ha='center' ensures the text is centered on the bar
        plt.savefig(os.path.join(dir_paths["current_dir_path"],"results","figs","gene_histogram({}).png".format(gene_type)), dpi=600,
                    bbox_inches='tight')
        # plt.show()
        plt.close()

    sorted_counter = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))
    genes, genes_num = zip(*sorted_counter.items())
    return genes, genes_num

def S3_3_Gene_Statis(dir_paths):
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

    with open(dir_paths["Dict_Extract_GeneText.json"], 'r') as file:
        Dict_Extract_GeneText = json.load(file)

    with open(dir_paths["Dict_Extract_GeneDict.json"], 'r') as file:
        Dict_Extract_GeneDict = json.load(file)

    if os.path.exists(dir_paths["Dict_Gene_Statis.json"]):
        with open(dir_paths["Dict_Gene_Statis.json"], 'r') as json_file:
            Dict_Gene_Statis = json.load(json_file)
    else:
        Dict_Gene_Statis = {}

    for index, (tissue, Dict_Extract_GeneDict_Single) in enumerate(Dict_Extract_GeneDict.items()):
        List_Oncogenes = []
        List_Oncogenes_Indexs = []
        for index_i, (index_s, Dict_Extract_GeneDict_Single_s) in enumerate(Dict_Extract_GeneDict_Single.items()):
            response_dict = Dict_Extract_GeneDict_Single_s['response_dict']
            try:
                if response_dict['mutated gene'] != ['no mention']:
                    List_Oncogenes = List_Oncogenes + response_dict['mutated gene']
                    List_Oncogenes_Indexs =List_Oncogenes_Indexs + len(response_dict['mutated gene']) * [int(index_s)]
                    uu=1
                # if ((response_dict['mutated gene'] != ['No mention']) and
                #         (response_dict['mutated gene'] != ['no mention'])):
                #     List_Oncogenes = List_Oncogenes + response_dict['mutated gene']
            except:
                pass
        do_plt = False
        if len(List_Oncogenes)>0:
            genes, genes_num = plt_hist_genes(dir_paths, List_Oncogenes, tissue, do_plt)
            genes_index = {}
            for gene in genes:
                genes_index_single = []
                for ind in range(len(List_Oncogenes)):
                    List_Oncogene = List_Oncogenes[ind]
                    if gene == List_Oncogene:
                        genes_index_single.append(List_Oncogenes_Indexs[ind])
                genes_index[gene] = genes_index_single

            Dict_Gene_Statis[tissue] = {"genes_name": genes, "genes_num": genes_num, "genes_index": genes_index}
        else:
            uu=1
    with open(dir_paths["Dict_Gene_Statis.json"], 'w') as json_file:
        json.dump(Dict_Gene_Statis, json_file, indent=4)

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S3_3_Gene_Statis(dir_paths)