import shutil
import os
import datetime

datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

format_template = '''---
title: {title}
date: {date}
top: {is_top_boolstr}
cover: {is_cover_boolstr}
toc: true
mathjax: false
categories: {categories}
tags:
  - {tags}
--- 
 
'''
markdown_dir='data/blog'
dest_path = 'source/_posts/'

def process_format(src_path, filename):
    with open(src_path, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        content = first_line+file.read()
    if not '---' in first_line:
        hexo_template = format_template.format(title= os.path.basename(src_path).split('.')[0]    , date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), is_top_boolstr='false', is_cover_boolstr='false', categories='common', tags='common')     
        content = hexo_template+content
    content = '\n'.join(line for line in content.split('\n') if '@[TOC]' not in line)
    # 保存修改后的内容
    with open(src_path, 'w', encoding='utf-8') as file:
        file.write(content)        
    shutil.copy(src_path, dest_path+filename)
    

for root, dirs, files in os.walk(markdown_dir):
    for filename in files:
        if filename.endswith('.md'):
            process_format(os.path.join(root, filename), filename)

