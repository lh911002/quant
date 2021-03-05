from jqdatasdk import *
import os
import pandas
import datetime


def prepare() -> object:
    print('jqdatasdk init')
    auth('18616337370', '1qaz@WSX')
    print("当日API调用情况 {}".format(get_query_count()))

def mkdir(path) ->object:
    # 去除首位空格
    path = path.strip()
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False




