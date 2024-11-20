import json
import pandas as pd
import pickle
import os

def S0_3_CancerList_Full(dir_paths):
    with open(dir_paths["Dict_TissueCancerNames_Added.json"] , 'r') as file:
        Dict_TissueCancerNames = json.load(file)
    len_n = 0
    Dict_TissueCancerNames_Full = {}
    for key in Dict_TissueCancerNames:
        List_TissueCancerNames = Dict_TissueCancerNames[key]
        single_dict = []
        for s in List_TissueCancerNames:
            single_dict.append({"name": s.lower(), "num": 0, "index": []})
        Dict_TissueCancerNames_Full[key] = single_dict
        print(len(single_dict))
        len_n = len_n + len(single_dict)
    with open(dir_paths["Dict_TissueCancerNames_Full.json"] , 'w') as f:
        json.dump(Dict_TissueCancerNames_Full, f, indent=4)
    print(len_n)
# if __name__ == "__main__":
#     current_dir_path = os.path.dirname(os.getcwd())
#     S0_3_CancerList_Full(current_dir_path)
