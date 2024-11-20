import sqlite3
import pandas as pd
from collections import Counter
import json
import requests
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

def list_tables_and_columns(db_path='../datasets/disgenet_2020.db'):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取数据库中所有表格的名称
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # 遍历表格，打印每个表的字段
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            print(f"    Column: {column[1]}, Type: {column[2]}")

    # 关闭数据库连接
    cursor.close()
    conn.close()


"""
Table: diseaseAttributes
    Column: diseaseNID, Type: smallint(5)
    Column: diseaseId, Type: varchar(255)
    Column: diseaseName, Type: varchar(255)
    Column: type, Type: varchar(255)
Table: diseaseClass
    Column: diseaseClassNID, Type: tinyint(3)
    Column: vocabulary, Type: varchar(255)
    Column: diseaseClass, Type: varchar(255)
    Column: diseaseClassName, Type: varchar(255)
Table: disease2class
    Column: diseaseNID, Type: smallint(5)
    Column: diseaseClassNID, Type: smallint(5)
Table: geneAttributes
    Column: geneNID, Type: smallint(5)
    Column: geneId, Type: int(10)
    Column: geneName, Type: varchar(255)
    Column: geneDescription, Type: varchar(255)
    Column: pLI, Type: double
    Column: DSI, Type: double
    Column: DPI, Type: double
Table: geneDiseaseNetwork
    Column: NID, Type: int(10)
    Column: diseaseNID, Type: smallint(5)
    Column: geneNID, Type: smallint(5)
    Column: source, Type: varchar(255)
    Column: association, Type: mediumint(8)
    Column: associationType, Type: TEXT
    Column: sentence, Type: TEXT
    Column: pmid, Type: int(10)
    Column: score, Type: double
    Column: EL, Type: varchar(255)
    Column: EI, Type: double
    Column: year, Type: int(10)
Table: variantAttributes
    Column: variantNID, Type: SMALLINT (6)
    Column: variantId, Type: VARCHAR (255)
    Column: s, Type: class VARCHAR (255)
    Column: chromosome, Type: VARCHAR (255)
    Column: coord, Type: VARCHAR (255)
    Column: most_severe_consequence, Type: VARCHAR (255)
    Column: DSI, Type: double
    Column: DPI, Type: double
Table: variantGene
    Column: geneNID, Type: SMALLINT (5)
    Column: variantNID, Type: SMALLINT (6)
Table: variantDiseaseNetwork
    Column: NID, Type: int(10)
    Column: diseaseNID, Type: SMALLINT (5)
    Column: variantNID, Type: SMALLINT (6)
    Column: source, Type: VARCHAR (255)
    Column: association, Type: MEDIUMINT (8)
    Column: associationType, Type: TEXT
    Column: sentence, Type: TEXT
    Column: pmid, Type: INT (10)
    Column: score, Type: double
    Column: EI, Type: double
    Column: year, Type: int(10)
"""


def connect_db(db_path):
    """ Connect to the SQLite database. """
    conn = sqlite3.connect(db_path)
    return conn


def get_diseases_for_gene(gene_name, conn):
    """ Retrieve diseases associated with a specific gene. """
    query = """
    SELECT d.diseaseName, d.diseaseId, gd.score, gd.associationType
    FROM geneAttributes ga
    JOIN geneDiseaseNetwork gd ON ga.geneNID = gd.geneNID
    JOIN diseaseAttributes d ON gd.diseaseNID = d.diseaseNID
    WHERE ga.geneName = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (gene_name,))
    results = cursor.fetchall()
    return results


def check_if_gene_exists(db_path, gene_name):
    # Connecting to a SQLite Database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query gene name
    query = """
    SELECT EXISTS(SELECT 1 FROM geneAttributes WHERE geneName = ?)
    """
    cursor.execute(query, (gene_name,))
    exists = cursor.fetchone()[0]  # 将返回 1 如果存在，否则返回 0

    # Close the database connection
    conn.close()

    return exists == 1
def Diseases_associated_gene(db_path, gene_name):
    conn = connect_db(db_path)
    diseases = get_diseases_for_gene(gene_name, conn)
    conn.close()

    if diseases:
        print(f"Diseases associated with {gene_name}:")
        for disease in diseases:
            print(
                f"Disease Name: {disease[0]}, Disease ID: {disease[1]}, Score: {disease[2]}, Association Type: {disease[3]}")
    else:
        print(f"No diseases found associated with {gene_name}.")


def query_gene_disease_association(db_path, gene_name, disease_name):
    # Connecting to a SQLite Database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Constructing SQL queries
    query = """
    SELECT g.geneName, d.diseaseName, n.score, n.associationType
    FROM geneAttributes g
    JOIN geneDiseaseNetwork n ON g.geneNID = n.geneNID
    JOIN diseaseAttributes d ON n.diseaseNID = d.diseaseNID
    WHERE g.geneName = ? AND d.diseaseName = ?
    """

    # Execute a query
    cursor.execute(query, (gene_name, disease_name))

    # Get all results
    results = cursor.fetchall()

    conn.close()

    return results


def fetch_disease_nids(db_path, disease_keyword):
    # Connecting to a SQLite Database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Construct a SQL query to find disease IDs related to 'Breast Cancer'
    query = """
    SELECT diseaseNID, diseaseName
    FROM diseaseAttributes
    WHERE diseaseName LIKE ?
    """

    # '%Breast Cancer%' is used to fuzzy match any disease name containing 'Breast Cancer'
    cursor.execute(query, ('%' + disease_keyword + '%',))

    results = cursor.fetchall()

    conn.close()

    return results

# According to the gene name, get all the corresponding links
def get_diseases_associated_with_gene(db_path, gene_name, cancer_name = "", gene_num=0):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    gene_query = """
    SELECT geneNID
    FROM geneAttributes
    WHERE geneName = ?
    """

    cursor.execute(gene_query, (gene_name,))
    gene_nid_result = cursor.fetchone()
    gene_nid_0 = gene_nid_result[0] if gene_nid_result else None

    if not gene_nid_0:
        # print("   Try find right name")
        gene_name_new = fetch_gene_name(gene_name)

        cursor.execute(gene_query, (gene_name_new,))
        gene_nid_result = cursor.fetchone()
        gene_nid = gene_nid_result[0] if gene_nid_result else None

        if not gene_nid:
            print("{}   {} gene {}(Number of occurrences{})   {}".format("-" * 10, cancer_name, gene_name, gene_num, "-" * 10))
            print("   Gene({}) not found in the disgenet.".format(gene_name))
            return []

    # Use the gene's NID to query associated disease information
    associations_query = """
    SELECT d.diseaseName, n.score, n.associationType, n.sentence
    FROM geneDiseaseNetwork n
    JOIN diseaseAttributes d ON n.diseaseNID = d.diseaseNID
    WHERE n.geneNID = ?
    """
    if not gene_nid_0:
        cursor.execute(associations_query, (gene_nid,))
    else:
        cursor.execute(associations_query, (gene_nid_0,))
    results = cursor.fetchall()

    conn.close()

    return results

import os

def to_windows_filename(filename):
    # List of illegal characters that need to be replaced
    illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    # Replace illegal characters with underscores
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename

def extract_NCBI_gene_web(dir_paths, gene_name, browser):
    url = f"https://www.ncbi.nlm.nih.gov/gene/?term=({gene_name})+AND+Homo+sapiens%5BOrganism%5D"
    browser.get(url)

    filename_html = os.path.join(dir_paths["current_dir_path"], "results", "NCBI_gene_html_files",
                                 "{}.html".format(to_windows_filename(gene_name)))

    # filename_html = "../results/NCBI_gene_html_files/{}.html".format(to_windows_filename(gene_name))

    try:
        # Wait for the table to load
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[@class="jig-ncbigrid gene-tabular-rprt ui-ncbigrid"]'))
        )

        # Get table content
        table = browser.find_element(By.XPATH, '//table[@class="jig-ncbigrid gene-tabular-rprt ui-ncbigrid"]')

        html_content = table.get_attribute('outerHTML')

        with open(filename_html, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return html_content
    except:
        with open(filename_html, 'w', encoding='utf-8') as file:
            file.write("")
        return ""

    return ""

def fetch_gene_name(dir_paths,gene_name, browser):
    filename_html = os.path.join(dir_paths["current_dir_path"], "results", "NCBI_gene_html_files",
                                 "{}.html".format(to_windows_filename(gene_name)))

    # filename_html = "../results/NCBI_gene_html_files/{}.html".format(to_windows_filename(gene_name))
    if os.path.exists(filename_html):
        with open(filename_html, 'r', encoding='utf-8') as file:
            html_content = file.read()
    else:
        try:
            html_content = extract_NCBI_gene_web(dir_paths, gene_name, browser)
        except:
            html_content = ""
            filename_html = os.path.join(dir_paths["current_dir_path"] ,"results","NCBI_gene_html_files", "{}.html".format(to_windows_filename(gene_name)))

            with open(filename_html, 'w', encoding='utf-8') as file:
                file.write(html_content)


    if len(html_content) == 0:
        return ""

    table = BeautifulSoup(html_content, 'html.parser')

    #Extract all rows of a table
    rows = table.find_all("tr")

    # Loop through each row and check if the Aliases column contains "HER2"
    for row in rows:
        columns = row.find_all("td")

        if len(columns) > 3: # Make sure there are enough columns
            aliases = columns[3].text
            aliases_list = aliases.split(', ')
            aliases_list_full = []
            for aliase in aliases_list:
                aliases_list_full.append(aliase)
                aliases_list_full.append(aliase.lower())
            if gene_name in aliases_list_full:  # Check if the alias contains HER2
                gene_id = columns[0].text  # Get the value in the corresponding Name/Gene ID column
                segments = gene_id.split("ID:")
                ID = segments[1].strip()
                segments_n = segments[0].split(ID)
                gene_new_name = segments_n[1]
                print(f"  √  {gene_name} → {gene_new_name} ")
                return gene_new_name

    return ""


if __name__ == "__main__":
    filename_Dict_TissueCancerNames_Full = "../results/data_files/Dict_TissueCancerNames_Full.json"
    with open(filename_Dict_TissueCancerNames_Full, 'r') as file:
        Dict_TissueCancerNames = json.load(file)

    db_path = '../datasets/disgenet_2020.db'
    gene_name = "NF1"
    # gene_name = "MLL3"
    # tissue = "Soft Tissue"
    tissue = "CNS/Brain"
    if check_if_gene_exists(db_path, gene_name):
        Dict_TissueCancerNames_Single = Dict_TissueCancerNames[tissue]

        associations = get_diseases_associated_with_gene(db_path, gene_name, tissue)
        list_disease = []
        list_score = []
        list_association_type = []
        for disease, score, association_type, sentence in associations:
            for Dict_TissueCancerNames_S in Dict_TissueCancerNames_Single:
                TissueCancerName = Dict_TissueCancerNames_S["name"]
                if TissueCancerName in disease.lower():
                    list_disease.append(disease)
                    list_score.append(score)
                    list_association_type.append(association_type)
        if len(list_score) > 0:
                print("++ {}  {}-{}".format(gene_name,  min(list_score),max(list_score)))
        uu=1
    ssss=1