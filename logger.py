#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from config import LOG_FILE

formatter = logging.Formatter(
    fmt='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logger = logging.getLogger("ArticleCrawler")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


if __name__ == '__main__':
    pass
