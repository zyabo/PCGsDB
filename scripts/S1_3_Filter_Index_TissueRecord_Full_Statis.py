"""
Statistical results
"""
import pickle
import json
import matplotlib.pyplot as plt
import pandas as pd
import os

def S1_3_Filter_Index_TissueRecord_Full_Statis(dir_paths):

    #1. Read the medical records of all cases
    df = pd.read_csv(dir_paths["PMC-Patients.csv"] )
    list_records = df['patient'].tolist()

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"], 'r') as file:
        Dict_Index_TissueRecord_Full = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord.json"], 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    # For each major type of tissue cancer, list the sub-diseases involved in each medical record
    for index_cancer, tissue in enumerate(Dict_Index_TissueRecord_Full):
        # print("-----  {}  -----".format(tissue))
        List_Index_TissueRecord_Full = Dict_Index_TissueRecord_Full[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]

        mutation_n = 0
        for index_T in List_TissueRecord_Index:
            record = list_records[index_T].lower()
            if "mutation" in record and "gene" in record:
                mutation_n = mutation_n + 1
        try:
            print("{}: {}/{}={:.1f}%".format(tissue, mutation_n,len(List_TissueRecord_Index), 100*mutation_n/len(List_TissueRecord_Index)))
        except:
            print("{}: {}/{}".format(tissue, mutation_n, len(List_TissueRecord_Index)))

        # print("*"*20)

        for l1 in range(len(List_Index_TissueRecord_Full)):
            List_CancerName_Full_s = List_Index_TissueRecord_Full[l1]
            indexs = List_CancerName_Full_s["index"]
            for index_s in indexs:
                index_selected = List_TissueRecord_Index.index(index_s)
                Subdisease = []
                Subdisease = List_TissueRecord_Subdisease[index_selected]
                Subdisease.append(List_CancerName_Full_s["name"])
                List_TissueRecord_Subdisease[index_selected] = Subdisease
        Dict_Index_TissueRecord[tissue] = {"index": List_TissueRecord_Index,
                                           "subdisease": List_TissueRecord_Subdisease}
    #
    with open(dir_paths["Dict_Index_TissueRecord.json"], 'w') as f:
        json.dump(Dict_Index_TissueRecord, f, indent=4)


    #
    for index_cancer, tissue in enumerate(Dict_Index_TissueRecord_Full):
        print("{} {}".format(index_cancer, tissue))
        List_Index_TissueRecord_Full = Dict_Index_TissueRecord_Full[tissue]
        names, nums = [], []
        for l1 in range(len(List_Index_TissueRecord_Full)):
            List_CancerName_Full_s = List_Index_TissueRecord_Full[l1]
            names.append(List_CancerName_Full_s["name"])
            nums.append(List_CancerName_Full_s["num"])
            # index = List_CancerName_Full_s["index"]

        fig, ax = plt.subplots(figsize=(12, 22))
        bars = ax.barh(names, nums)
        ax.set_title('Histogram of Values')
        ax.set_xlabel('Number of cases')
        ax.set_ylabel('sub-disease ')
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width}', ha='left', va='center')
        # plt.xticks(rotation=90, fontsize=14)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        # plt.show()

        title_str = "Statistics on the number of sub-cancers in the tissue"
        plt.title(title_str + "({}  {})".format(tissue.replace('/', '_'), len(Dict_Index_TissueRecord[tissue]['subdisease'])))

        fig_filepath = os.path.join(dir_paths["current_dir_path"],"results","figs",title_str + "({})".format(tissue.replace('/', '_')) + '.png')

        plt.savefig(fig_filepath, dpi=600)
        plt.close()

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    S1_3_Filter_Index_TissueRecord_Full_Statis(dir_paths)
