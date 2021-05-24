from src.jq.utils import *


def print_all_securities():
    stocks = get_all_securities(['stock'])
    print(len(stocks))


def get_security_name(code):
    info = get_security_info(code)
    print(info)
    return info.display_name


# 周k级别策略，200亿以上，毛利>20 调整幅度比较大的股票，且最近几周未破新低
def strage1():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 100,
        valuation.pe_ratio > 0,  # 盈利
        valuation.pe_ratio < 100,  # 盈利
    ), datetime.date.today() - datetime.timedelta(1))

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'price', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 100, '1w', ['date', 'open', 'high', 'low', 'close'], True,
                           datetime.date.today() + datetime.timedelta(1),
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
        if bar_last.close >= 5 and (high - low_after_high) / high > 0.40 and (len(df_bars) - low_after_high_idx) >= 8 and 0.05 < (
                bar_last.close - low_after_high) / low_after_high < 0.40:
            item['display_name'] = get_security_name(item.code)
            item['price'] = bar_last.close
            item['high'] = high
            item['low'] = low_after_high
            df_securities.loc[df_securities.index.size] = item

    print("共有{}个股票满足条件".format(len(df_securities)))
    mkdir("output/1-周线止跌横盘（每周更新）")
    df_securities.to_csv("output/1-周线止跌横盘（每周更新）/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')


# 周线级别向好
def strage2():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 100,
    ), datetime.date.today() - datetime.timedelta(1))

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'price', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 80, '1w', ['date', 'open', 'high', 'low', 'close'], True,
                           datetime.date.today() + datetime.timedelta(1),
                           datetime.datetime.now(), True)  # 近一年k线前复权

        high = 0  # 最高价
        high_idx = 0
        for bar_idx in range(len(df_bars)):
            bar_item = df_bars.iloc[bar_idx]
            if high <= bar_item.high:
                high = bar_item.high
                high_idx = bar_idx
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
        # 调整幅度>30% 最近4根周k线未破新低，距离最低点涨幅<16%
        if ((high - low_after_high) / high > 0.35 and len(df_bars) - low_after_high_idx) >= 8 and 0 < (
                bar_last.close - low_after_high) / low_after_high < 0.18:
            flag = 1
            pre_item_high = df_bars.iloc[len(df_bars)-3].high
            pre_item_low = df_bars.iloc[len(df_bars)-3].low
            for idx2 in range(low_after_high_idx, len(df_bars)):
                bar_item = df_bars.iloc[idx2]
                # 最近两根k线底部不断抬高
                if idx2 >= len(df_bars) - 2 and bar_item.low <= pre_item_low:
                    flag = 0
                # 最新涨幅不能过大
                if idx2 == len(df_bars) - 1 and (bar_item.close - bar_item.open)/bar_item.open > 0.04:
                    flag = 0
                pre_item_high = bar_item.high
                pre_item_low = bar_item.low

            if flag == 1:
                item['display_name'] = get_security_name(item.code)
                item['price'] = bar_last.close
                item['high'] = high
                item['low'] = low_after_high
                df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    mkdir("output/2-周线蓄势待发（每周更新）")
    df_securities.to_csv("output/2-周线蓄势待发（每周更新）/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')


# 旗形：大阳线后横盘几日，逢低买入
def strage3():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap >= 50,
        indicator.gross_profit_margin > 10,
        valuation.pe_ratio > 0,  # 盈利
        valuation.pe_ratio < 50,  # 盈利
    ), datetime.date.today() - datetime.timedelta(1))

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'price'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 150, '1d', ['date', 'open', 'high', 'low', 'close'], True,
                           datetime.date.today() + datetime.timedelta(1),
                           datetime.datetime.now(), True)  # 近一年k线前复权

        high = 0  # 最高价
        high_idx = 0
        low = 100000  # 最低价
        low_idx = 0
        for bar_idx in range(len(df_bars)):
            bar_item = df_bars.iloc[bar_idx]
            if high < bar_item.high:
                high = bar_item.high
                high_idx = bar_idx
            if low > bar_item.low:
                low = bar_item.low
                low_idx = bar_idx

        low_after_high = 100000  # 最高价以后的最低价
        low_after_high_idx = 0
        for idx1 in range(high_idx, len(df_bars)):
            bar_item = df_bars.iloc[idx1]
            if low_after_high > bar_item.low:
                low_after_high = bar_item.low
                low_after_high_idx = idx1

        last_increase_bar_idx = 0  # 近期大阳线位置
        last_increase_bar_percent = 0  # 近期大阳线涨幅
        for bar_idx in range(len(df_bars)-1, -1, -1):
            bar_item = df_bars.iloc[bar_idx]
            pre_bar_item = df_bars.iloc[bar_idx-1]
            change = (bar_item.close - pre_bar_item.close)/pre_bar_item.close
            if change >= 0.04:
                last_increase_bar_idx = bar_idx
                last_increase_bar_percent = change
                break
        if 1 <= (len(df_bars) - last_increase_bar_idx) <= 5: # 近期出现大阳线，趁着热乎
            last_increase_bar = df_bars.iloc[last_increase_bar_idx]
            bar_last = df_bars.iloc[len(df_bars) - 1]
            change_from_last_increase_bar = (bar_last.close - last_increase_bar.close)/last_increase_bar.close
            if -last_increase_bar_percent * 0.9 <= change_from_last_increase_bar <= last_increase_bar_percent * 0.3 \
                    and (high - low_after_high) / high >= 0.37 \
                    and (len(df_bars) - low_after_high_idx) >= 3 \
                    and 0.04 <= (bar_last.close - low_after_high) / low_after_high <= 0.25:
                item['display_name'] = get_security_name(item.code)
                item['price'] = bar_last.close
                df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    mkdir("output/3-旗形（每日）")
    df_securities.to_csv("output/3-旗形（每日）/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')

#月线反转机会
def strage4():
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap > 100,
        indicator.gross_profit_margin > 20,
    ), datetime.date.today() - datetime.timedelta(1))

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name', 'price', 'high', 'low'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, 40, '1M', ['date', 'open', 'high', 'low', 'close'], True,
                           datetime.date.today() + datetime.timedelta(1),
                           datetime.datetime.now(), True)  # 近一年k线前复权

        if len(df_bars) < 12:
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
        for idx1 in range(high_idx+1, len(df_bars)):
            bar_item = df_bars.iloc[idx1]
            if low_after_high < bar_item.low:
                low_after_high = low_after_high
            else:
                low_after_high = bar_item.low
                low_after_high_idx = idx1
        bar_last = df_bars.iloc[len(df_bars) - 1]
        change_from_high = (high - low_after_high) / high
        if change_from_high > 0.40 and 6 <= (len(df_bars) - low_after_high_idx) <= 12 and change_from_high * 0.1 < (
                bar_last.close - low_after_high) / low_after_high < change_from_high * 0.666:
            item['display_name'] = get_security_name(item.code)
            item['price'] = bar_last.close
            item['high'] = high
            item['low'] = low_after_high
            df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    mkdir("output/4-月线反转机会（每月更新）")
    df_securities.to_csv("output/4-月线反转机会（每月更新）/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')


# 连续x日以上下跌，企稳以后做反弹
def strage5(count):
    df = get_fundamentals(query(
        valuation.code, valuation.market_cap, valuation.pe_ratio, income.total_operating_revenue,
        indicator.inc_total_revenue_year_on_year
    ).filter(
        valuation.market_cap >= 50,
        valuation.pe_ratio > 0,  # 盈利
        valuation.pe_ratio < 50,  # 盈利
    ), datetime.date.today() - datetime.timedelta(1))

    df_securities = pandas.DataFrame(None, None, ['code', 'display_name'], None, False)
    for index in range(len(df)):
        item = df.iloc[index]
        df_bars = get_bars(item.code, count*2, '1d', ['date', 'open', 'high', 'low', 'close'], True,
                           datetime.date.today() + datetime.timedelta(1),
                           datetime.datetime.now(), True)  # 近一年k线前复权

        first_increse_index = len(df_bars)-1
        for bar_idx in range(len(df_bars)-1, -1, -1):
            bar_item = df_bars.iloc[bar_idx]
            pre_bar_item = df_bars.iloc[bar_idx-1]
            change = (bar_item.close - pre_bar_item.close)/pre_bar_item.close
            if change > 0.00 or bar_item.close > bar_item.open:
                first_increse_index = bar_idx
                break

        if len(df_bars)-1 - first_increse_index >=count: # 近期出现大阳线，趁着热乎
            item['display_name'] = get_security_name(item.code)
            df_securities.loc[df_securities.index.size] = item
    print("共有{}个股票满足条件".format(len(df_securities)))
    mkdir("output/5-连续下跌，做企稳反弹（每日）")
    df_securities.to_csv("output/5-连续下跌，做企稳反弹（每日）/{}.csv".format(datetime.date.today()), index=False, encoding='utf-8', float_format='%.1f')


