"""
Determine whether there is a gene mutation and all gene mutations
"""

import json
import pandas as pd
import ollama
import re
import time
import pickle
import os
import pandas as pd
import re
import time
import pickle
import json
import os
import ast
from transformers import AutoTokenizer
import transformers
import torch
try:
    from scripts.call_llm import get_response, init_llm
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm
    from pathfile import parse_path
torch.cuda.empty_cache()
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cuda"


def get_prompt_text(record, age, gender):
    prompt_str = """
Based on the medical records of patients ({}, {}), answer the following questions:

**Question A: If genetic testing is mentioned in the medical record, please list complete sentences referring to genetic testing. **
Answer:
* xxx

**[Question B: If gene-related biomarkers are mentioned in the medical record, please list complete sentences referring to the gene-related biomarkers. **
Answer:
* xxx


The following is the patient's medical record:
{} 
""".format(gender, age, record)

    #     prompt_str = prompt_str + """
    # """
    return prompt_str


def get_prompt(record):
    prompt_str = """
Please fill in the dict in python format below based on the content of genetic testing and gene-related biomarkers in the patient medical record description below (2 questions).
Patient_medical_gene_record = {"is there genetic testing?": "yes, no, or unknown", 
"is there gene-related biomarker?": "yes, no, or unknown"}
"""

    prompt_str = prompt_str + """
The patient medical record describes the following:
{} 

""".format(record)

    return prompt_str



def S2_0_Filter_Gene_Keywords(dir_paths):

    """
    2. Read the medical records of all cases and save them in list_records
    """
    df = pd.read_csv(dir_paths["PMC-Patients.csv"])
    list_records = df['patient'].tolist()
    list_ages = df['age'].tolist()
    list_genders = df['gender'].tolist()
    list_file_paths = df['file_path'].tolist()

    Keywords_lower = ['Sequence Motif Analysis','Frameshift Peptide','Chromatin Immunoprecipitation','Locus Control Region','Positional Cloning','Transcriptome','Chromosomal Aberration','Quantitative Trait Loci','Genetic','Chromatin Remodeling','Recombinant DNA Technology','Mosaicism','Post-transcriptional Regulation','Transcriptional Regulation','Genomics','Biomarker','Transgenic','Toxicogenomics','Phenotypic','Metagenomics','Resequencing','Assimilation','Mutation','cGene', 'Allele', 'Genotype', 'Phenotype', 'Deoxyribonucleic Acid', 'Chromosome',
                      'Nucleotide', 'Point Mutation', 'Insertion', 'Deletion', 'Frameshift Mutation',
                      'Missense Mutation', 'Nonsense Mutation', 'Silent Mutation', 'Substitution',
                      'Genomic Instability', 'Mutagen', 'Carcinogen', 'Polymorphism', 'Translocation', 'Inversion',
                      'Duplication', 'Somatic Mutation', 'Germline Mutation', 'Spontaneous Mutation',
                      'Induced Mutation', 'Genetic Drift', 'Genetic Diversity', 'Founder Effect', 'Bottleneck Effect',
                      'Selective Pressure', 'Adaptive Mutation', 'Recessive Mutation', 'Dominant Mutation',
                      'Loss of Function Mutation', 'Gain of Function Mutation', 'Penetrance', 'Expressivity',
                      'aplotype', 'Genetic Testing', 'Genomic Sequencing', 'DNA Profiling', 'Carrier Screening',
                      'Prenatal Testing', 'Newborn Screening', 'Pharmacogenomics', 'Gene Therapy',
                      'Molecular Diagnostics', 'Bioinformatics', 'Genetic Counseling', 'Risk Assessment',
                      'Single Nucleotide Polymorphism', 'Whole Exome Sequencing', 'Whole Genome Sequencing',
                      'CRISPR - CRISPR', 'Liquid Biopsy', 'Personalized Medicine', 'Genetic Marker',
                      'Hereditary Diseases', 'Genetic Variant', 'Pathogenic Variant', 'Benign Variant',
                      'Variant of Unknown Significance', 'Genetic Predisposition', 'Gene Panel Testing',
                      'Tumor Profiling', 'Oncogenetics', 'Epigenetics', 'Gene Expression Profiling', 'Gene Knockout',
                      'Gene Silencing', 'Next-Generation Sequencing', 'Haplotyping', 'Microarray Analysis',
                      'Non-Invasive Prenatal Testing', 'Genetic Linkage Analysis', 'Syndromic Testing',
                      'Targeted Therapy', 'Clinical Genomics', 'Sanger Sequencing',
                      'Multiplex Ligation-dependent Probe Amplification', 'Quantitative PCR',
                      'Reverse Transcription PCR', 'Comparative Genomic Hybridization', 'Single-Cell Genomics',
                      'Cytogenetics', 'Transcriptomics', 'Proteomics', 'Metabolomics', 'Biomarker Discovery',
                      'Functional Genomics', 'Structural Variants', 'Copy Number Variants',
                      'Genotype-Phenotype Correlation', 'Precision Medicine', 'Preimplantation Genetic Diagnosis',
                      'Genome-Wide Association Studies', 'Forensic Genetics', 'Nutrigenomics', 'Immunogenetics',
                      'Genetic Epidemiology', 'Genetic Architecture', 'Exon Skipping', 'Antisense Oligonucleotides',
                      'Gene Editing', 'CRISPR-Cas9 - CRISPR-Cas9', 'Gene Drive', 'High-Throughput Screening',
                      'In Situ Hybridization', 'Linkage Disequilibrium', 'Mendelian Inheritance', 'Monogenic Disorders',
                      'Polygenic Risk Score', 'Regenerative Medicine', 'RNA Sequencing', 'Gene Panels', 'Tissue Typing',
                      'Xenotransplantation Genetics', 'Zygosity Testing', 'Synthetic Biology',
                      'Chimeric Antigen Receptor T-cell Therapy', 'Molecular Cloning', 'Therapeutic Cloning',
                      'Vector Design', 'Gene Networks', 'Systems Biology', 'Bioethical Considerations in Genetics',
                      'Population Genetics', 'Mitochondrial DNA Testing', 'Neonatal Genomics', 'Gene Doping',
                      'Human Leukocyte Antigen Testing', 'Microsatellite Instability Testing', 'Gene Signature',
                      'Exome Capture', 'Whole Transcriptome Shotgun Sequencing', 'Digital PCR', 'Genetic Modification',
                      'Single-Molecule Real-Time Sequencing']
    Keywords_upper = ['ChIP','SNP','LCR','qPCR', 'RT-PCR', 'CGH', 'CNV', 'PGD', 'GWAS', 'ASOs', 'ISH', 'PRS', 'RNA-seq', 'RNA', 'CAR-T',
                      'mtDNA', 'HLA', 'MSI', 'SMRT', 'DNA', 'SNP', 'WES', 'WGS', 'NGS', 'NIPT', 'VUS']

    with open(dir_paths["SelectedTissue.json"], 'r') as json_file:
        SelectedTissue = json.load(json_file)

    with open(dir_paths["Dict_Index_TissueRecord_Full.json"], 'r') as file:
        Dict_TissueCancerNames_Full = json.load(file)

    with open(dir_paths["Dict_Index_TissueRecord.json"] , 'r') as file:
        Dict_Index_TissueRecord = json.load(file)

    if os.path.exists(dir_paths["Dict_Records_Gene.json"]):
        with open(dir_paths["Dict_Records_Gene.json"], 'r') as json_file:
            Dict_Records_Gene = json.load(json_file)
    else:
        Dict_Records_Gene = {}

    if os.path.exists(dir_paths["Dict_Records_Gene_prompts.json"]):
        with open(dir_paths["Dict_Records_Gene_prompts.json"], 'r') as json_file:
            Dict_Records_Gene_prompts = json.load(json_file)
    else:
        Dict_Records_Gene_prompts = {}

    if os.path.exists(dir_paths["Dict_Records_GeneText.json"]):
        with open(dir_paths["Dict_Records_GeneText.json"], 'r') as json_file:
            Dict_Records_GeneText = json.load(json_file)
    else:
        Dict_Records_GeneText = {}

    if os.path.exists(dir_paths["Dict_Records_GeneText_prompts.json"]):
        with open(dir_paths["Dict_Records_GeneText_prompts.json"], 'r') as json_file:
            Dict_Records_GeneText_prompts = json.load(json_file)
    else:
        Dict_Records_GeneText_prompts = {}

    Dict_Records_Gene_kw_indice = {}

    # for index_cancer in range(len(SelectedTissue)):
    for index_cancer, tissue in enumerate(Dict_TissueCancerNames_Full):
        # tissue = SelectedTissue[index_cancer]
        Dict_TissueCancerName_Full = Dict_TissueCancerNames_Full[tissue]
        List_TissueRecord_Index = Dict_Index_TissueRecord[tissue]["index"]
        List_TissueRecord_Subdisease = Dict_Index_TissueRecord[tissue]["subdisease"]
        Index_TissueRecord_Index_num = len(List_TissueRecord_Index)
        print("*" * 100)
        print("-" * 20 + "     " + "{}:{}({})".format(index_cancer, tissue,
                                                      Index_TissueRecord_Index_num) + "     " + "-" * 20)
        print("*" * 100)



        gene_kw_indice = []
        for indice_i in range(len(List_TissueRecord_Index)):
            indice_s = List_TissueRecord_Index[indice_i]
            record = list_records[indice_s]

            exist_gene = False
            for Keyword_lower in Keywords_lower:
                if Keyword_lower.lower() in record.lower():
                    exist_gene = True
                    break
            if not exist_gene:
                for Keyword_upper in Keywords_upper:
                    if Keyword_upper in record.lower():
                        exist_gene = True
                        break
            if exist_gene:
                gene_kw_indice.append(indice_s)

        print("{}/{}".format(len(gene_kw_indice), len(List_TissueRecord_Index)))
        Dict_Records_Gene_kw_indice[tissue] = gene_kw_indice

        with open(dir_paths["Dict_Records_Gene_kw_indice.json"], 'w') as json_file:
            json.dump(Dict_Records_Gene_kw_indice, json_file, indent=4)


if __name__ == '__main__':
    from get_dir_paths import get_dir_paths

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)

    """
    1. init llm
    """
    model_type = "local"
    # model_type = "api"

    # model_name = "llama3"
    # model_name = "medllama2"
    model_name = "Llama-3.1-8B-Instruct"
    # model_name = "Qwen2.5-7B-Instruct"

    S2_1_Filter_Gene(dir_paths, model_type, model_name)

