# MFE5210 Alpha Factors Project
Course Assignment Submission

---

## 1. Project Overview
This project develops 5 price-volume-based alpha factors for Chinese A-share stocks using daily data from BaoStock. The pipeline includes data acquisition, factor construction, correlation screening, and performance evaluation.

- Data Source: BaoStock (A-share daily OHLCV data)
- Factor Type: Cross-sectional, daily-frequency, long-short compatible
- Correlation Constraint: Max absolute correlation ≤ 0.5
- Evaluation: IC, IC Sharpe (ICIR), IC Decay, monotonicity, average Sharpe (without cost)

---

## 2. Alpha Factors
1. **F1_MOM5**: 5-day momentum (sum of 5-day returns)
2. **F2_VOL_SPIKE**: Volume spike (MA5 / MA20 − 1)
3. **F3_VOL_CHANGE**: 5-day percentage change of volume
4. **F4_RANK_MOM**: 20-day mean return momentum
5. **F5_VOL_VOLATILITY**: 10-day rolling standard deviation of volume

---

## 3. Data & Preprocessing
- Stock Universe: 40 large-cap A-share stocks
- Period: 2023-01-01 to 2025-05-15
- Winsorization: 1%–99%
- Cross-sectional daily standardization (z-score)
- Drop missing values

---

## 4. Key Results (Actual Run Output)

### 4.1 Selected Factors
All 5 factors passed the low-correlation filter:
`['F1_MOM5', 'F2_VOL_SPIKE', 'F3_VOL_CHANGE', 'F4_RANK_MOM', 'F5_VOL_VOLATILITY']`

---

### 4.2 Correlation Matrix
|                     | F1_MOM5 | F2_VOL_SPIKE | F3_VOL_CHANGE | F4_RANK_MOM | F5_VOL_VOLATILITY |
|---------------------|---------|--------------|---------------|-------------|-------------------|
| F1_MOM5             | 1.000   | 0.249        | 0.211         | 0.482       | 0.076             |
| F2_VOL_SPIKE        | 0.249   | 1.000        | 0.413         | 0.128       | 0.135             |
| F3_VOL_CHANGE       | 0.211   | 0.413        | 1.000         | 0.042       | 0.046             |
| F4_RANK_MOM         | 0.482   | 0.128        | 0.042         | 1.000       | 0.127             |
| F5_VOL_VOLATILITY   | 0.076   | 0.135        | 0.046         | 0.127       | 1.000             |

- **Max Correlation: 0.4821 ≤ 0.5** 

---

### 4.3 IC Sharpe (ICIR)
| Factor               | IC Mean | IC Std  | IC Sharpe (ICIR) |
|----------------------|---------|---------|------------------|
| F1_MOM5              | 0.0190  | 0.2348  | 1.2870           |
| F2_VOL_SPIKE         | 0.0127  | 0.2036  | 0.9906           |
| F3_VOL_CHANGE        | 0.0079  | 0.1951  | 0.6447           |
| F4_RANK_MOM          | 0.0237  | 0.2444  | 1.5367           |
| F5_VOL_VOLATILITY    | 0.0213  | 0.2183  | 1.5505           |

---

### 4.4 Average Sharpe Ratio for All Alpha Factors (Without Cost)
- **Average IC Sharpe: 1.2019**

---

### 4.5 IC Decay (Factor Predictability Decay)
| Factor               | IC_1d  | IC_3d  | IC_5d  | IC_10d | IC_20d |
|----------------------|--------|--------|--------|--------|--------|
| F1_MOM5              | -0.0101| 0.0098 | 0.0190 | 0.0120 | 0.0320 |
| F2_VOL_SPIKE         | 0.0014 | 0.0111 | 0.0127 | 0.0140 | 0.0040 |
| F3_VOL_CHANGE        | -0.0084| -0.0035| 0.0079 | 0.0006 | 0.0033 |
| F4_RANK_MOM          | 0.0057 | 0.0130 | 0.0237 | 0.0298 | 0.0473 |
| F5_VOL_VOLATILITY    | 0.0121 | 0.0158 | 0.0213 | 0.0280 | 0.0341 |

---

### 4.6 Monotonicity (5 Groups)
| Factor               | Monotonicity   | Group Returns                                  |
|----------------------|----------------|------------------------------------------------|
| F1_MOM5              | Up             | [-0.0006, 0.0006, 0.0005, 0.0013, 0.0026]      |
| F2_VOL_SPIKE         | Non-monotonic  | [0.0008, -0.0009, -0.0005, 0.0009, 0.0040]     |
| F3_VOL_CHANGE        | Non-monotonic  | [0.0008, 0.0001, 0.0014, 0.0013, 0.0007]       |
| F4_RANK_MOM          | Non-monotonic  | [-0.0011, -0.0004, 0.0014, 0.0002, 0.0043]     |
| F5_VOL_VOLATILITY    | Non-monotonic  | [-0.0017, 0.0007, 0.0030, 0.0006, 0.0017]      |

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
