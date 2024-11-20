import json
import os

def read_OncotreeDict(filename):
    with open(filename, 'r') as file:
        tumor_types_dict = json.load(file)
    return tumor_types_dict


def find_cancer_by_tissue(tumor_types_dict, parent_name):
    result = []
    for tumor_list in tumor_types_dict:
        if tumor_list['tissue'] == parent_name and  tumor_list['level']>1:
            result.append(tumor_list)
    return result

def S0_2_CancerList(dir_paths):

    tumor_types_dict = read_OncotreeDict(dir_paths["OncotreeDict.json"])

    level_1_names = [tumor['name'] for tumor in tumor_types_dict if tumor['level'] == 1]

    Dict_TissueCancerNames = {}

    CancerNameList_n = 0

    for level_1_name in level_1_names:
        CancerNameList = []
        if level_1_name != "Other":
            """
            level_1 Cancer Name
            """
            if '/' in level_1_name:
                list_level_1_names = level_1_name.split('/')
            else:
                list_level_1_names = [level_1_name]

            for list_level_1_name in list_level_1_names:
                CancerNameList = CancerNameList + [list_level_1_name.lower() + " cancer",
                                                   list_level_1_name.lower() + " carcinoma",
                                                   list_level_1_name.lower() + " tumor"]
            # print(CancerNameList)

        """
        
        """
        list_tissue_cancers = find_cancer_by_tissue(tumor_types_dict, level_1_name)
        for list_tissue_cancer in list_tissue_cancers:
            CancerNameList = CancerNameList + [list_tissue_cancer["name"].lower()]
        """
        
        """

        Dict_TissueCancerNames[level_1_name] = CancerNameList
        CancerNameList_n = CancerNameList_n + len(CancerNameList)
    with open(dir_paths["Dict_TissueCancerNames.json"], 'w') as f:
        json.dump(Dict_TissueCancerNames, f, indent=4)
    print(CancerNameList_n)

# if __name__ == "__main__":
#     current_dir_path = os.path.dirname(os.getcwd())
#     S0_2_CancerList(current_dir_path)

