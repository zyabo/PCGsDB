import pubmed_parser as pp

def pmc_parse_xml(path = r"E:\20TDatas\Datas\Collected\医学数据集\pubmed\PMC_oa_comm\PMC000xxxxxx\PMC556014.xml"):
    full_txt = ""

    dict_out = pp.parse_pubmed_xml(path) # dict_keys(['full_title', 'abstract', 'journal', 'pmid', 'pmc', 'doi', 'publisher_id', 'author_list', 'affiliation_list', 'publication_year', 'publication_date', 'epublication_date', 'subjects', 'coi_statement'])
    dicts_out_paragraphs = pp.parse_pubmed_paragraph(path, all_paragraph=False)

    try:
        full_txt = full_txt + "# Title: " + dict_out['full_title'] + "\n"
    except:
        pass

    try:
        full_txt = full_txt + "## Abstract\n" + dict_out['abstract'] + "\n"
    except:
        pass

    for dicts_out_paragraph in dicts_out_paragraphs:
        # dicts_out_paragraph.keys() # dict_keys(['pmc', 'pmid', 'reference_ids', 'section', 'text'])
        try:
            full_txt = full_txt + "## {}\n{}\n".format(dicts_out_paragraph["section"], dicts_out_paragraph['text'])
        except:
            pass

    return full_txt

if __name__ == '__main__':
    path = r"E:/20TDatas/Datas/Collected/%E5%8C%BB%E5%AD%A6%E6%95%B0%E6%8D%AE%E9%9B%86/pubmed/PMC_oa_comm/PMC005xxxxxx/PMC5000546.xml"
    full_txt = pmc_parse_xml(path)
    uu=1