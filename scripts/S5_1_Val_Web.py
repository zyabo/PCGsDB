import pickle
import json
import pandas as pd
import ollama
import re
import time
import pickle
import os
import pandas as pd
import json
import pprint
from collections import Counter
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import shutil
try:
    from scripts.call_llm import get_response, init_llm, get_model_dict
    from scripts.pathfile import parse_path
except:
    from call_llm import get_response, init_llm, get_model_dict
    from pathfile import parse_path

def create_search_url(query: str) -> str:
    from urllib.parse import quote_plus
    base_url = "https://duckduckgo.com/"
    # URL encode the query parameters
    encoded_query = quote_plus(query)
    # Construct the full URL for the search
    full_url = f"{base_url}?t=h_&q={encoded_query}&ia=web"
    return full_url

def search_query(Query_str, browser):
    full_url = create_search_url(Query_str)
    for t0 in range(0,10):
        try:
            browser.get(full_url)
            break
        except:
            time.sleep(3)
            pass

    more_page_n = 0
    for t1 in range(0, more_page_n):
        try:
            # 使用显式等待确保按钮可点击
            wait = WebDriverWait(browser, 3)
            more_results_button = wait.until(EC.element_to_be_clickable((By.ID, "more-results")))

            # 点击按钮加载更多结果
            more_results_button.click()

            # 可以选择再次等待一段时间，确保新内容加载完成
            time.sleep(1)
        except:
            try:
                # 向下滚动页面
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # 可以选择等待几秒钟，让页面加载
                time.sleep(1)
            except:
                pass

    # 获取页面的HTML内容
    html_data = browser.page_source

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_data, 'html.parser')

    # Find all <li> tags with data-layout="organic"
    organic_lis = soup.find_all('li', attrs={'data-layout': 'organic'})

    # List to hold all extracted URLs
    urls = []

    # Extract URLs from each li element
    for li in organic_lis:
        h2 = li.find('h2')
        if h2:
            a_tag = h2.find('a')
            if a_tag and a_tag.has_attr('href'):
                urls.append(a_tag['href'])

    # Output the URLs
    # for url in urls:
    #     print(url)
    return urls



def S5_1_Val_Web(dir_paths):
    Dict_Gene_Level_pth = dir_paths["Dict_Gene_Level.json"]

    with open(Dict_Gene_Level_pth, 'r') as file:
        Dict_Gene_Level = json.load(file)

    try:
        with open(dir_paths["Dict_Gene_Val.json"], 'r') as file:
            Dict_Gene_Val = json.load(file)
    except:
        Dict_Gene_Val = Dict_Gene_Level

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)

    """
    
    """
    for index, (tissue, Dict_Gene_Level_Single) in enumerate(Dict_Gene_Level.items()):
        print("*" * 100)
        print("-" * 20 + "     " + "{}: {}".format(index, tissue) + "     " + "-" * 20)

        genes_name = Dict_Gene_Level_Single["genes_name"]
        genes_level = Dict_Gene_Level_Single["genes_level"]
        genes_num = Dict_Gene_Level_Single["genes_num"]
        genes_index = Dict_Gene_Level_Single["genes_index"]
        genes_Score_CGC_GeneID = Dict_Gene_Level_Single["genes_Score_CGC_GeneID"]
        genes_Score_CGC_Tier = Dict_Gene_Level_Single["genes_Score_CGC_Tier"]
        genes_Score_CGC_Exist = Dict_Gene_Level_Single["genes_Score_CGC_Exist"]
        genes_Score_DisGeNET_exist = Dict_Gene_Level_Single["genes_Score_DisGeNET_exist"]
        genes_Score_DisGeNET_min = Dict_Gene_Level_Single["genes_Score_DisGeNET_min"]
        genes_Score_DisGeNET_max = Dict_Gene_Level_Single["genes_Score_DisGeNET_max"]
        val_webs = [{}]*len(genes_num)

        if "val_webs" in Dict_Gene_Val[tissue].keys():
            continue
        else:
            for g1, gene_level in enumerate(genes_level):
                print("{}/{}  {} ".format(g1, len(genes_level), gene_level))

                if gene_level == 3:
                    print("√")

                    gene_name = genes_name[g1]
                    gene_num = genes_num[g1]
                    """
                    execute online search
                    """
                    # Mutated Genes
                    Query_str = '{} cancer "{}" gene mutation'.format(tissue, gene_name)
                    urls = search_query(Query_str, browser)

                    val_web_urls = [""] * len(urls)
                    val_web_texts = [""] * len(urls)
                    val_web_types = [""] * len(urls)
                    for u1, url in enumerate(urls):
                        val_web_urls[u1] = url
                        for t1 in range(10):
                            try:
                                browser.get(url)
                                break
                            except:
                                time.sleep(1)
                                pass

                        # 检查当前URL是否以.pdf结尾
                        if browser.current_url.endswith('.pdf'):

                            text_data = ""
                            try:
                                # 下载PDF文件
                                response = requests.get(browser.current_url, stream=True)
                                if response.status_code == 200:
                                    with open('temp.pdf', 'wb') as f:
                                        response.raw.decode_content = True
                                        shutil.copyfileobj(response.raw, f)

                                    # 读取PDF内容
                                    with pdfplumber.open('temp.pdf') as pdf:
                                        for page in pdf.pages:
                                            # print(page.extract_text())
                                            text_data = text_data + page.extract_text()
                                else:
                                    print("Failed to download the PDF")
                            except:
                                pass
                            val_web_texts[u1] = text_data
                            val_web_types[u1] = "pdf"

                        else:
                            # 获取页面的HTML内容
                            html_data = browser.page_source
                            val_web_texts[u1] = html_data
                            val_web_types[u1] = "html"
                    val_webs[g1] = {"urls": val_web_urls, "texts": val_web_texts, "types": val_web_types}

        Dict_Gene_Val[tissue] = {"genes_name": genes_name,
                                   "genes_level": genes_level,
                                   "genes_num": genes_num,
                                   "genes_index": genes_index,
                                   "genes_Score_CGC_GeneID": genes_Score_CGC_GeneID,
                                   "genes_Score_CGC_Tier": genes_Score_CGC_Tier,
                                   "genes_Score_CGC_Exist": genes_Score_CGC_Exist,
                                   "genes_Score_DisGeNET_exist": genes_Score_DisGeNET_exist,
                                   "genes_Score_DisGeNET_min": genes_Score_DisGeNET_min,
                                   "genes_Score_DisGeNET_max": genes_Score_DisGeNET_max,
                                   "val_webs": val_webs}
        with open(dir_paths["Dict_Gene_Val.json"], 'w') as json_file:
            json.dump(Dict_Gene_Val, json_file, indent=4)

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    Dict_Gene_Level_pth = r'D:\\Codes\\GeneExplorer\\results\\data_files\\Dict_Gene_Level.json'
    S5_1_Val_Web(dir_paths)




