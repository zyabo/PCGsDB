"""
1. Cancer
2. Oncogenes
3. Read cases
4. Retrieve cases of different cancers
5. Screen out cases with gene mutations
"""
import json
import pandas as pd
import pickle
import os

def S1_1_Filter_Index_TissueRecord(dir_paths):
    # 1. Read the medical records of all cases
    df = pd.read_csv(dir_paths["PMC-Patients.csv"] )
    list_records = df['patient'].tolist()

    # 2.Dict_CancerNames
    with open(dir_paths["Dict_TissueCancerNames_Added.json"] , 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    for key in Dict_TissueCancerNames:
        List_TissueCancerNames = Dict_TissueCancerNames[key]
        Dict_TissueCancerNames[key] = [item.lower() for item in List_TissueCancerNames]

    with open(dir_paths["Dict_TissueCancerNames_Added.json"] , 'w') as json_file:
        json.dump(Dict_TissueCancerNames, json_file, indent=4)

    """
    In the medical records, all medical records with keywords index
    """
    with open(dir_paths["List_RecordsCancer_Index.pkl"] , 'rb') as file:
        List_RecordsCancer_Index = pickle.load(file)

    """
    # 3.For each type of cancer, list all the indexes
    """
    num_c = 0
    num_k = 0
    Dict_Index_TissueRecord = {}
    for index_cancer, tissue in enumerate(Dict_TissueCancerNames):

        List_CancerNames = Dict_TissueCancerNames[tissue]
        List_Index_TissueRecord = []
        for index, record in enumerate(list_records):
            if index not in List_RecordsCancer_Index:
                continue

            # print(f"Index: {index}, Item: {record}")
            record = record.lower()

            Find_io = False
            for List_CancerName in List_CancerNames:
                if List_CancerName in record:
                    List_Index_TissueRecord.append(index)
                    Find_io = True
                    break

            # if not Find_io:
            #     if tissue.lower() in record and tissue != "Other":
            #         List_Index_TissueRecord.append(index)

        Dict_Index_TissueRecord[tissue] = {"index": List_Index_TissueRecord,
                                           "subdisease": [[]] * len(List_Index_TissueRecord)}

        print("    {}/{} | Num:{} | {} |  {}".format(index_cancer, len(Dict_TissueCancerNames), len(List_Index_TissueRecord), len(List_CancerNames), tissue))
        num_c = num_c + len(List_Index_TissueRecord)
        num_k = num_k + len(List_CancerNames)

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'w') as f:
        json.dump(Dict_Index_TissueRecord, f, indent=4)

    print(num_c)
    print(num_k)
if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S1_1_Filter_Index_TissueRecord(dir_paths)

