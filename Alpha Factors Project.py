# ============================================================
# MFE5210 Alpha Factors Project
# Data Source: BaoStock
# ============================================================

import baostock as bs
import pandas as pd
import numpy as np

# ============================================================
# 1. 登录 BaoStock
# ============================================================

lg = bs.login()

print("login respond error_code:" + lg.error_code)
print("login respond error_msg:" + lg.error_msg)

# ============================================================
# 2. 下载股票数据
# ============================================================

def get_multi_stock_data(
        codes,
        start_date="2023-01-01",
        end_date="2025-05-15"):

    all_data = []

    for code in codes:


        rs = bs.query_history_k_data_plus(
            code=code,
            fields="date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"
        )

        df = rs.get_data()

        if df.empty:
            print(f"{code} no data")
            continue

        # 数据类型转换
        df = df.astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        })

        df["date"] = pd.to_datetime(df["date"])
        df["code"] = code

        all_data.append(df)

    df_all = pd.concat(all_data, ignore_index=True)

    df_all = df_all.sort_values(
        ["code", "date"]
    ).reset_index(drop=True)

    print(f"Total records: {len(df_all)}")

    return df_all


# ============================================================
# 3. 收益率计算
# ============================================================

def calculate_returns(df):

    # 日收益率
    df["ret_1d"] = (
        df.groupby("code")["close"]
        .pct_change()
    )

    # 未来5日收益率（Forward Return）
    df["fwd_ret_5d"] = (
        df.groupby("code")["close"]
        .shift(-5) / df["close"] - 1
    )

    # 用于 Decay
    for d in [1,3,5,10,20]:
        df[f"fwd_ret_{d}d"] = df.groupby("code")["close"].shift(-d) / df["close"] - 1

    return df


# ============================================================
# 4. 构建 Alpha 因子
# ============================================================

def build_alpha_factors(df):

    # --------------------------------------------------------
    # F1: 5日动量因子
    # --------------------------------------------------------
    df["F1_MOM5"] = (
        df.groupby("code")["ret_1d"]
        .rolling(5)
        .sum()
        .reset_index(0, drop=True)
    )

    # --------------------------------------------------------
    # F2: 成交量放大量因子
    # --------------------------------------------------------
    vol_ma5 = (
        df.groupby("code")["volume"]
        .rolling(5)
        .mean()
        .reset_index(0, drop=True)
    )

    vol_ma20 = (
        df.groupby("code")["volume"]
        .rolling(20)
        .mean()
        .reset_index(0, drop=True)
    )

    df["F2_VOL_SPIKE"] = (
        vol_ma5 / vol_ma20 - 1
    )

    # --------------------------------------------------------
    # F3: 成交量变化率因子
    # --------------------------------------------------------
    df["F3_VOL_CHANGE"] = (
        df.groupby("code")["volume"]
        .pct_change(5)
    )

    # --------------------------------------------------------
    # F4: 20日Rank Momentum
    # --------------------------------------------------------
    df["F4_RANK_MOM"] = (
        df.groupby("code")["ret_1d"]
        .rolling(20)
        .mean()
        .reset_index(0, drop=True)
    )

    # --------------------------------------------------------
    # F5: 成交量波动率
    # --------------------------------------------------------
    df["F5_VOL_VOLATILITY"] = (
        df.groupby("code")["volume"]
        .rolling(10)
        .std()
        .reset_index(0, drop=True)
    )

    # ========================================================
    # 因子列表
    # ========================================================

    factor_cols = [
        "F1_MOM5",
        "F2_VOL_SPIKE",
        "F3_VOL_CHANGE",
        "F4_RANK_MOM",
        "F5_VOL_VOLATILITY"
    ]

    # ========================================================
    # 去极值 + 截面标准化
    # ========================================================

    for f in factor_cols:

        # 去极值
        lower = df[f].quantile(0.01)
        upper = df[f].quantile(0.99)

        df[f] = df[f].clip(lower, upper)

        # 截面标准化
        df[f] = (
            df.groupby("date")[f]
            .transform(lambda x: (x - x.mean()) / x.std())
        )

    return df, factor_cols


# ============================================================
# 5. 自动筛选低相关因子
# ============================================================

def select_low_corr_factors(df, factor_cols, threshold=0.5):
    corr_mat = df[factor_cols].corr().abs()
    selected = []
    for f in factor_cols:
        keep = True
        for sf in selected:
            if corr_mat.loc[f, sf] > threshold:
                keep = False
                break
        if keep:
            selected.append(f)
    return selected


# ============================================================
# 6. 计算 IC Sharpe (ICIR)
# ============================================================

def calculate_ic_sharpe(df, factor_cols, freq=252):
    result = []
    for f in factor_cols:
        ic_series = (
            df.groupby("date")
            .apply(lambda x: x[f].corr(x["fwd_ret_5d"], method="spearman"))
            .dropna()
        )
        if len(ic_series) < 20:
            ic_mean = np.nan
            ic_std = np.nan
            sharpe = np.nan
        else:
            ic_mean = ic_series.mean()
            ic_std = ic_series.std()
            sharpe = (ic_mean / ic_std) * np.sqrt(freq) if ic_std != 0 else 0
        result.append([f, round(ic_mean,4), round(ic_std,4), round(sharpe,4)])
    result_df = pd.DataFrame(result, columns=["Factor","IC Mean","IC Std","IC Sharpe (ICIR)"])
    return result_df


# ============================================================
# 7. IC Decay 因子衰减
# ============================================================

def calculate_ic_decay(df, factor_cols):
    decay = []
    forward_days = [1,3,5,10,20]
    for f in factor_cols:
        row = {"Factor": f}
        for d in forward_days:
            ic = df.groupby("date").apply(
                lambda x: x[f].corr(x[f"fwd_ret_{d}d"], method="spearman")
            ).mean()
            row[f"IC_{d}d"] = round(ic,4)
        decay.append(row)
    return pd.DataFrame(decay)


# ============================================================
# 8. 分组收益单调性
# ============================================================

def factor_monotonicity(df, factor_cols, n_groups=5):
    mono_result = []
    for f in factor_cols:
        df["group"] = df.groupby("date")[f].transform(
            lambda x: pd.qcut(x, n_groups, labels=False, duplicates='drop')
        )
        group_ret = df.groupby("group")["fwd_ret_5d"].mean()
        diff = group_ret.diff().dropna()
        is_up = all(diff > -0.0001)
        is_down = all(diff < 0.0001)
        mono = "Up" if is_up else ("Down" if is_down else "Non-monotonic")
        gr = [round(group_ret[i],4) for i in range(n_groups)]
        mono_result.append([f, mono, gr])
    return pd.DataFrame(mono_result, columns=["Factor","Monotonicity","GroupReturns"])


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":

    stock_codes = [
        "sz.000001","sz.000002","sz.000063","sz.000100","sz.000157",
        "sz.000333","sz.000651","sz.000725","sz.000768","sz.000858",
        "sz.002230","sz.002415","sz.002594","sz.002714","sz.002938",
        "sz.300015","sz.300059","sz.300122","sz.300308","sz.300750",
        "sh.600000","sh.600009","sh.600036","sh.600050","sh.600104",
        "sh.600276","sh.600309","sh.600519","sh.600690","sh.600809",
        "sh.601012","sh.601166","sh.601318","sh.601398","sh.601688",
        "sh.601888","sh.601899","sh.603259","sh.603288","sh.603501"
    ]

    df = get_multi_stock_data(stock_codes)
    df = calculate_returns(df)
    df, factor_cols = build_alpha_factors(df)
    df = df.dropna().reset_index(drop=True)
    print("Data Ready")

    selected_factors = select_low_corr_factors(df, factor_cols, threshold=0.5)
    print("\n===================================")
    print("Selected Factors")
    print("===================================")
    print(selected_factors)

    corr_mat = df[selected_factors].corr()
    print("\n===================================")
    print("Correlation Matrix")
    print("===================================")
    print(corr_mat.round(3))

    sharpe_df = calculate_ic_sharpe(df, selected_factors)
    print("\n===================================")
    print("IC Sharpe (ICIR)")
    print("===================================")
    print(sharpe_df)

    avg_sharpe = sharpe_df["IC Sharpe (ICIR)"].mean()
    print("\n===================================")
    print("Average IC Sharpe (No Cost)")
    print("===================================")
    print(round(avg_sharpe,4))

    upper = corr_mat.where(np.triu(np.ones(corr_mat.shape), k=1).astype(bool))
    max_corr = upper.max().max()
    print("\n===================================")
    print("Max Correlation")
    print("===================================")
    print(round(max_corr,4))


    # ==============================
    decay_df = calculate_ic_decay(df, selected_factors)
    print("\n===================================")
    print("IC Decay (Factor Decay)")
    print("===================================")
    print(decay_df)


    # ==============================
    mono_df = factor_monotonicity(df, selected_factors)
    print("\n===================================")
    print("Monotonicity (5 Groups)")
    print("===================================")
    print(mono_df)

bs.logout()