#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-
"""
@describe: 大众点评评分抓取-解析
"""
import sys
import io
import os
import re
import requests
import urllib
from pyquery import PyQuery as pq

from urllib.request import urlopen

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

header_pinlun = {
    'Host': 'www.dianping.com',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
}

header_css = {
    'Host': 's3plus.meituan.net',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

}


# 0-详情页
def get_msg():
    """
    url: http://www.dianping.com/shop/+ 商铺ID +/review_all
    :return:
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
    # url = "http://m.dianping.com/shop/500212"
    # html = requests.get(url, headers=header_pinlun)
    # print("1 ===> STATUS", html.status_code)
    # doc = pq(html.text)
    path = sys.argv[1]
    html = open(path, 'r', encoding="utf-8")
    htmlcontent = html.read()

    doc = pq(htmlcontent)

    # 解析每条评论
    pinglunLi = doc("div.description").items()
    """
    调用评论里的css样式处理和加密字体svg处理
    :return:
    dict_svg_text: svg整个加密字库，以字典形式返回
    list_svg_y：svg背景中的<path>标签里的[x,y]坐标轴，以[x,y]形式返回
    dict_css_x_y：css样式中，每个加密字体的<span> 标签内容，用于匹配dict_svg_text 中的key，以字典形式返回
    """
    dict_svg_text, list_svg_y, dict_css_x_y = css_get(doc)

    for data in pinglunLi:
        pinglun = data("div.description").html()
        print("", css_decode(dict_css_x_y, dict_svg_text, list_svg_y, pinglun))
        service = doc("div.star_icon").html()
        print("", service)


# 1-评论隐含部分字体css样式, 获取svg链接，获取加密汉字background
def css_get(doc):
    css_link = "http:" + doc("body > link:nth-child(5)").attr("href")
    background_link = requests.get(css_link, headers=header_css)
    r = r'background-image: url(.*?);'
    matchObj = re.compile(r, re.I)
    svg_link = matchObj.findall(background_link.text)[0].replace(")", "").replace("(", "http:")
    """
    svg_text() 方法：请求svg字库，并抓取加密字
    dict_svg_text: svg整个加密字库，以字典形式返回
    list_svg_y：svg背景中的<path>标签里的[x,y]坐标轴，以[x,y]形式返回
    """
    dict_avg_text, list_svg_y = svg_text(svg_link)
    if dict_avg_text == {}:  # 判断值是否在小于0或大于10
        svg_link = matchObj.findall(background_link.text)[4].replace(")", "").replace("(", "http:")
        dict_avg_text, list_svg_y = svg_text(svg_link)
    """
    css_dict() 方法：生成css样式中background的样式库
    dict_css: 返回css字典样式
    """
    dict_css = css_dict(background_link.text)
    return dict_avg_text, list_svg_y, dict_css


# 2-字体库链接
def svg_text(url):
    html = requests.get(url)
    dict_svg, list_y = svg_dict(html.text)
    return dict_svg, list_y


# 3-生成svg字库字典
def svg_dict(csv_html):
    #svg_text_r = r'<textPath xlink:href="(.*?)" textLength="(.*?)">(.*?)</textPath>'
    svg_text_r = r'<text x="(.*)" y="(.*)">(.*?)</text>'
    svg_text_re = re.findall(svg_text_r, csv_html)
    dict_avg = {}
    # # 生成svg加密字体库字典
    for data in svg_text_re:
         dict_avg[data[0].replace("#", "")] = list(data[2])
    """
    重点：http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/74d63812e5b327d850ab4a8782833d47.svg
        svg <path> 标签里内容对应css样式中background的y轴参数，小于关系，
        如果css样式中的background的y参数小于 svg_y_re 集合中最小的数，则向上取y轴，('18', 'M0', '748', 'H600')，
        如.gqi4j {background: -98.0px -745.0px;} 中的y-745，取正数745，小于748，则对应加密字库实际y轴为748，对应的18就是<textPath>中的x轴
    """
    svg_y_r = r'<text x="(.*)" y="(.*)">(.*?)</text>'
    svg_y_re = re.findall(svg_y_r, csv_html)
    list_y = []

    # 存储('18', 'M0', '748', 'H600') eg:(x坐标，未知，y坐标，未知)
    for data in svg_y_re:
        list_y.append([data[0], data[2]])
    return dict_avg, list_y


# 4-生成css字库字典
def css_dict(html):
    css_text_r = r'.(.*?){background:(.*?)px (.*?)px;}'
    css_text_re = re.findall(css_text_r, html)

    dict_css = {}
    for data in css_text_re:
        """
        加密字库.gqi4j {background: -98.0px -745.0px;}与svg文件对应关系，x/14，就是svg文件加密字体下标
        y，原样返回，需要在svg函数中做处理
        """
        x = int(float(data[1]))
        """
        字典参数：{css参数名：(background-x,background-y,background-x/14,background-y)}
        """
        dict_css[data[0]] = (data[1], data[2], x, data[2])
    return dict_css


# 5-最终评论汇总
def css_decode(css_html, svg_dict, svg_list, pinglun_html):
    """
    :param css_html: css 的HTML源码
    :param svg_dict: svg加密字库的字典
    :param svg_list: svg加密字库对应的坐标数组[x, y]
    :param pinglun_html: 评论的HTML源码，对应0-详情页的评论，在此处理
    :return: 最终合成的评 论
    """
    css_dict_text = css_html
    csv_dict_text, csv_dict_list = svg_dict, svg_list
    # 处理评论源码中的span标签，生成字典key
    pinglun_text = pq(pinglun_html.replace('<span class="', ',').replace('"/>', ",")).text()
    pinglun_list = [x for x in pinglun_text.split(",") if x != '']
    pinglun_str = []
    for msg in pinglun_list:
        # 如果有加密标签
        if msg in css_dict_text:
            x = -int(css_dict_text[msg][2])
            for g in csv_dict_list:
                bin = g[0].split(' ')
                for k in range(len(bin)):
                    if bin[k] != "":
                        if x < int(bin[k]):
                            pinglun_str.append(list(csv_dict_text.values())[0][k])
                            break
                            quit()
        # 没有加密标签
        else:
            pinglun_str.append(msg.replace("\n", ""))

    str_pinglun = ""
    for x in pinglun_str:
        str_pinglun += x
    return str_pinglun


if __name__ == '__main__':
    get_msg()
