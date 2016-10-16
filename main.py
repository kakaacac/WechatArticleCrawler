# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, element
import requests
import json
from docx import Document
import os
import codecs

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

    def get_web_content(self, url=None, present_tag="class", present_element="main_col"):
        target_url = url if url else self.url
        tag = By.ID if present_tag == 'id' else By.CLASS_NAME
        driver = webdriver.Chrome(CHROME_DRIVER)
        driver.get(target_url)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((tag, present_element))
            )
        finally:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()
            return soup

    def get_articles(self, url=None):
        content = self.get_web_content(url=url)
        return [(item.string.strip(), WORKING_DOMAIN + item['href']) for item in content.find_all(class_="question_link")]

    def get_new_articles(self, url=None):
        articles = self.get_articles(url=url)
        return [item for item in articles if item[0] not in self.old_articles and TARGET_TITLE in item[0]]

    def get_article_content(self, url):
        content = self.get_web_content(url, "id", "js_content")
        return content

    def output_to_html(self, title, content):
        start_num, end_num = title.replace(TARGET_TITLE, "").replace(" ", "").split("-")
        all_p = content.find_all("p")

        init = 0
        for i, p in enumerate(all_p):
            if self.is_title(p) and p.strong.contents[0].startswith(start_num):
                init = i
                break

        output_filename = title + u".html"
        with codecs.open(os.path.join(self.output_dir, output_filename), 'w', encoding="utf-8") as f:
            beginning_html = '<!DOCTYPE html><html>' \
                             '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body>'
            ending_html = '</body></html>'

            f.write(beginning_html)

            last_one = False
            for p in all_p[init:]:
                if self.is_title(p) and p.strong.contents[0].startswith(end_num):
                    last_one = True

                f.write(unicode(p))

                if last_one and p.find("br"):
                    break

            f.write(ending_html)

        self.update_downloaded_list(title)

    def update_downloaded_list(self, title):
        self.old_articles.append(title)
        with codecs.open(USER_DATA_FILE, 'wb', encoding="utf-8") as f:
            json.dump(self.old_articles, f, indent=2, ensure_ascii=False)

    def run(self, url=None):
        articles = self.get_new_articles(url=url)
        for article in articles:
            self.output_to_html(article[0], self.get_article_content(article[1]))

    def get_all(self, ignore_old=False):
        if ignore_old:
            self.old_articles = []
            with codecs.open(USER_DATA_FILE, 'wb', encoding="utf-8") as f:
                json.dump(self.old_articles, f, indent=2, ensure_ascii=False)

        total = 1
        for start in range(total):
            url = self.url + "?start={}".format(start*12)
            self.run(url=url)


    @staticmethod
    def is_title(p):
        return len(p.find_all("strong")) >= 1 and len(p.strong.contents) == 1 and \
               isinstance(p.strong.contents[0], element.NavigableString)

    def is_content(self, p):
        """ Deprecated """
        check = True
        for c in p.contents:
            if not (isinstance(c, unicode) or self.is_emphases(c) or (isinstance(c, element.Tag) and c.name == "em")):
                return False
        return check

    @staticmethod
    def is_emphases(e):
        """ Deprecated """
        return e.name == "span" and u"color: rgb(255, 0, 0)" in e['style']



if __name__ == '__main__':
    crawler = ArticleCrawler()
    crawler.get_all()
    # p = BeautifulSoup('<p style="max-width: 100%; min-height: 1em; white-space: pre-wrap; color: rgb(62, 62, 62); line-height: 25px; -webkit-text-stroke-width: initial; text-align: justify; font-family: Avenir; -webkit-text-stroke-color: rgb(0, 0, 0); box-sizing: border-box !important; word-wrap: break-word !important; background-color: rgb(255, 255, 255);"><strong style="max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important;">141、inside and out 从里到外，彻底</strong></p>', "html.parser")
    # print type(p.find("p")['style'])

