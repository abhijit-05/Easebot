import re
import difflib
import pdfplumber

from langchain_core.documents import Document

def extract_text_before_chapter(input_string):
    pattern = r'(.*)(?=\nChapter V: Placement Support \d+)'
    match = re.search(pattern, input_string, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

def is_substring_similar(s1, s2, threshold=0.7):
    """
    Check if any part of s2 is similar to s1 based on a given threshold.
    
    :param s1: The string to search for
    :param s2: The paragraph to search within
    :param threshold: Similarity threshold (default is 0.7)
    :return: True if a similar substring is found, otherwise False
    """
    s1 = s1.lower()
    s2 = s2.lower()
    len_s1 = len(s1)
    for i in range(len(s2) - len_s1 + 1):
        substring = s2[i:i+len_s1]
        similarity_ratio = difflib.SequenceMatcher(None, s1, substring).ratio()
        if similarity_ratio >= threshold:
            return True
    return False

def page_wise_retrieval(pdf_path):
    documents = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                documents.append(Document(page_content=text, metadata={"page_no": i+1}))
    return documents

def add_page_data(splits, pdf_page_split):
    split_curr = 0
    for i in range(len(pdf_page_split)):
        la_data = extract_text_before_chapter(pdf_page_split[i].page_content[-75:])
        for j in range(split_curr, len(splits)):
            splits[j].metadata['source'] += f'#page={i+1}'
            if is_substring_similar(la_data, splits[j].page_content):
                split_curr = j + 1
                break

