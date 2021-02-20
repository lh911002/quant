from utils import *


def print_all_securities():
    stocks = get_all_securities(['stock'])
    print(len(stocks))


def get_security_name(code):
    info = get_security_info(code)
    print(info)
    return info.display_name


# 获取市值>100亿元 PEG<1,且最近三周股价是上涨的股票
def strage1():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 100,  # 市值 >100亿元
        valuation.pe_ratio > 0,  # 盈利
        indicator.inc_total_revenue_year_on_year > 0,  # 营收增长
        valuation.pe_ratio / indicator.inc_total_revenue_year_on_year < 1  # PEG < 1
    ), '2021-02-05')

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 100, '1w', ['date', 'open', 'high', 'low', 'close'], True, '2021-02-06',
                           datetime.datetime.now(), True)  # 近两年k线

        bar_last = df_bars.iloc[len(df_bars) - 1]
        bar_third_last = df_bars.iloc[len(df_bars) - 3]
        if bar_last.close > bar_third_last.close and (
                bar_last.close - bar_third_last.close) / bar_third_last.close < 0.05:
            item['display_name'] = get_security_name(item.code)
            df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    df_securities.to_csv("output/securities.csv")


# 市值>200亿元 ， 最近调整百分之40以上, 且已经3周不破新低,且涨幅相对低点百分之15以内
def strage2():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 100,  # 市值 >200亿元
    ), '2021-02-05')

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 50, '1w', ['date', 'open', 'high', 'low', 'close'], True, '2021-02-06',
                           datetime.datetime.now(), True)  # 近一年k线前复权

        high = 0  # 最高价
        high_idx = 0
        low = 100000  # 最低价
        low_idx = 0
        for bar_idx in range(len(df_bars)):
            bar_item = df_bars.iloc[bar_idx]
            if high > bar_item.high:
                high = high
            else:
                high = bar_item.high
                high_idx = bar_idx
            if low < bar_item.low:
                low = low
            else:
                low = bar_item.low
                low_idx = bar_idx
        low_after_high = 100000  # 最高价以后的最低价
        low_after_high_idx = 0
        for idx1 in range(high_idx, len(df_bars)):
            bar_item = df_bars.iloc[idx1]
            if low_after_high < bar_item.low:
                low_after_high = low_after_high
            else:
                low_after_high = bar_item.low
                low_after_high_idx = idx1
        high_after_low = 0
        high_after_low_idx = 0
        for idx2 in range(low_after_high_idx, len(df_bars)):
            bar_item = df_bars.iloc[idx2]
            if high_after_low > bar_item.high:
                high_after_low = high_after_low
            else:
                high_after_low = bar_item.high
                high_after_low_idx = idx2
        if (df_bars.iloc[high_after_low_idx].high - low_after_high) / low_after_high < 0.3:  # 在最低价后股价没有重新大涨（防止二次探顶）
            bar_last = df_bars.iloc[len(df_bars) - 1]
            if ((high - bar_last.close) / high > 0.4 and len(df_bars) - low_after_high_idx) > 4 and 0.05 < (
                    bar_last.close - low_after_high) / low_after_high < 0.15:
                item['display_name'] = get_security_name(item.code)
                item['high'] = high
                item['low'] = low_after_high
                df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    df_securities.to_csv("output/securities2.csv")


# 150亿以上，毛利>20 调整幅度比较大的股票，且最近几周未破新低
def strage3():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 150,
        indicator.gross_profit_margin > 20
    ), '2021-02-19')

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 50, '1w', ['date', 'open', 'high', 'low', 'close'], True, '2021-02-19',
                           datetime.datetime.now(), True)  # 近一年k线前复权

        high = 0  # 最高价
        high_idx = 0
        low = 100000  # 最低价
        low_idx = 0
        for bar_idx in range(len(df_bars)):
            bar_item = df_bars.iloc[bar_idx]
            if high > bar_item.high:
                high = high
            else:
                high = bar_item.high
                high_idx = bar_idx
            if low < bar_item.low:
                low = low
            else:
                low = bar_item.low
                low_idx = bar_idx
        low_after_high = 100000  # 最高价以后的最低价
        low_after_high_idx = 0
        for idx1 in range(high_idx, len(df_bars)):
            bar_item = df_bars.iloc[idx1]
            if low_after_high < bar_item.low:
                low_after_high = low_after_high
            else:
                low_after_high = bar_item.low
                low_after_high_idx = idx1
        bar_last = df_bars.iloc[len(df_bars) - 1]
        if ((high - low_after_high) / high > 0.3 and len(df_bars) - low_after_high_idx) > 2 and 0.02 < (
                bar_last.close - low_after_high) / low_after_high < 0.12:
            item['display_name'] = get_security_name(item.code)
            item['high'] = high
            item['low'] = low_after_high
            df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    df_securities.to_csv("output/securities3.csv")


# 日k级别，大阳线回调买入策略
def strage4():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 150,
        indicator.gross_profit_margin > 20
    ), '2021-02-19')

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'price', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 150, '1d', ['date', 'open', 'high', 'low', 'close'], True, '2021-02-19',
                           datetime.datetime.now(), True)  # 近一年k线前复权

        if len(df_bars) < 100:
            continue
        high = 0  # 最高价
        high_idx = 0
        low = 100000  # 最低价
        low_idx = 0
        for bar_idx in range(len(df_bars)):
            bar_item = df_bars.iloc[bar_idx]
            if high > bar_item.high:
                high = high
            else:
                high = bar_item.high
                high_idx = bar_idx
            if low < bar_item.low:
                low = low
            else:
                low = bar_item.low
                low_idx = bar_idx
        low_after_high = 100000  # 最高价以后的最低价
        low_after_high_idx = 0
        for idx1 in range(high_idx, len(df_bars)):
            bar_item = df_bars.iloc[idx1]
            if low_after_high < bar_item.low:
                low_after_high = low_after_high
            else:
                low_after_high = bar_item.low
                low_after_high_idx = idx1
        bar_last = df_bars.iloc[len(df_bars) - 1]
        for idx2 in range(len(df_bars) - 1, len(df_bars) - 6, -1):
            bar_item = df_bars.iloc[idx2]
            pre_bar_item = df_bars.iloc[idx2 - 1]
            # 低点以后出现大阳线（涨幅>4%) 回落介入，且距离高点有空间
            if (low_after_high_idx <= idx2 and bar_item.close - pre_bar_item.close) / pre_bar_item.close > 0.04 and (
                    len(df_bars) - idx2 >= 2) and 0.0 < (bar_last.close - bar_item.low) / bar_item.low < 0.04 and (
                    high - bar_last.close) / high > 0.2:
                item['display_name'] = get_security_name(item.code)
                item['price'] = bar_last.close
                item['high'] = high
                item['low'] = low_after_high
                df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    df_securities.to_csv("output/securities4.csv")
