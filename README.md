# MFE5210 Alpha Factors Project

---

## 1. Project Overview
This project develops **5 price-volume-based alpha factors** for Chinese A-share stocks, using daily data from BaoStock. The full pipeline includes data acquisition, factor construction, correlation screening, and performance evaluation.

- **Data Source**: BaoStock (Chinese A-share daily OHLCV data)
- **Factor Type**: Cross-sectional, daily-frequency, long-short compatible
- **Correlation Control**: Max absolute correlation ≤ 0.5
- **Evaluation Metric**: Spearman rank IC and IC Sharpe ratio (without transaction cost)

---

## 2. Alpha Factors
The 5 factors built in the code are:
1. **F1_MOM5**: 5-day momentum (sum of daily returns over 5 trading days)
2. **F2_VOL_SPIKE**: Volume spike ratio (5-day moving average volume / 20-day moving average volume - 1)
3. **F3_VOL_CHANGE**: 5-day percentage change in volume
4. **F4_RANK_MOM**: 20-day momentum (average daily returns over 20 trading days)
5. **F5_VOL_VOLATILITY**: 10-day rolling standard deviation of volume

---

## 3. Data & Preprocessing
- **Stock Universe**: 40 large-cap A-share stocks
- **Time Period**: 2023-01-01 to 2025-05-15
- **Preprocessing Steps**:
  1. Winsorization: Clip values at 1st and 99th percentiles
  2. Cross-sectional standardization (daily z-score)
  3. Drop rows with missing values

---

## 4. Key Outputs (Matching Assignment Requirements)

### 4.1 Selected Factors
All 5 factors passed the low-correlation filter (max absolute correlation ≤ 0.5):
`['F1_MOM5', 'F2_VOL_SPIKE', 'F3_VOL_CHANGE', 'F4_RANK_MOM', 'F5_VOL_VOLATILITY']`

---

### 4.2 Correlation Matrix
|                   | F1_MOM5 | F2_VOL_SPIKE | F3_VOL_CHANGE | F4_RANK_MOM | F5_VOL_VOLATILITY |
|-------------------|---------|--------------|---------------|-------------|-------------------|
| F1_MOM5           | 1.000   | 0.243        | 0.210         | 0.474       | 0.075             |
| F2_VOL_SPIKE      | 0.243   | 1.000        | 0.411         | 0.120       | 0.134             |
| F3_VOL_CHANGE     | 0.210   | 0.411        | 1.000         | 0.042       | 0.045             |
| F4_RANK_MOM       | 0.474   | 0.120        | 0.042         | 1.000       | 0.124             |
| F5_VOL_VOLATILITY | 0.075   | 0.134        | 0.045         | 0.124       | 1.000             |

- **Max Correlation**: 0.4739 (between F1_MOM5 and F4_RANK_MOM), which is ≤ 0.5 as required.

---

### 4.3 Factor Performance (IC & IC Sharpe)
| Factor              | IC Mean | IC Std  | IC Sharpe |
|---------------------|---------|---------|-----------|
| F1_MOM5             | 0.0182  | 0.2339  | 1.2366    |
| F2_VOL_SPIKE        | 0.0091  | 0.2034  | 0.7103    |
| F3_VOL_CHANGE       | 0.0039  | 0.1966  | 0.3135    |
| F4_RANK_MOM         | 0.0164  | 0.2467  | 1.0580    |
| F5_VOL_VOLATILITY   | 0.0219  | 0.2164  | 1.6068    |

---

### 4.4 Average Sharpe Ratio for All Alpha Factors (Without Transaction Cost)
The assignment requires the average performance of all alpha factors without considering transaction costs. We use the **average IC Sharpe ratio** as the measure:

- **Average IC Sharpe**: 0.985
- This is the arithmetic mean of the IC Sharpe ratios of the 5 selected factors, directly corresponding to the "Average Sharpe ratio for all alpha factors (without cost)" in the assignment requirements.

---

## 5. How to Run
1. Install required packages:
pip install baostock pandas numpy
2. Run the script:
Alpha Factors Project
3. The terminal will print all required outputs for the assignment:
- Data loading status
- Selected factors list
- Correlation matrix
- IC Sharpe results for each factor
- Average IC Sharpe ratio
- Maximum correlation coefficient
