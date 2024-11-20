"""
, model_name
[model_name]

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
from scripts.call_llm import get_response, init_llm
from scripts.pathfile import parse_path

torch.cuda.empty_cache()

def S2_2_Filter_Gene_Extract(dir_paths):
    """
    2. Read the medical records of all cases and save them in list_records
    """
    df = pd.read_csv(dir_paths["PMC-Patients.csv"] )
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

    with open(dir_paths["Dict_Records_Gene.json"], 'r') as json_file:
        Dict_Records_Gene = json.load(json_file)

    with open(dir_paths["Dict_Records_Gene_prompts.json"], 'r') as json_file:
        Dict_Records_Gene_prompts = json.load(json_file)

    with open(dir_paths["Dict_Records_GeneText.json"], 'r') as json_file:
        Dict_Records_GeneText = json.load(json_file)

    with open(dir_paths["Dict_Records_GeneText_prompts.json"], 'r') as json_file:
        Dict_Records_GeneText_prompts = json.load(json_file)

    # for index_cancer, tissue in enumerate(Dict_TissueCancerNames_Full):
    #     if tissue not in SelectedTissue:
    #         continue

    for index_cancer, tissue in enumerate(Dict_Records_Gene):

        # tissue = SelectedTissue[index_cancer]
        Dict_TissueCancerName_Full = Dict_TissueCancerNames_Full[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]
        Index_TissueRecord_Index_num = len(List_TissueRecord_Index)
        print("*" * 100)
        print("-" * 20 + "     " + "{}:{}({})".format(index_cancer, tissue,
                                                      Index_TissueRecord_Index_num) + "     " + "-" * 20)

        Dict_Record_Gene = Dict_Records_Gene[tissue]
        Dict_Record_Gene_prompts = Dict_Records_Gene_prompts[tissue]
        Dict_Record_GeneText = Dict_Records_GeneText[tissue]
        Dict_Record_GeneText_prompts = Dict_Records_GeneText_prompts[tissue]

        yes_no_unknown_n = [0, 0, 0]
        yes_no_unknown_Biomarker_n = [0, 0, 0]
        # for index_s in range(len(list_Records_Gene)):


        for index, index_s in enumerate(Dict_Record_Gene):

            Dict_Record_Gene_single = Dict_Record_Gene[index_s]
            Dict_Record_Gene_prompts_single = Dict_Record_Gene_prompts[index]
            Dict_Record_GeneText_single = Dict_Record_GeneText[index]
            Dict_Record_GeneText_prompts_single = Dict_Record_GeneText_prompts[index]

            HasGene_right = ""
            Indix_right = 0
            for key in Dict_Record_Gene_single:
                # if key.lower() == "is there a genetic test or gene-related biomarker in the medical record?":
                if "is there genetic testing" in key.lower():
                    try:
                        HasGene = Dict_Record_Gene_single[key]
                        if isinstance(HasGene, list):
                            HasGene = HasGene[0]

                        if HasGene.lower() == "yes":
                            HasGene_right = "yes"
                            yes_no_unknown_n[0] = yes_no_unknown_n[0] + 1
                        elif HasGene.lower() == "no":
                            HasGene_right = "no"
                            yes_no_unknown_n[1] = yes_no_unknown_n[1] + 1
                        elif HasGene.lower() == "unknown":
                            HasGene_right = "unknown"
                            yes_no_unknown_n[2] = yes_no_unknown_n[2] + 1
                        else:
                            pass
                    except:
                        sss=1
                elif "is there gene-related biomarker" in key.lower():
                    try:
                        HasGene = Dict_Record_Gene_single[key]
                        if isinstance(HasGene, list):
                            HasGene = HasGene[0]

                        if HasGene.lower() == "yes":
                            HasGeneBiomarker_right = "yes"
                            yes_no_unknown_Biomarker_n[0] = yes_no_unknown_Biomarker_n[0] + 1
                        elif HasGene.lower() == "no":
                            HasGeneBiomarker_right = "no"
                            yes_no_unknown_Biomarker_n[1] = yes_no_unknown_Biomarker_n[1] + 1
                        elif HasGene.lower() == "unknown":
                            HasGeneBiomarker_right = "unknown"
                            yes_no_unknown_Biomarker_n[2] = yes_no_unknown_Biomarker_n[2] + 1
                        else:
                            pass
                    except:
                        sss=1
                elif key.lower() == 'index':
                    Indix_right = Dict_Record_Gene_single[key]
                else:
                    pass

            Dict_Record_Gene[index_s] = {"Has genetic testing?": HasGene_right,
                                         "Has gene-related biomarker?": HasGeneBiomarker_right,
                                         "GeneText": Dict_Record_GeneText_single,
                                         "GeneText_prompts": Dict_Record_GeneText_prompts_single,
                                         "Gene_prompts": Dict_Record_Gene_prompts_single,
                                         "Index": Indix_right}

        print("Gene: Y({}) + N({}) + U({}) = {} / {}".format(yes_no_unknown_n[0], yes_no_unknown_n[1], yes_no_unknown_n[2],
                                                             sum(yes_no_unknown_n), len(Dict_Record_Gene)))

        print("Gene Biomarker: Y({}) + N({}) + U({}) = {} / {}".format(yes_no_unknown_Biomarker_n[0],
                                                                       yes_no_unknown_Biomarker_n[1],
                                                                       yes_no_unknown_Biomarker_n[2],
                                                                       sum(yes_no_unknown_Biomarker_n),
                                                                       len(Dict_Record_Gene)))

        print("*" * 100)

        Dict_Records_Gene[tissue] = Dict_Record_Gene

        with open(dir_paths["Dict_Records_GeneDict.json"], 'w') as json_file:
            json.dump(Dict_Records_Gene, json_file, indent=4)
