import os

def get_dir_paths(current_dir_path):
    dir_paths = {}
    dir_paths["current_dir_path"] = current_dir_path
    dir_paths["SelectedTissue.json"] = os.path.join(current_dir_path, "results", "data_files", "SelectedTissue.json")
    dir_paths["PMC-Patients.csv"] = os.path.join(current_dir_path, "datasets", "PMC-Patients.csv")
    dir_paths["PMC-Patients.db"] = os.path.join(current_dir_path, "datasets", "PMC-Patients.db")
    dir_paths["OncotreeDict.json"] = os.path.join(current_dir_path, "results", "data_files", "OncotreeDict.json")
    dir_paths["OncotreeDict.json"] = os.path.join(current_dir_path, "results", "data_files", "OncotreeDict.json")
    dir_paths["Dict_TissueCancerNames.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                            "Dict_TissueCancerNames.json")
    dir_paths["Dict_TissueCancerNames_Added.json"] = (
        os.path.join(current_dir_path, "results", "data_files", "Dict_TissueCancerNames_Added.json"))
    dir_paths["Dict_TissueCancerNames_Full.json"] = (
        os.path.join(current_dir_path, "results", "data_files", "Dict_TissueCancerNames_Full.json"))
    dir_paths["List_RecordsCancer_Index.pkl"] = os.path.join(current_dir_path, "results", "data_files",
                                                             "List_RecordsCancer_Index.pkl")
    dir_paths["Dict_Index_TissueRecord.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                             "Dict_Index_TissueRecord.json")
    dir_paths["Dict_Records_Gene.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                       "Dict_Records_Gene.json")
    dir_paths["Dict_Index_TissueRecord_Full.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                                  "Dict_Index_TissueRecord_Full.json")
    dir_paths["Dict_Records_Gene_prompts.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                               "Dict_Records_Gene_prompts.json")
    dir_paths["Dict_Records_GeneText.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                           "Dict_Records_GeneText.json")
    dir_paths["Dict_Records_GeneText_prompts.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                                   "Dict_Records_GeneText_prompts.json")
    dir_paths["Dict_Records_GeneDict.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                           "Dict_Records_GeneDict.json")
    dir_paths["Dict_Extract_GeneText.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                           "Dict_Extract_GeneText.json")
    dir_paths["Dict_Extract_GeneDict.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                           "Dict_Extract_GeneDict.json")
    dir_paths["Dict_Gene_Statis.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                      "Dict_Gene_Statis.json")
    dir_paths["Dict_Records_Gene_kw_indice.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                      "Dict_Records_Gene_kw_indice.json")

    dir_paths["Dict_Gene_Val.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                      "Dict_Gene_Val.json")

    dir_paths["Dict_Gene_Level.json"] = os.path.join(current_dir_path, "results", "data_files", "Dict_Gene_Level.json")
    dir_paths["Dict_Gene_Statis_Rename.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                             "Dict_Gene_Statis_Rename.json")
    dir_paths["disgenet_2020.db"] = os.path.join(current_dir_path, "datasets", "disgenet_2020.db")

    dir_paths["Census_abbreviations.csv"] = os.path.join(current_dir_path, "datasets", "Census_abbreviations.csv")

    dir_paths["Census_allTue May 14 09_10_51 2024.csv"] = os.path.join(current_dir_path, "datasets",
                                                                       "Census_allTue May 14 09_10_51 2024.csv")

    dir_paths["Dict_Gene_Score.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                     "Dict_Gene_Score.json")

    dir_paths["List_Score_results.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                        "List_Score_results.json")

    dir_paths["Dict_CandidateGene_DisGeNET.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                                 "Dict_CandidateGene_DisGeNET.json")

    dir_paths["Dict_CandidateGene.json"] = os.path.join(current_dir_path, "results", "data_files",
                                                        "Dict_CandidateGene.json")
    dir_paths["results_dir"] = os.path.join(current_dir_path, "datasets", "results")

    return dir_paths