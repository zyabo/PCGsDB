import json
import pandas as pd
import pickle
import os


def read_data(dir_paths):
    data = {}
    df_PMC_Patients = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df_PMC_Patients['patient'].tolist()
    data["df_PMC_Patients"] = df_PMC_Patients
    data["list_records"] =list_records

    # 2.Dict_CancerNames 共32个
    with open(dir_paths["Dict_TissueCancerNames_Added.json"], 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    for key in Dict_TissueCancerNames:
        List_TissueCancerNames = Dict_TissueCancerNames[key]
        Dict_TissueCancerNames[key] = [item.lower() for item in List_TissueCancerNames]

    with open(dir_paths["Dict_TissueCancerNames_Added.json"], 'w') as json_file:
        json.dump(Dict_TissueCancerNames, json_file, indent=4)

    data["Dict_TissueCancerNames"] =Dict_TissueCancerNames


    """
    In the medical records, all medical records with keywords index
    """
    with open(dir_paths["List_RecordsCancer_Index.pkl"], 'rb') as file:
        List_RecordsCancer_Index = pickle.load(file)

    data["List_RecordsCancer_Index"] =List_RecordsCancer_Index

    return data