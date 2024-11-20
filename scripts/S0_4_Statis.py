import json
import pandas as pd
import pickle
import os

"""
pip install git+https://github.com/Anth-us/openai_cost_calculator.git@main
"""

def count_words(text):
    # 分割字符串
    words = text.split()
    # 返回单词数量
    return len(words)
def S0_4_Statis(dir_paths):
    print("\n*S0_4_Statis")
    df = pd.read_csv(dir_paths["PMC-Patients.csv"] )
    list_records = df['patient'].tolist()

    # 2.Dict_CancerNames
    with open(dir_paths["Dict_TissueCancerNames_Added.json"], 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    List_TissueCancerNames_All = []
    for key in Dict_TissueCancerNames:
        List_TissueCancerNames_All = List_TissueCancerNames_All + Dict_TissueCancerNames[key]

    """
    In the medical records, all medical records with keywords index
    """
    records_cancer_num = 0
    List_Cancer_KeyWords = ["cancer", "tumor", "malignant", "carcinoma", "oncology", "metastasis", "chemotherapy",
                            "radiation therapy", "lymphoma", "leukemia", "sarcoma", "neoplasm", "adenocarcinoma",
                            "melanoma", "glioma", "metastatic", "immunotherapy"]

    List_Cancer_KeyWords = List_Cancer_KeyWords + List_TissueCancerNames_All
    List_Cancer_KeyWords_lower = [item.lower() for item in List_Cancer_KeyWords]

    List_RecordsCancer_Index = []
    list_records_n = len(list_records)

    word_count_all = 0
    for index, record in enumerate(list_records):
        print("    {}/{}".format(index, list_records_n))
        record = record.lower()
        word_count = count_words(record)
        word_count_all = word_count_all + word_count

        for List_CancerName in List_Cancer_KeyWords_lower:
            if List_CancerName.lower() in record:
                records_cancer_num = records_cancer_num + 1
                List_RecordsCancer_Index.append(index)
                break
    print("    The number of cases with cancer:{}".format(len(List_RecordsCancer_Index)))  # 68139
    print(word_count_all)
    # Open a new file and save the list to that file using pickle
    with open(dir_paths["List_RecordsCancer_Index.pkl"], 'wb') as f:
        pickle.dump(List_RecordsCancer_Index, f)

if __name__ == "__main__":
    from get_dir_paths import get_dir_paths

    # current_dir_path = os.path.dirname(os.getcwd())
    current_dir_path = r"D:\Codes\GeneExplorer"

    dir_paths = get_dir_paths(current_dir_path)

    S0_4_Statis(dir_paths)
