

# PCGs DB

This repository contains the implementation for the work **PCGs DB: A database of potential cancer-associated genes mined from medical reports via large language models**



## How to use

You can mine a dataset from scratch or download a mined dataset directly for viewing.



## 1.Building PCGs DB from scratch

#### 1.1 Install dependencies

##### 1.1.1 Conda Virtual Environment

The source code runs on Python. All dependencies are listed in `requirements.txt`. Data and models are automatically downloaded upon the first execution of the pipeline.

To install the dependencies, consider creating a virtual environment:

```bash
python -m venv my-virtual-venv
source my-virtual-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```



##### 1.1.2 Chrome driver installation and configuration

To install and configure the Chrome Driver on a Windows system for use with automation frameworks like Selenium, you can follow these detailed steps:

###### a. Check Your Chrome Version
First, ensure that the Chrome browser is installed on your Windows machine. You need to check your version of Chrome to download the corresponding version of ChromeDriver.

- Open Chrome.
- Click on the three dots in the upper right corner to open the menu.
- Go to `Help` > `About Google Chrome`.
- Note the version number displayed there.

###### b. Download ChromeDriver
Next, download the appropriate version of ChromeDriver based on your Chrome version.

- Visit the ChromeDriver download page: [ChromeDriver - WebDriver for Chrome](https://sites.google.com/chromium.org/driver/)
- Find the version of ChromeDriver that matches your Chrome version.
- Click on the link for the Windows version to download the `.zip` file.

###### c. Extract the Downloaded File
Once the download is complete, extract the `.zip` file.

- Navigate to the folder where the `.zip` file was downloaded.
- Right-click on the zip file and select `Extract All…`.
- Choose the location where you want to extract the files (it's advisable to extract it to a known directory like `C:\WebDrivers`).

###### d. Add ChromeDriver to Your PATH
To easily use ChromeDriver from any command line interface, you should add it to your Windows PATH.

- Right-click on `This PC` or `My Computer` on your desktop or in File Explorer.
- Select `Properties`.
- Click on `Advanced system settings`.
- In the System Properties window, click on the `Environment Variables` button.
- In the Environment Variables window, select the `Path` variable under System variables (or create it if it's not there).
- Click on `Edit`.
- In the Edit Environment Variable window, click `New` and add the path where you extracted your ChromeDriver (e.g., `C:\WebDrivers`).
- Click `OK` to close all dialogs.

###### e. Verify Installation
To verify that ChromeDriver is set up correctly, open a command prompt and type:

```cmd
chromedriver
```

If everything is set up correctly, you should see a message indicating that ChromeDriver is running and listening on a port.

###### f. Configuring Your Selenium Test
Finally, in your Selenium tests, you can now set up WebDriver to use ChromeDriver. Here’s an example in Python:

```python
from selenium import webdriver

driver_path = 'C:/WebDrivers/chromedriver.exe'  # Path to the ChromeDriver executable
driver = webdriver.Chrome(executable_path=driver_path)
driver.get('https://www.google.com')
```

This script initializes the Chrome browser through Selenium using the ChromeDriver you've just set up. The `executable_path` parameter is used to specify the location of `chromedriver.exe` if it's not added to the PATH or if you want to use a specific version of the driver.

By following these steps, you can successfully install and configure ChromeDriver on a Windows system for automated testing with Selenium.



##### 1.1.3 Ollama

Need to install llama 3.1 8B model：

```
ollama run llama3.1:8b
```

For more information, please visit https://ollama.com/



#### 1.2 Data preparation

Before reconstructing the data set, you need to download the following data set locally.

| Datasets     | Source                                    |
| ------------ | ----------------------------------------- |
| PMC-Patients | https://github.com/zhao-zy15/PMC-Patients |
| OncoTree     | https://oncotree.mskcc.org/               |
| CGC          | https://cancer.sanger.ac.uk/census        |
| DisGeNET     | https://disgenet.com/                     |

The above dataset needs to be downloaded and placed in the datasets folder.

To access the NCBI Gene dataset you need to install the chrome driver.



#### 1.3 Database creation

##### 1.3.1 Prepare

```
# Check settings
python scripts/S0_0_Check_Settings.py

# Prepare Oncotree dataset
python scripts/S0_1_Oncotree.py

# Prepare keyword library
python scripts/S0_2_CancerList.py

# Prepare complete keyword library
python scripts/S0_3_CancerList_Full.py

# Statistic
python scripts/S0_4_Statis.py
```



##### 1.3.2 Rapid Screening of Cancer Cases

```
python scripts/S1_1_Filter_Index_TissueRecord.py
python scripts/S1_2_Filter_Index_TissueRecord_Full.py
python scripts/S1_3_Filter_Index_TissueRecord_Full_Statis.py
```



##### 1.3.3 Mutation Gene Extraction

```
python scripts/S2_0_Filter_Gene_Keywords.py
python scripts/S2_1_Filter_Gene.py
python scripts/S2_2_Filter_Gene_Extract.py

# reading comprehension and structured information extraction
python scripts/S3_1_Extract_GeneText.py
python scripts/S3_2_Extract_GeneDict.py
python scripts/S3_3_Gene_Statis.py
python scripts/S3_4_Gene_Rename.py

# Grading of Potential Associated Genes
python scripts/S4_1_Score_DisGeNET.py
python scripts/S4_2_Score_CGC.py
python scripts/S4_3_Score_Level.py
```



##### 1.3.4 Literature-based Validation

```
python S5_1_Val_Web.py
python S5_2_Val_Text.py
python S5_3_Val.py
```



## 2.Download and view the dataset

Ensure that the `dataset` folder contains the appropriate data before starting training. 





