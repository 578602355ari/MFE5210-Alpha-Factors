# ============================================================
# MFE5210 Alpha Factors Project
# FINAL SUBMISSION VERSION
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

        print(f"Downloading {code} ...")

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

    print(f"\n✅ Total records: {len(df_all)}")

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
            .transform(
                lambda x: (
                    x - x.mean()
                ) / x.std()
            )
        )

    return df, factor_cols


# ============================================================
# 5. 自动筛选低相关因子
# ============================================================

def select_low_corr_factors(
        df,
        factor_cols,
        threshold=0.5):

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
# 6. 计算 IC Sharpe
# 使用 Spearman Rank IC
# ============================================================

def calculate_ic_sharpe(
        df,
        factor_cols,
        freq=252):

    result = []

    for f in factor_cols:

        ic_series = (
            df.groupby("date")
            .apply(
                lambda x: x[f].corr(
                    x["fwd_ret_5d"],
                    method="spearman"
                )
            )
            .dropna()
        )

        if len(ic_series) < 20:

            ic_mean = np.nan
            ic_std = np.nan
            sharpe = np.nan

        else:

            ic_mean = ic_series.mean()
            ic_std = ic_series.std()

            if ic_std == 0:
                sharpe = 0
            else:
                sharpe = (
                    ic_mean / ic_std
                ) * np.sqrt(freq)

        result.append([
            f,
            round(ic_mean, 4),
            round(ic_std, 4),
            round(sharpe, 4)
        ])

    result_df = pd.DataFrame(
        result,
        columns=[
            "Factor",
            "IC Mean",
            "IC Std",
            "IC Sharpe"
        ]
    )

    return result_df


# ============================================================
# 7. 主程序
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # 股票池（40只A股）
    # ========================================================

    stock_codes = [

        # 深市
        "sz.000001",
        "sz.000002",
        "sz.000063",
        "sz.000100",
        "sz.000157",
        "sz.000333",
        "sz.000651",
        "sz.000725",
        "sz.000768",
        "sz.000858",

        "sz.002230",
        "sz.002415",
        "sz.002594",
        "sz.002714",
        "sz.002938",

        "sz.300015",
        "sz.300059",
        "sz.300122",
        "sz.300308",
        "sz.300750",

        # 沪市
        "sh.600000",
        "sh.600009",
        "sh.600036",
        "sh.600050",
        "sh.600104",

        "sh.600276",
        "sh.600309",
        "sh.600519",
        "sh.600690",
        "sh.600809",

        "sh.601012",
        "sh.601166",
        "sh.601318",
        "sh.601398",
        "sh.601688",

        "sh.601888",
        "sh.601899",
        "sh.603259",
        "sh.603288",
        "sh.603501"
    ]

    # ========================================================
    # 下载数据
    # ========================================================

    df = get_multi_stock_data(stock_codes)

    # ========================================================
    # 收益率
    # ========================================================

    df = calculate_returns(df)

    # ========================================================
    # Alpha 因子
    # ========================================================

    df, factor_cols = build_alpha_factors(df)

    # ========================================================
    # 删除缺失值
    # ========================================================

    df = df.dropna().reset_index(drop=True)

    print("\n✅ Data Ready")

    # ========================================================
    # 自动筛选低相关因子
    # ========================================================

    selected_factors = select_low_corr_factors(
        df,
        factor_cols,
        threshold=0.5
    )

    print("\n===================================")
    print("Selected Factors")
    print("===================================")

    print(selected_factors)

    # ========================================================
    # 相关矩阵
    # ========================================================

    corr_mat = df[selected_factors].corr()

    print("\n===================================")
    print("Correlation Matrix")
    print("===================================")

    print(corr_mat.round(3))

    # ========================================================
    # IC Sharpe
    # ========================================================

    sharpe_df = calculate_ic_sharpe(
        df,
        selected_factors
    )

    print("\n===================================")
    print("IC Sharpe Result")
    print("===================================")

    print(sharpe_df)

    # ========================================================
    # 平均 IC Sharpe
    # ========================================================

    avg_sharpe = sharpe_df[
        "IC Sharpe"
    ].mean()

    print("\n===================================")
    print("Average IC Sharpe")
    print("===================================")

    print(round(avg_sharpe, 4))

    # ========================================================
    # 最大相关系数
    # ========================================================

    upper = corr_mat.where(
        np.triu(
            np.ones(corr_mat.shape),
            k=1
        ).astype(bool)
    )

    max_corr = upper.max().max()

    print("\n===================================")
    print("Max Correlation")
    print("===================================")

    print(round(max_corr, 4))

# ============================================================
# 8. 登出
# ============================================================

bs.logout()