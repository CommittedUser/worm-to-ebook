#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unidecode import unidecode
from collections import namedtuple
import subprocess
import os
import re
from bs4 import BeautifulSoup
from unidecode import unidecode

Chapter = namedtuple('Chapter', ['title', 'url', 'content'])

def html2rst(html):
    # adapted from http://johnpaulett.com/2009/10/15/html-to-restructured-text-in-python-using-pandoc/
    p = subprocess.Popen(['pandoc', '--from=html', '--no-wrap', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return unidecode(p.communicate(html)[0].decode('utf-8'))

def scrape_worm():
    page_content = subprocess.check_output(['curl', 'http://parahumans.wordpress.com/category/stories-arcs-1-10/arc-4-shell/4-x-interlude/'])

    soup = BeautifulSoup(page_content)

    categories = soup.find_all(attrs={"class":"widget_categories"})[0]
    groups = categories.contents[2]

    lis = groups.find_all("li")
    chapters = []
    for li in lis:
        if li.li is None:
            print li.a.contents[0], li.a.get('href')
            url = li.a.get('href')
            mirror_path = os.path.join(url.replace('http://parahumans.wordpress.com', 'mirror'),'index.html')
            mirror_path = mirror_path.encode('ascii', 'ignore')
            os.system('mkdir -p ' + os.path.split(mirror_path)[0])
            with open(mirror_path, 'w') as f:
                f.write(subprocess.check_output(['curl', url]))

def traverse_into_one():
    infos = []
    for root, dirs, files in os.walk('mirror/category/'):
        for f in files:
            temp=(root[(root[16:]).find("/")+17:]).replace('/','_')
            if temp.find("arc") != -1:
                if temp[5]=='-':
                    temp="arc-0"+temp[4:]
            os.system("cp " + os.path.join(root,f) + " files/"+temp+".html")
            with open("files/"+temp+".html") as html:
                soup = BeautifulSoup(html)
            elem = soup.find_all('article')
            contentstr = str(elem[0])

            contentstr = re.sub(r'<a href=".+">(.+)</a>', r'\1', contentstr)

            with open("formatted/"+temp+".html", 'w') as f:
                f.write("<html><body> " + contentstr + " </body></html>")

def make_toc():
    cmd = [ 'ls', 'formatted/' ]
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE ).communicate()[0]
    splitoutput = output.split('\n')
    tocstring = "<html><body><h1>Table of Contents</h1><p style=\"text-indent:0pt\">"
    for line in splitoutput:
        tocstring+="<a href=\"" + line + "\">" + line[:line.find(".")] + "</a><br/>"
    tocstring+="</p></body></html>"
    with open("formatted/0toc.html",'w') as f:
        f.write(tocstring)

if __name__ == '__main__':
    scrape_worm() #scrape from site
    traverse_into_one() #rename all files, format, and move to formatted directory
    make_toc() #create a simple table of contents named 0toc.html