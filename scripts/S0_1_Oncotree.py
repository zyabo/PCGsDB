import requests
import json
import os
def fetch_tumor_types():
    # URL to the Oncotree API endpoint
    url = "http://oncotree.mskcc.org/api/tumorTypes"
    # Specify the version parameter
    params = {
        'version': 'oncotree_latest_stable'
    }

    # Send a GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        tumor_types = response.json()
        return tumor_types
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def get_OncotreeDict():
    # Fetch and store tumor types
    tumor_types_dict = fetch_tumor_types()
    print(tumor_types_dict)
    return tumor_types_dict

def save_OncotreeDict(filename):
    tumor_types_dict = get_OncotreeDict()
    # 写入JSON数据到文件
    with open(filename, 'w') as f:
        json.dump(tumor_types_dict, f, indent=4)
    return tumor_types_dict

def read_OncotreeDict(filename):
    with open(filename, 'r') as file:
        tumor_types_dict = json.load(file)
    return tumor_types_dict


def S0_1_Oncotree(dir_paths):
    # tumor_types_dict = save_OncotreeDict(filename)

    tumor_types_dict = read_OncotreeDict(dir_paths["OncotreeDict.json"])

    # Extracting names of tumor types where level is 2
    level_1_names = [tumor['name'] for tumor in tumor_types_dict if tumor['level'] == 1]

    print("\n*S0_1_Oncotree\n    Oncotree's first-level organization name: \n    "+str(level_1_names))
    uu=1
    return tumor_types_dict, level_1_names
if __name__ == "__main__":
    from get_dir_paths import get_dir_paths
    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)
    S0_1_Oncotree(current_dir_path)



