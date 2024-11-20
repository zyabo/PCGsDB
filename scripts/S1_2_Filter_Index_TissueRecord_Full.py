
import json
import pandas as pd
import pickle

def S1_2_Filter_Index_TissueRecord_Full(dir_paths):
    """
    In the medical records, all medical records with keywords index
    """
    with open(dir_paths["List_RecordsCancer_Index.pkl"], 'rb') as file:
        List_RecordsCancer_Index = pickle.load(file)

    # 1.读取所有病例的病历
    df = pd.read_csv(dir_paths["PMC-Patients.csv"] )
    list_records = df['patient'].tolist()

    # 2.Dict_CancerNames
    with open(dir_paths["Dict_TissueCancerNames_Full.json"], 'r') as file:
        Dict_TissueCancerNames_Full = json.load(file)

    # 3.每一种癌症，列出所有的index
    num_c = 0
    for index_cancer, tissue in enumerate(Dict_TissueCancerNames_Full):
        print("{} {}".format(index_cancer, tissue))
        List_CancerNames = Dict_TissueCancerNames_Full[tissue]
        List_Index_TissueRecord = []
        for index, record in enumerate(list_records):
            if index not in List_RecordsCancer_Index:
                continue
            record = record.lower()

            Find_io = False

            for l1 in range(len(List_CancerNames)):
                List_CancerName = List_CancerNames[l1]

                if List_CancerName["name"] in record:
                    List_CancerName["num"] = List_CancerName["num"] + 1
                    index_single = []
                    index_single = List_CancerName["index"]
                    if index_single is None:
                        index_single = []
                    index_single.append(index)
                    List_CancerName["index"] = index_single
                    Find_io = True
                    List_CancerNames[l1] = List_CancerName
        Dict_TissueCancerNames_Full[tissue] = List_CancerNames

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"] , 'w') as f:
        json.dump(Dict_TissueCancerNames_Full, f, indent=4)

