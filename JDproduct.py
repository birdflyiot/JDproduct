#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 时间：2016年12月10日
# 根据京东商品ID，获取评论中的型号等信息，保存为CSV格式，留作进一步分析用

# __author__ = 'bird'

from urllib import request,parse
from urllib.request import urlopen
import urllib.request

import csv
import re
import time


def get_productID():
    productID = input('请输入产品ID:')
    return productID


# 根据商品ID构造参数
def get_callback(productID):
    # 提取commentVersion:需要用到的正则表达式
    re_commentVersion = 'commentVersion:\'(.*?)\''#获得的就是（）内的值

    productURL = 'http://item.jd.com/' + productID + '.html'
    req = request.Request(productURL)
    response = request.urlopen(req)
    result = response.read().decode('raw_unicode_escape')
    commentVersion = (re.findall(re_commentVersion,result))
    callback = 'fetchJSON_comment98vv' + commentVersion[0]

    return callback
# 获得评论内容，页面依次递增


def get_comments(productID,callback):
    # 构造地址http://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3&productId=1025674073&score=0&sortType=5&page=0&pageSize=10
    page = 0
    '''
    当前商品评论https://club.jd.com/comment/skuProductPageComments.action?

    所有商品评论https://club.jd.com/comment/productPageComments.action?
    '''
    commentURL = 'http://club.jd.com/comment/productPageComments.action?callback=' + callback + '&productId=' + productID + '&score=0&sortType=5&page=' + str(page) + '&pageSize=10'
    # 获得评论的页数（总评论数/10）\
    re_commentCount = '\"commentCount\":(.*?),'#获得评论的总数
    re_replies = re.compile('\"replies\"\:\[(.*?)\]')#:[] 其中[]是特殊符号，需要转义（构造表达式对象和上面效果一样）
    re_showOrderComment = '\"showOrderComment\"\:\{(.*?)\}'#剔除其他信息showOrderComment
    re_referenceName = '\"referenceName\":\"(.*?)\"'#提取标题——保存文件名

    req_commentCount = request.Request(commentURL)
    response_commentCount = request.urlopen(req_commentCount)
    result_commentCount = response_commentCount.read().decode('gb18030')
    #print(response_commentCount)
    commentCount = (re.findall(re_commentCount, result_commentCount))
    referenceName = re.findall(re_referenceName,result_commentCount)
    tittle = re.sub('[\\ \/ \: \* \? \" < >]','',referenceName[0])
    print(tittle)

    column = ['会员类型','省份','颜色','型号','购买时间','评论时间','客户端']
    filename = str(productID) + tittle + '.csv'
    with open(filename, "a+", newline="") as datacsv:
        # dialect为打开csv文件的方式，默认是excel，delimiter="\t"参数指写入的时候的分隔符
        csvwriter = csv.writer(datacsv, dialect=("excel"))
        # csv文件插入一行数据，把下面列表中的每一项放入一个单元格（可以用循环插入多行）
        csvwriter.writerow(column)
    # print(commentCount)
    page_max = int((int(commentCount[0]))/10)
    print (page_max)

    page = 0
    while page < page_max:
        commentURL = 'http://club.jd.com/comment/productPageComments.action?callback=' + callback + '&productId=' + productID + '&score=0&sortType=5&page=' + str(page) + '&pageSize=10'
        req_comments = request.Request(commentURL)
        response_comments = request.urlopen(req_comments)
        result_comments = response_comments.read().decode('gb18030')

        try:
            result_comments = re_replies.sub('', result_comments)
        except:
            pass
        try:
            result_comments = re.sub(re_showOrderComment,'',result_comments)
        except:
            pass
        #print(result_comments)
        userLevelNameList = re.findall('\"userLevelName\":\"(.*?)\"',result_comments)
        userProvinceList = re.findall('\"userProvince\":\"(.*?)\"',result_comments)
        productColorList = re.findall('\"productColor\":\"(.*?)\"', result_comments)
        productSizeList = re.findall('\"productSize\":\"(.*?)\"', result_comments)
        referenceTimeList = re.findall('\"referenceTime\":\"(.*?)\"', result_comments)
        creationTimeList = re.findall('\"creationTime\":\"(.*?)\"', result_comments)
        userClientShowList = re.findall('\"userClientShow\":\"(.*?)\"', result_comments)
        length = len(userLevelNameList)
        if length == 0:
            break

        i = 0
        while i < length:
            try:
                row = []
                row.append(userLevelNameList[i])
                row.append(userProvinceList[i])
                row.append(productColorList[i])
                row.append(productSizeList[i].replace('海南','海南省'))
                row.append(referenceTimeList[i])
                row.append(creationTimeList[i])
                row.append(userClientShowList[i])

                with open(filename, "a+", newline="") as datacsv:
                    # dialect为打开csv文件的方式，默认是excel，delimiter="\t"参数指写入的时候的分隔符
                    csvwriter = csv.writer(datacsv, dialect=("excel"))
                    csvwriter.writerow(row)
            except:
                pass

            i = i + 1

        page = page + 1
        print('第{}页提取完毕'.format(page))
        time.sleep(1)

# 按评论数排序，根据关键字 批量提取某一类产品ID(排序在第一页的)，返回列表
def get_id_by_keyword():
    keyword = input("请输入要搜索的商品：")
    keyword = urllib.request.quote(keyword)
    # 按评论数排序的网址
    #https://search.jd.com/s_new.php?keyword=关键字&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=3&wq=关键字&psort=4&click=0
    jd_url = 'https://search.jd.com/s_new.php?keyword={}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=3&wq={}&psort=4&click=0'.format(keyword,keyword)
    jd_html = urlopen(jd_url).read().decode('utf-8')
    #print(jd_html)
    jd_id = re.findall('id=\"J_AD_(.*?)\"',jd_html)
    jd_id = list(set(jd_id)) # 去除重复的产品id
    # 据说下面方法更快
    # jd_id = {}.fromkeys(jd_id).keys()
    print(jd_id)
    return (jd_id)




if __name__=='__main__':

    # 以下三行根据ID获取评论
    # productID = get_productID()
    # callback = get_callback(productID)
    # get_comments(productID, callback)

    # 以下四行通过输入关键字获取评论
    productID = get_id_by_keyword()
    for item in productID:
        #print(item)
        try:
            callback = get_callback(item)
            get_comments(item,callback)
        except:
            pass

