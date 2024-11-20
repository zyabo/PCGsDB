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
from scripts.call_llm import get_response, init_llm
from scripts.pathfile import parse_path
import pprint

torch.cuda.empty_cache()

def S3_2_Extract_GeneDict(dir_paths):

    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()
    list_ages = df['age'].tolist()
    list_genders = df['gender'].tolist()
    list_file_paths = df['file_path'].tolist()

    with open(dir_paths["SelectedTissue.json"], 'r') as json_file:
        SelectedTissue = json.load(json_file)

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"] , 'r') as file:
        Dict_TissueCancerNames_Full = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    with open(dir_paths["Dict_Records_GeneDict.json"] , 'r') as file:
        Dict_Records_GeneDict = json.load(file)

    with open(dir_paths["Dict_Extract_GeneText.json"], 'r') as file:
        Dict_Extract_GeneText = json.load(file)

    """
    
    """
    Dict_Extract_GeneDict = Dict_Extract_GeneText
    for index_cancer, tissue in enumerate(Dict_Extract_GeneDict):
        # tissue = SelectedTissue[index_cancer]
        Dict_TissueCancerName_Full = Dict_TissueCancerNames_Full[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]
        Index_TissueRecord_Index_num = len(List_TissueRecord_Index)
        print("*" * 100)
        print("-" * 20 + "     " + "{}:{}({})".format(index_cancer, tissue,
                                                      Index_TissueRecord_Index_num) + "     " + "-" * 20)
        print("*" * 100)

        Dict_Extract_GeneText_Tissue = Dict_Extract_GeneDict[tissue]

        start_time = time.time()

        for indice_i, key in enumerate(Dict_Extract_GeneText_Tissue):
            response_str_dict = Dict_Extract_GeneText_Tissue[key]['response']
            # response_str_dict
            # 'Patient_mutated_gene = {"mutated gene": ["No mention"]}'
            #

            try:
                if isinstance(response_str_dict, list):
                    response_str_dict_tmp = re.search(r'\{([^}]*)\}', response_str_dict[0].replace("\n  ","")).group(0)
                    dict_content = re.search(r'\{([^}]*)\}', response_str_dict_tmp).group(0)
                    dict_content = dict_content.replace("The patient\'s mutated gene","mutated gene")
                else:
                    dict_content = re.search(r'\{([^}]*)\}', response_str_dict).group(0)

                response_dict = eval(dict_content)

                mutated_gene = response_dict['mutated gene']

                # response_dict_new = {}
                if len(mutated_gene) == 1 and (
                        "no mention" in mutated_gene[0].lower() or
                        "no mutation found" in mutated_gene[0].lower() or
                        "no mutations detected" in mutated_gene[0].lower() or
                        "none mentioned" in mutated_gene[0].lower() or
                        "not available" in mutated_gene[0].lower() or
                        "not mentioned" in mutated_gene[0].lower() or
                        "none detected" in mutated_gene[0].lower() or
                        "not mentioned" in mutated_gene[0].lower() or
                        "not specified" in mutated_gene[0].lower() or
                        "not tested" in mutated_gene[0].lower() or
                        "no pathogenic mutations detected" in mutated_gene[0].lower() or
                        "not applicable" in mutated_gene[0].lower() or
                        "negative" in mutated_gene[0].lower() or
                        "no mutation identified" in mutated_gene[0].lower() or
                        "no specific gene mutation mentioned" in mutated_gene[0].lower() or
                        "no specific gene mutations mentioned" in mutated_gene[0].lower() or
                        "not tested" in mutated_gene[0].lower() or
                        "not tested or mentioned" in mutated_gene[0].lower() or
                        "no mutations mentioned" in mutated_gene[0].lower() or
                        "none found" in mutated_gene[0].lower()):

                    response_dict['mutated gene'] = ["no mention"]

                else:
                    print("*"*10)
                    print(mutated_gene)
                    pass

                uu = 1
            except:
                print("=" * 20)
                # print(response_str_dict)
                # response_dict = {}
                try:
                    dict_content = re.search(r'\{([^}]*)\}', response_str_dict).group(0)
                    response_dict = eval(dict_content)
                except:
                    # print("=" * 20)
                    # print(response_str_dict)
                    response_dict = {}

            # if response_dict == {} and isinstance(response_str_dict, list):
            #     try:
            #         print("*****  " + response_str_dict)
            #         response_str_dict_data = json.loads(response_str_dict[0].replace("\n  ",""))
            #         response_dict = response_str_dict_data["This patient's gene mutation"]
            #     except:
            #         response_dict = {}

            # Clean out what is not in the medical records
            if len(response_dict)>0:
                if 'mutated gene' in response_dict.keys():
                    mutated_genes = response_dict['mutated gene']
                    mutated_genes_new = []
                    if mutated_genes != ["no mention"]:
                        for mutated_gene in mutated_genes:
                            if isinstance(mutated_gene, str):
                                if mutated_gene in list_records[int(key)]:
                                    mutated_genes_new.append(mutated_gene)
                                else:
                                    print(mutated_gene)
                                    yyy=1
                    response_dict['mutated gene']=mutated_genes_new
            Dict_Extract_GeneText_Tissue[key]['response_dict'] = response_dict

        Dict_Extract_GeneDict[tissue] = Dict_Extract_GeneText_Tissue

    with open(dir_paths["Dict_Extract_GeneDict.json"], 'w') as json_file:
        json.dump(Dict_Extract_GeneDict, json_file, indent=4)


# "response": "Patient_mutated_gene= {\"mutated gene\": [\"No mention\"]}",
# "response_dict": {
#     "mutated gene": []
# }