# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, element
import requests
import json
from docx import Document

from logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import *

class ArticleCrawler(object):
    def __init__(self, url=WORKING_URL, output_dir=OUTPUT_DIRECTORY, output_fn=OUTPUT_FILENAME,
                 datafile=USER_DATA_FILE):
        self.url = url
        self.output_dir = output_dir
        self.output_fn = output_fn
        self.datafile = datafile

        with open(USER_DATA_FILE) as f:
            self.old_articles = json.load(f)

    def get_web_content(self, url=None, present_class="main_col"):
        target_url = url if url else self.url
        driver = webdriver.Chrome(CHROME_DRIVER)
        driver.get(target_url)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, present_class))
            )
        finally:
            soup = BeautifulSoup(driver.page_source,  "html.parser")
            driver.quit()
            return soup

    def get_articles(self):
        content = self.get_web_content()
        return [(item.string, WORKING_DOMAIN + item['href']) for item in content.find_all(class_="question_link")]

    def get_new_articles(self):
        articles = self.get_articles()
        return [item for item in articles if item[0] not in self.old_articles and TARGET_TITLE in item[0]]

    def get_article_content(self, url):
        content = self.get_web_content(url, "rich_media_content").find("section", class_="Powered-by-XIUMI V5")
        return content

    def parse_html_to_docx(self, title, content, doc):
        start_num, end_num = title.replace(TARGET_TITLE, "").replace(" ", "").split("-")
        all_p = content.find_all("p")

        init = 0
        for i, p in enumerate(all_p):
            if len(p.find_all("strong")) == 1 and len(p.strong.contents) == 1 and \
                    isinstance(p.strong.contents[0], element.NavigableString) and \
                    p.strong.contents[0].startswith(start_num):
                init = i
                break

        for p in all_p[init:]:




if __name__ == '__main__':
    crawler = ArticleCrawler()
    # print crawler.get_article_content()

    l = range(5)

    for i, j in enumerate(l):
        if j == 3:
            break

    print l[i:] if i else l

