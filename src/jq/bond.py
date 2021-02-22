# 债券
from src.jq.utils import *


# 可转债
def strage1():
    df = bond.run_query(query(bond.CONBOND_DAILY_PRICE).filter(bond.CONBOND_DAILY_PRICE.date == '2021-02-08',
                                                               bond.CONBOND_DAILY_PRICE.close <= 90).limit(5000))
    print("当前价格小于90的可转债数目：{}".format(len(df)))
    # df_result = pandas.DataFrame(None, None, ['code', 'name', 'price', 'convert_premium_rate'], None, False)
    # for index in range(len(df)):
    #     item = df.iloc[index]
    #     df_filter_convert = bond.run_query(
    #         query(bond.CONBOND_DAILY_CONVERT).filter(bond.CONBOND_DAILY_CONVERT.date == '2021-02-09',
    #                                                  bond.CONBOND_DAILY_CONVERT.code == item.code).limit(5000))
    #     if df_filter_convert is not None and len(df_filter_convert) > 0:
    #         result = df_filter_convert.iloc[0]
    #         result['price'] = item.close
    #         df_result.loc[df_result.index.size] = result
    df = df.drop(['id', 'date', 'exchange_code', 'pre_close', 'open', 'high', 'low'], 1)
    df.to_csv("output/可转债.csv")
