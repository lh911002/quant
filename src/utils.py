from jqdatasdk import *
import pandas
import datetime


def prepare() -> object:
    print('jqdatasdk init')
    auth('18616337370', '1qaz@WSX')
    print("当日API调用情况 {}".format(get_query_count()))





