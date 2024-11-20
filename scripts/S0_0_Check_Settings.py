import json
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import statistics
import os

def count_words_in_list(strings_list):
    total_words = 0
    list_count_words = [0] * len(strings_list)
    for s1 in range(len(strings_list)):
        string = strings_list[s1]
        words = string.split()  # 将字符串按空格分割成单词列表
        list_count_words[s1] = len(words)
    return list_count_words

def calculate_mean_and_variance(data):
    mean = statistics.mean(data)
    variance = statistics.variance(data)
    return mean, variance


def check_medical_records(dir_paths):
    """
    1.Read medical records for all cases
    """
    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()

    # Count the total number of words
    list_count_words = count_words_in_list(list_records)
    mean, variance = calculate_mean_and_variance(list_count_words)
    total_word_count = sum(list_count_words)
    print("\n*S0_0_Statis_Settings")
    print(
        f"    Total number of words: {total_word_count}  Average words: {round((total_word_count / len(list_records)), 1)}   {mean:.1f}±{variance:.1f} ")

    # Plotting a Histogram
    plt.hist(list_count_words, bins=range(0, 1000, 100), edgecolor='black', alpha=0.7)
    plt.title('Distribution of Numbers')
    plt.xlabel('Number')
    plt.ylabel('Frequency')
    # plt.show()
    title_str = "S0_0_Statis_Settings(Distribution of Numbers)"
    S0_0_Statis_Settings_fig_filepath = os.path.join(dir_paths["current_dir_path"],"results","figs",title_str + '.png')
    plt.savefig(S0_0_Statis_Settings_fig_filepath, dpi=600)
    plt.close()

    # Find the maximum value
    max_value = max(list_count_words)
    # Get the first index of the maximum value
    max_index = list_count_words.index(max_value)
    # list_records[max_index]

def S0_0_Check_Settings(dir_paths):
    check_medical_records(dir_paths)

    """
    """
    records_cancer_num = 0
    List_Cancer_KeyWords = ["cancer", "tumor", "malignant", "carcinoma", "oncology", "metastasis", "chemotherapy",
                            "radiation therapy", "lymphoma", "leukemia", "sarcoma", "neoplasm", "adenocarcinoma",
                            "melanoma", "glioma", "metastatic", "immunotherapy"]
    List_RecordsCancer_Index = []
    num_0 = 0
    num_1 = 0
    for index, record in enumerate(list_records):
        record = record.lower()
        Find_io = False
        for List_CancerName in List_Cancer_KeyWords:
            if List_CancerName in record:
                records_cancer_num = records_cancer_num + 1
                List_RecordsCancer_Index.append(index)
                Find_io = True
                break
        if Find_io:
            if ("mutation" in record or "mutations" in record) and ("gene" in record or "genes" in record):
                num_0 = num_0 + 1
            if "mutation" in record or "mutations" in record:
                num_1 = num_1 + 1

    """
    1. "mutation"  
    """
    records_mutation_num = 0
    for index, record in enumerate(list_records):
        record = record.lower()
        if "mutation" in record:
            records_mutation_num = records_mutation_num + 1
    print("    {} records contain the word 'mutation'".format(records_mutation_num))

    uu = 1

    """
    1."pancreatic cancer"  
    2."pancreatic cancer" & "gene"
    """
    # records_cancer_num = 0
    # records_cancer_num_gene = 0
    # List_RecordsCancer_Index = []
    # for index, record in enumerate(list_records):
    #     record = record.lower()
    #     if "pancreatic cancer" in record:
    #         records_cancer_num = records_cancer_num + 1
    #         List_RecordsCancer_Index.append(index)
    #         if "gene" in record:
    #             records_cancer_num_gene = records_cancer_num_gene + 1
    # print("    pancreatic cancer  :{}".format(records_cancer_num))
    # print("    pancreatic cancer  & gene :{}".format(records_cancer_num_gene))



    # Selected human tissues
    # SelectedTissue = ["Breast", "Myeloid", "Lung", "Skin", "Bowel", "Soft Tissue", "CNS/Brain", "Lymphoid"]
    # SelectedTissue = {"Breast": {"COSMIC": "Breast"},
    #                   "Lung": {"COSMIC": "Lung"},
    #                   "Skin": {"COSMIC": "Skin"},
    #                   "Liver": {"COSMIC": "Liver"},
    #                   "Soft Tissue": {"COSMIC": "Soft tissue"},
    #                   "Thyroid": {"COSMIC": "Thyroid"},
    #                   "Adrenal Gland": {"COSMIC": "Adrenal gland"}}

    SelectedTissue = {"Breast": {"COSMIC": "Breast"},
                      "Lung": {"COSMIC": "Lung"},
                      "Skin": {"COSMIC": "Skin"},
                      "Soft Tissue": {"COSMIC": "Soft tissue"}}

    with open(dir_paths["SelectedTissue.json"], 'w') as json_file:
        json.dump(SelectedTissue, json_file)


# if __name__ == "__main__":
#     import os
#     current_dir_path = os.path.dirname(os.getcwd())
#     S0_0_Statis_Settings(dir_paths)