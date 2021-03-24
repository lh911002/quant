from src.jq.utils import *
import math

def get_security_name(code):
    info = get_security_info(code)
    return info.display_name


# 连续4年利润增速百分之10以上
def strage1():
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
                    continue
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

def strage2():
    mkdir("output/平均利润低估")
    stocks = get_all_securities(['stock'])
    df_result = pandas.DataFrame(None, None, ['代码', '名称', '当前市值(亿元)', '目标市值(亿元)', '目标估值', '近年平均利润(亿元)', '加权年数'], None, False)
    for stock_index in range(len(stocks)):
        print("当前进度：{}".format(stock_index/len(stocks)))
        stock_item = stocks.iloc[stock_index]
        q = query(finance.STK_INCOME_STATEMENT.company_name,
                  finance.STK_INCOME_STATEMENT.code,
                  finance.STK_INCOME_STATEMENT.end_date,
                  finance.STK_INCOME_STATEMENT.total_operating_revenue,
                  finance.STK_INCOME_STATEMENT.np_parent_company_owners).filter(
            finance.STK_INCOME_STATEMENT.code == stock_item.name,
            finance.STK_INCOME_STATEMENT.end_date >= '2015-01-01',
            finance.STK_INCOME_STATEMENT.report_type == 0).order_by(finance.STK_INCOME_STATEMENT.end_date).limit(100)
        df_finance = finance.run_query(q)
        last_income = 0  # 去年收入
        last_profit = 0  # 去年利润
        count = 0  #利润增长的年份
        first_year_profit = 0
        last_year_profit = 0
        max_year_profit =0
        min_year_profit =0
        average_profit = 0  # 近几年平均利润
        years_count = 0
        years_profit = 0
        for index in range(len(df_finance)):
            item = df_finance.iloc[index]
            if item.end_date.month == 12:  # 年报数据
                years_count = years_count+1
                years_profit = years_profit + item.np_parent_company_owners
                if years_count == 1:
                    max_year_profit = item.np_parent_company_owners
                    min_year_profit = item.np_parent_company_owners
                else:
                    if item.np_parent_company_owners > max_year_profit:
                        max_year_profit = item.np_parent_company_owners
                    if item.np_parent_company_owners < min_year_profit:
                        min_year_profit = item.np_parent_company_owners

                if last_income == 0:
                    last_income = item.total_operating_revenue  # 去年收入
                    last_profit = item.np_parent_company_owners  # 去年利润
                    first_year_profit = item.np_parent_company_owners
                    continue

                last_year_profit = item.np_parent_company_owners

                income_percent = item.total_operating_revenue / last_income - 1
                profit_percent = item.np_parent_company_owners / last_profit - 1
                last_income = item.total_operating_revenue  # 去年收入
                last_profit = item.np_parent_company_owners  # 去年利润
                if profit_percent <= 0.00:
                    continue
                else:
                    count = count + 1
        if years_count <= 1 or last_year_profit <= 0:
            continue

        if first_year_profit > 0:
            change_one_year = math.pow(last_year_profit/first_year_profit, 1/years_count)-1
            average_profit = years_profit / years_count
            if change_one_year <= 0:  # 过滤几年利润都未增长的
                continue
            target_pe = 5 + change_one_year * 100
            # if change_one_year < 0.06:
            #     target_pe = 6
            # elif change_one_year < 0.10:
            #     target_pe = 10

            target_market_value = last_year_profit * target_pe
            df = get_fundamentals(query(
                valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
                indicator.inc_total_revenue_year_on_year
            ).filter(
                valuation.market_cap <= (target_market_value / 100000000) * 0.7,  #比合理估值略低具有买入价值
                valuation.code == stock_item.name
            ), datetime.date.today() - datetime.timedelta(1))

            if len(df) > 0 and (max_year_profit * 0.8 + min_year_profit) > 0 and average_profit >= 200000000 and (years_count - count) <= 2:
                result_item = pandas.Series({'代码': item.code})
                result_item['名称'] = get_security_name(item.code)
                result_item['当前市值(亿元)'] = df.iloc[0].market_cap
                result_item['目标市值(亿元)'] = target_market_value / 100000000
                result_item['近年平均利润(亿元)'] = average_profit / 100000000
                result_item['加权年数'] = years_count
                result_item['目标估值'] = target_pe
                df_result.loc[df_result.index.size] = result_item
    df_result.to_csv("output/平均利润低估/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')
