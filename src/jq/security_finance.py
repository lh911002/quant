from src.jq.utils import *


def get_security_name(code):
    info = get_security_info(code)
    return info.display_name


# 连续4年利润增速百分之10以上
def strage():
    mkdir("output/全A业绩持续增长")
    stocks = get_all_securities(['stock'])
    df_result = pandas.DataFrame(None, None, ['股票代码', '股票名称', '2019年报利润(亿元）'], None, False)
    for stock_index in range(len(stocks)):
        stock_item = stocks.iloc[stock_index]
        q = query(finance.STK_INCOME_STATEMENT.company_name,
                  finance.STK_INCOME_STATEMENT.code,
                  finance.STK_INCOME_STATEMENT.end_date,
                  finance.STK_INCOME_STATEMENT.total_operating_revenue,
                  finance.STK_INCOME_STATEMENT.np_parent_company_owners).filter(
            finance.STK_INCOME_STATEMENT.code == stock_item.name,
            finance.STK_INCOME_STATEMENT.end_date >= '2014-01-01',
            finance.STK_INCOME_STATEMENT.report_type == 0).order_by(finance.STK_INCOME_STATEMENT.end_date).limit(100)
        df_finance = finance.run_query(q)
        last_income = 0  # 去年收入
        last_profit = 0  # 去年利润
        count = 0
        last_year_profit = 0
        for index in range(len(df_finance)):
            item = df_finance.iloc[index]
            if item.end_date.month == 12:  # 年报数据
                if last_income == 0:
                    last_income = item.total_operating_revenue  # 去年收入
                    last_profit = item.np_parent_company_owners  # 去年利润
                    continue

                income_percent = item.total_operating_revenue / last_income - 1
                profit_percent = item.np_parent_company_owners / last_profit - 1
                last_income = item.total_operating_revenue  # 去年收入
                last_profit = item.np_parent_company_owners  # 去年利润
                if income_percent <= 0.15:
                    break
                else:
                    count = count + 1
                    last_year_profit = item.np_parent_company_owners
        if count >= 5 and last_year_profit >= 500000000:
            result_item = pandas.Series({'股票代码': item.code})
            result_item['股票名称'] = get_security_name(item.code)
            result_item['2019年报利润(亿元）'] = last_year_profit / 100000000
            df_result.loc[df_result.index.size] = result_item
    # df_result.sort_values("2019年报利润(亿元）", ascending=False).to_csv("output/全A业绩持续增长/{}.csv".format(datetime.date.today()))
    df_result.to_csv("output/全A业绩持续增长/{}.csv".format(datetime.date.today()))
