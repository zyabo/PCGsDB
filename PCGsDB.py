import os
from scripts.get_dir_paths import get_dir_paths
from scripts.S0_0_Check_Settings import S0_0_Check_Settings
from scripts.S0_1_Oncotree import S0_1_Oncotree
from scripts.S0_2_CancerList import S0_2_CancerList
from scripts.S0_3_CancerList_Full import S0_3_CancerList_Full
from scripts.S0_4_Statis import S0_4_Statis
from scripts.S1_1_Filter_Index_TissueRecord import S1_1_Filter_Index_TissueRecord
from scripts.S1_2_Filter_Index_TissueRecord_Full import S1_2_Filter_Index_TissueRecord_Full
from scripts.S1_3_Filter_Index_TissueRecord_Full_Statis import S1_3_Filter_Index_TissueRecord_Full_Statis

from scripts.S2_0_Filter_Gene_Keywords import S2_0_Filter_Gene_Keywords
from scripts.S2_1_Filter_Gene import S2_1_Filter_Gene
from scripts.S2_2_Filter_Gene_Extract import S2_2_Filter_Gene_Extract
from scripts.S3_1_Extract_GeneText import S3_1_Extract_GeneText
from scripts.S3_2_Extract_GeneDict import S3_2_Extract_GeneDict
from scripts.S3_3_Gene_Statis import S3_3_Gene_Statis
from scripts.S3_4_Gene_Rename import S3_4_Gene_Rename
from scripts.S4_1_Score_DisGeNET import S4_1_Score_DisGeNET
from scripts.S4_2_Score_CGC import S4_2_Score_CGC
from scripts.S4_3_Score_Level import S4_3_Score_Level

from scripts.S5_1_Val_Web import S5_1_Val_Web
from scripts.S5_2_Val_Text import S5_2_Val_Text
from scripts.S5_3_Val import S5_3_Val

# from scripts.S5_1_Score_LLM import S5_1_Score_LLM
from scripts.call_llm import get_response_gpt
from Modules.pmc_DB import pmc_csv2DB, pmc_searchDB, check_DB
from Modules.read_data import read_data
import re
import json

def Initial_Settings(dir_paths, do_Initial_Settings):
    if not do_Initial_Settings:
        if (not os.path.exists(dir_paths["List_RecordsCancer_Index.pkl"]) or
                not os.path.exists(dir_paths["Dict_TissueCancerNames_Added.json"]) or
                not os.path.exists(dir_paths["Dict_TissueCancerNames_Full.json"]) or
                not os.path.exists(dir_paths["Dict_TissueCancerNames_Added.json"])):
            do_Initial_Settings = True

    if do_Initial_Settings:
        S0_0_Check_Settings(dir_paths)
        S0_1_Oncotree(dir_paths)
        S0_2_CancerList(dir_paths)
        S0_3_CancerList_Full(dir_paths)
        S0_4_Statis(dir_paths)

current_dir_path = os.getcwd()
dir_paths = get_dir_paths(current_dir_path)

do_Initial_Settings = False
Initial_Settings(dir_paths, do_Initial_Settings)
tumor_types_dict, level_1_names = S0_1_Oncotree(dir_paths)

data = read_data(dir_paths)

"""
一、关键词快速过滤（1.1）
1.按照 病症 名称，筛选出病症 的Index
"""

if False:
    # 1.按照 病症 名称，筛选出病症 的Index
    S1_1_Filter_Index_TissueRecord(dir_paths)

    with open(dir_paths["Dict_TissueCancerNames.json"], 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    # 遍历字典，并打印每个键对应值的个数
    for key, value in Dict_Index_TissueRecord.items():
        print(f"The key '{key}' has {len(value['index'])} elements.")
        print(len(Dict_TissueCancerNames[key]))

with open(dir_paths["Dict_TissueCancerNames.json"], 'r') as file:
    Dict_TissueCancerNames = json.load(file)
Dict_TissueCancerNames_n = 0
for key in Dict_TissueCancerNames:
    List_TissueCancerNames = Dict_TissueCancerNames[key]
    Dict_TissueCancerNames_n = Dict_TissueCancerNames_n + len(List_TissueCancerNames)

uu=1


"""
二、信息判断（2.1、2.2）
2.筛选出有基因的 Index
	1. 直接LLM
	2. Chain-of-Thoughts
	3. Thinking Fast and Slow
	4. Critical Thinking
	5. Iceberg Mental Model
	6. Second Order Thinking
只要有，那么，就进入
"""

# S2_0_Filter_Gene_Keywords(dir_paths)

# model_type = "api"
# # ollama run llama3.1:8b
# model_names = ["chain-of-thoughts.q5",  "thinking-fast-n-slow.q5",  "critical-thinking.q5",  "iceberg-mental-model.q5", "second-order-thinking.q5"]
# for model_name in model_names:
#     S2_1_Filter_Gene(dir_paths, model_type, model_name)

# S4_3_Score_Level(dir_paths)
#
# S5_1_Val_Web(dir_paths)
S5_2_Val_Text(dir_paths)
uu=1


# 修改：S2_2_Filter_Gene_Extract 为 通过 NuExtract-1.5，提取规则化

# S2_2_Filter_Gene_Extract(dir_paths)

# S3_1_Extract_GeneText(dir_paths)
# S3_2_Extract_GeneDict(dir_paths)

# S3_3_Gene_Statis(dir_paths)
# S3_4_Gene_Rename(dir_paths)

# with open(dir_paths["Dict_Gene_Statis.json"], 'r') as file:
#     Dict_Gene_Statis = json.load(file)

# S4_1_Score_DisGeNET(dir_paths)
# S4_2_Score_CGC(dir_paths)

# model_type = "api"
# model_name = "chain-of-thoughts.q5"
# S4_3_Score_LLM(dir_paths,model_type,model_name)

# S4_3_Score_Filter(dir_paths)

# 用于排除：
# S5_1_Score_LLM(dir_paths)
S5_2_Val_Text(dir_paths)
uu=1


