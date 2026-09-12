# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu, f_oneway, jarque_bera
# import statsmodels.api as sm
# from statsmodels.stats.outliers_influence import variance_inflation_factor
# from statsmodels.graphics.gofplots import qqplot
# import matplotlib.pyplot as plt

# def format_pvalue(p):
#     """Display very small p-values without making them look like exactly zero."""
#     if p == 0:
#         return "< 1e-300"
#     if p < 0.0001:
#         return f"{p:.2e}"
#     return f"{p:.4f}"

# st.set_page_config(
#     page_title="California Housing Analytics",
#     page_icon="🏠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # -------------------- DARK UI --------------------
# st.markdown("""
# <style>
# [data-testid="stAppViewContainer"] {
#     background: #090d18;
#     color: #e5e7eb;
# }
# [data-testid="stHeader"] { background: #090d18; }
# [data-testid="stSidebar"] {
#     background: #0f172a;
#     border-right: 1px solid #263244;
# }
# [data-testid="stSidebar"] * { color: #e5e7eb !important; }
# .block-container { padding-top: 1.8rem; padding-bottom: 3rem; }

# .hero {
#     padding: 1.7rem 2rem;
#     border-radius: 20px;
#     background: linear-gradient(135deg, #111827 0%, #172554 52%, #312e81 100%);
#     border: 1px solid #334155;
#     margin-bottom: 1.4rem;
#     box-shadow: 0 12px 35px rgba(0,0,0,.28);
# }
# .hero h1 { margin: 0 0 .35rem 0; font-size: 2.35rem; color: #f8fafc; }
# .hero p { margin: 0; color: #cbd5e1; font-size: 1rem; }

# .section-title {
#     color: #f8fafc;
#     font-size: 1.35rem;
#     font-weight: 750;
#     margin: 1rem 0 .75rem;
# }

# [data-testid="stMetric"] {
#     background: linear-gradient(145deg, #111827, #151d2d) !important;
#     border: 1px solid #293548 !important;
#     border-radius: 15px !important;
#     padding: 13px !important;
#     box-shadow: 0 5px 18px rgba(0,0,0,.22);
# }
# [data-testid="stMetricLabel"] { color: #94a3b8 !important; }
# [data-testid="stMetricValue"] { color: #f8fafc !important; }
# [data-testid="stMetricDelta"] { color: #cbd5e1 !important; }

# [data-testid="stDataFrame"] {
#     border: 1px solid #293548;
#     border-radius: 12px;
# }

# div[data-baseweb="select"] > div,
# div[data-baseweb="input"] > div,
# textarea {
#     background: #111827 !important;
#     color: #f8fafc !important;
#     border-color: #334155 !important;
# }

# .stTabs [data-baseweb="tab-list"] { gap: 8px; }
# .stTabs [data-baseweb="tab"] {
#     background: #111827;
#     border: 1px solid #293548;
#     border-radius: 10px 10px 0 0;
#     padding: 9px 16px;
#     color: #cbd5e1;
# }
# .stTabs [aria-selected="true"] {
#     background: #1e293b !important;
#     color: #f8fafc !important;
#     border-bottom: 2px solid #818cf8 !important;
# }

# .info-card {
#     background: #111827;
#     border: 1px solid #293548;
#     border-radius: 14px;
#     padding: 1rem 1.15rem;
# }
# .small-note { color: #94a3b8; font-size: .9rem; }
# hr { border-color: #263244; }
# </style>
# """, unsafe_allow_html=True)

# # -------------------- DATA --------------------
# @st.cache_data
# def load_data():
#     data = pd.read_csv("data/california_housing.csv")
#     data["AgeGroup"] = pd.cut(
#         data["HouseAge"],
#         bins=[0, 20, 40, np.inf],
#         labels=["New", "Middle-aged", "Old"],
#         include_lowest=True
#     )
#     data["IncomeGroup"] = pd.qcut(
#         data["MedInc"],
#         q=3,
#         labels=["Low", "Medium", "High"],
#         duplicates="drop"
#     )
#         # Convert categorical variables to normal strings
#     data["AgeGroup"] = data["AgeGroup"].astype(str)
#     data["IncomeGroup"] = data["IncomeGroup"].astype(str)
#     return data

# try:
#     df = load_data()
# except FileNotFoundError:
#     st.error("Dataset not found. Put california_housing.csv inside the data/ folder.")
#     st.stop()

# numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
# predictors = [
#     "MedInc", "HouseAge", "AveRooms", "AveBedrms",
#     "Population", "AveOccup", "Latitude", "Longitude"
# ]
# target = "MedHouseVal"
# pretty = {
#     "MedInc": "Median Income", "HouseAge": "House Age",
#     "AveRooms": "Average Rooms", "AveBedrms": "Average Bedrooms",
#     "Population": "Population", "AveOccup": "Average Occupancy",
#     "Latitude": "Latitude", "Longitude": "Longitude",
#     "MedHouseVal": "Median House Value"
# }

# # -------------------- HEADER --------------------
# st.markdown("""
# <div class="hero">
#     <h1>🏠 California Housing Analytics</h1>
#     <p>Interactive statistical exploration • hypothesis testing • OLS modelling • diagnostics</p>
# </div>
# """, unsafe_allow_html=True)

# # -------------------- SIDEBAR --------------------
# st.sidebar.title("⚙️ Dashboard Controls")
# st.sidebar.caption("Filter the dataset used in the exploration tab.")
# st.sidebar.markdown("### 📌 Dataset")
# st.sidebar.info("California Housing district-level data with income, housing, population and location variables.")

# selected_income = st.sidebar.multiselect(
#     "Income group", ["Low", "Medium", "High"],
#     default=["Low", "Medium", "High"]
# )
# selected_age = st.sidebar.multiselect(
#     "House-age group", ["New", "Middle-aged", "Old"],
#     default=["New", "Middle-aged", "Old"]
# )

# filtered_df = df[
#     df["IncomeGroup"].astype(str).isin(selected_income) &
#     df["AgeGroup"].astype(str).isin(selected_age)
# ].copy()

# # -------------------- SUMMARY CARDS --------------------
# c1, c2, c3, c4 = st.columns(4)
# # c1.metric("📊 Total Records", f"{len(df):,}")
# # c2.metric("🔎 Filtered Records", f"{len(filtered_df):,}")
# # c3.metric("💰 Avg. House Value", f"{filtered_df[target].mean():.2f}" if len(filtered_df) else "—")
# # c4.metric("💵 Avg. Income", f"{filtered_df['MedInc'].mean():.2f}" if len(filtered_df) else "—")
# c1.metric("📊 Total Records", f"{len(df):,}")
# c2.metric("🔎 Filtered Records", f"{len(filtered_df):,}")

# avg_house_value = filtered_df[target].mean() * 100000
# avg_income = filtered_df["MedInc"].mean() * 10000

# c3.metric(
#     "🏠 Avg. House Value",
#     f"${avg_house_value:,.0f}"
# )

# c4.metric(
#     "💵 Avg. Income",
#     f"${avg_income:,.0f}"
# )

# tab1, tab2, tab3 = st.tabs([
#     "📊 Data Exploration", "🧪 Hypothesis Testing Lab", "🏠 Live Prediction & Diagnostics"
# ])

# # ======================================================
# # TAB 1
# # ======================================================
# # ======================================================
# # TAB 1 — DATA EXPLORATION
# # ======================================================
# with tab1:

#     st.markdown(
#         '<div class="section-title">Dataset Overview</div>',
#         unsafe_allow_html=True
#     )

#     col1, col2 = st.columns([1.55, 1])

#     with col1:
#         st.dataframe(
#             filtered_df.head(10),
#             use_container_width=True,
#             hide_index=True
#         )

#     with col2:
#         st.write("**Dataset dimensions**")
#         st.write(f"Rows: **{len(df):,}**")
#         st.write(f"Filtered rows: **{len(filtered_df):,}**")
#         st.write(f"Columns: **{len(df.columns)}**")
#         st.write(
#             f"Missing values: **{int(df.isna().sum().sum())}**"
#         )

#         st.write("**Numerical variables**")
#         st.caption(", ".join(numeric_columns))

#     # Safety check
#     if filtered_df.empty:

#         st.warning(
#             "⚠️ No records match the selected filters. "
#             "Please select at least one Income Group and one House-age Group."
#         )

#     else:

#         # ==================================================
#         # DESCRIPTIVE STATISTICS
#         # ==================================================

#         st.markdown("---")

#         st.markdown(
#             '<div class="section-title">📈 Descriptive Statistics</div>',
#             unsafe_allow_html=True
#         )

#         desc = pd.DataFrame({
#             "Mean": filtered_df[numeric_columns].mean(),
#             "Median": filtered_df[numeric_columns].median(),
#             "Std. Deviation": filtered_df[numeric_columns].std(),
#             "IQR": (
#                 filtered_df[numeric_columns].quantile(0.75)
#                 - filtered_df[numeric_columns].quantile(0.25)
#             ),
#             "Skewness": filtered_df[numeric_columns].skew(),
#             "Kurtosis": filtered_df[numeric_columns].kurt()
#         }).round(3)

#         st.dataframe(
#             desc,
#             use_container_width=True
#         )

#         # ==================================================
#         # DISTRIBUTION
#         # ==================================================

#         st.markdown("---")

#         st.markdown(
#             '<div class="section-title">📊 Distribution Explorer</div>',
#             unsafe_allow_html=True
#         )

#         d1, d2 = st.columns([1, 2])

#         with d1:

#             hist_variable = st.selectbox(
#                 "Choose numerical variable",
#                 numeric_columns,
#                 format_func=lambda x: pretty[x],
#                 key="hist_variable"
#             )

#         with d2:

#             hist_data = pd.to_numeric(
#                 filtered_df[hist_variable],
#                 errors="coerce"
#             ).dropna()

#             if len(hist_data) > 0:

#                 fig_hist = px.histogram(
#                     x=hist_data,
#                     nbins=45,
#                     histnorm="probability density",
#                     title=f"Distribution of {pretty[hist_variable]}"
#                 )

#                 fig_hist.update_traces(
#                     marker_line_width=0.5
#                 )

#                 fig_hist.update_layout(
#                     template="plotly_dark",
#                     height=430,
#                     bargap=0.04,
#                     xaxis_title=pretty[hist_variable],
#                     yaxis_title="Probability Density",
#                     margin=dict(l=50, r=20, t=60, b=50)
#                 )

#                 st.plotly_chart(
#                     fig_hist,
#                     use_container_width=True,
#                     key="histogram_chart"
#                 )

#             else:

#                 st.warning("No valid numeric data available for this variable.")

#         # ==================================================
#         # BOXPLOT
#         # ==================================================

#         st.markdown("---")

#         st.markdown(
#             '<div class="section-title">📦 Boxplot & Outlier Explorer</div>',
#             unsafe_allow_html=True
#         )

#         box_variable = st.selectbox(
#             "Choose variable for boxplot",
#             numeric_columns,
#             index=numeric_columns.index(target),
#             format_func=lambda x: pretty[x],
#             key="box_variable"
#         )

#         box_data = pd.to_numeric(
#             filtered_df[box_variable],
#             errors="coerce"
#         ).dropna()

#         if len(box_data) > 0:

#             fig_box = px.box(
#                 y=box_data,
#                 points="outliers",
#                 title=f"Boxplot of {pretty[box_variable]}"
#             )

#             fig_box.update_traces(
#                 marker_size=5,
#                 line_width=2
#             )

#             fig_box.update_layout(
#                 template="plotly_dark",
#                 height=470,
#                 yaxis_title=pretty[box_variable],
#                 margin=dict(l=50, r=20, t=60, b=50)
#             )

#             st.plotly_chart(
#                 fig_box,
#                 use_container_width=True,
#                 key="boxplot_chart"
#             )

#             q1 = box_data.quantile(0.25)
#             q3 = box_data.quantile(0.75)
#             iqr = q3 - q1

#             lower = q1 - 1.5 * iqr
#             upper = q3 + 1.5 * iqr

#             outlier_count = int(
#                 (
#                     (box_data < lower)
#                     | (box_data > upper)
#                 ).sum()
#             )

#             o1, o2, o3 = st.columns(3)

#             o1.metric(
#                 "Q1",
#                 f"{q1:.3f}"
#             )

#             o2.metric(
#                 "Q3",
#                 f"{q3:.3f}"
#             )

#             o3.metric(
#                 "Potential Outliers",
#                 f"{outlier_count:,}"
#             )

#             st.caption(
#                 "Outliers are identified using the "
#                 "1.5 × IQR rule. A flagged observation "
#                 "is not automatically an error."
#             )

#         # ==================================================
#         # SCATTER PLOT
#         # ==================================================

#         st.markdown("---")

#         st.markdown(
#             '<div class="section-title">🔗 Relationship Explorer</div>',
#             unsafe_allow_html=True
#         )

#         s1, s2 = st.columns(2)

#         with s1:

#             x_variable = st.selectbox(
#                 "X-axis",
#                 predictors,
#                 format_func=lambda x: pretty[x],
#                 key="x_variable"
#             )

#         with s2:

#             y_variable = st.selectbox(
#                 "Y-axis",
#                 [target] + predictors,
#                 format_func=lambda x: pretty[x],
#                 key="y_variable"
#             )

#         scatter_columns = list(dict.fromkeys([
#             x_variable,
#             y_variable,
#             "IncomeGroup",
#             "HouseAge",
#             "MedInc",
#             "MedHouseVal"
#         ]))

#         scatter_data = filtered_df[scatter_columns].copy()

#         scatter_data[x_variable] = pd.to_numeric(
#             scatter_data[x_variable],
#             errors="coerce"
#         )

#         scatter_data[y_variable] = pd.to_numeric(
#             scatter_data[y_variable],
#             errors="coerce"
#         )

#         scatter_data = scatter_data.dropna(
#             subset=[x_variable, y_variable]
#         )

#         if len(scatter_data) > 0:

#             fig_scatter = px.scatter(
#                 scatter_data,
#                 x=x_variable,
#                 y=y_variable,
#                 color="IncomeGroup",
#                 opacity=0.65,
#                 hover_data=[
#                     "HouseAge",
#                     "MedInc",
#                     "MedHouseVal"
#                 ],
#                 title=(
#                     f"{pretty[x_variable]} vs "
#                     f"{pretty[y_variable]}"
#                 )
#             )

#             fig_scatter.update_layout(
#                 template="plotly_dark",
#                 height=500,
#                 xaxis_title=pretty[x_variable],
#                 yaxis_title=pretty[y_variable],
#                 margin=dict(l=50, r=20, t=60, b=50)
#             )

#             st.plotly_chart(
#                 fig_scatter,
#                 use_container_width=True,
#                 key="scatter_chart"
#             )

#         # ==================================================
#         # CORRELATION MATRIX
#         # ==================================================

#         st.markdown("---")

#         st.markdown(
#             '<div class="section-title">🔥 Correlation Matrix</div>',
#             unsafe_allow_html=True
#         )

#         correlation_data = filtered_df[numeric_columns].apply(
#             pd.to_numeric,
#             errors="coerce"
#         )

#         corr = correlation_data.corr()

#         if not corr.empty:

#             fig_corr = px.imshow(
#                 corr,
#                 text_auto=".2f",
#                 aspect="auto",
#                 title="Pearson Correlation Matrix",
#                 color_continuous_scale="RdBu_r",
#                 zmin=-1,
#                 zmax=1
#             )

#             fig_corr.update_layout(
#                 template="plotly_dark",
#                 height=650,
#                 margin=dict(l=50, r=50, t=70, b=50)
#             )

#             st.plotly_chart(
#                 fig_corr,
#                 use_container_width=True,
#                 key="correlation_chart"
#             )

#             strongest = (
#                 corr[target]
#                 .drop(target)
#                 .abs()
#                 .sort_values(ascending=False)
#                 .head(3)
#             )

#             st.info(
#                 "Strongest linear associations with "
#                 "Median House Value: "
#                 + ", ".join(
#                     f"{pretty[i]} "
#                     f"({corr.loc[i, target]:.2f})"
#                     for i in strongest.index
#                 )
#             )
# # ======================================================
# # TAB 2
# # ======================================================
# with tab2:
#     st.markdown('<div class="section-title">🧪 Statistical Hypothesis Testing</div>', unsafe_allow_html=True)
#     st.write("Choose the type of comparison, grouping variable and numerical metric. The test is calculated automatically at α = 0.05.")

#     test_type = st.radio(
#         "Choose analysis",
#         ["Compare 2 Groups", "Compare 3+ Groups (One-Way ANOVA)"],
#         horizontal=True
#     )
#     categorical_columns = ["IncomeGroup", "AgeGroup"]
#     h1, h2 = st.columns(2)
#     with h1:
#         group_variable = st.selectbox(
#             "Grouping variable", categorical_columns,
#             format_func=lambda x: "Income Group" if x == "IncomeGroup" else "House Age Group"
#         )
#     with h2:
#         metric_variable = st.selectbox(
#             "Numerical metric", numeric_columns,
#             index=numeric_columns.index(target),
#             format_func=lambda x: pretty[x]
#         )

#     test_data = df[[group_variable, metric_variable]].dropna()

#     if test_type == "Compare 2 Groups":
#         groups = test_data[group_variable].astype(str).unique().tolist()
#         selected_groups = st.multiselect("Select exactly two groups", groups, default=groups[:2])

#         if len(selected_groups) != 2:
#             st.warning("Please select exactly two groups.")
#         else:
#             g1, g2 = selected_groups
#             sample1 = test_data[test_data[group_variable].astype(str) == g1][metric_variable]
#             sample2 = test_data[test_data[group_variable].astype(str) == g2][metric_variable]

#             st.markdown("### 📋 Group Summary")
#             a, b = st.columns(2)
#             with a:
#                 st.metric(f"{g1} mean", f"{sample1.mean():.3f}")
#                 st.write(f"Median: **{sample1.median():.3f}**  |  SD: **{sample1.std():.3f}**  |  n = **{len(sample1):,}**")
#             with b:
#                 st.metric(f"{g2} mean", f"{sample2.mean():.3f}")
#                 st.write(f"Median: **{sample2.median():.3f}**  |  SD: **{sample2.std():.3f}**  |  n = **{len(sample2):,}**")

#             st.markdown("### 1️⃣ Shapiro-Wilk Normality Test")
#             n_shapiro = min(5000, len(sample1), len(sample2))
#             sh1 = shapiro(sample1.sample(n=n_shapiro, random_state=42))
#             sh2 = shapiro(sample2.sample(n=n_shapiro, random_state=42))
#             normality = pd.DataFrame({
#                 "Group": [g1, g2],
#                 "Statistic": [f"{sh1.statistic:.4f}", f"{sh2.statistic:.4f}"],
#                 "p-value": [format_pvalue(sh1.pvalue), format_pvalue(sh2.pvalue)],
#                 "Decision": [
#                     "Reject normality" if sh1.pvalue < .05 else "Fail to reject normality",
#                     "Reject normality" if sh2.pvalue < .05 else "Fail to reject normality"
#                 ]
#             })
#             st.dataframe(normality, use_container_width=True, hide_index=True)

#             st.markdown("### 2️⃣ Levene's Test for Equal Variances")
#             lev = levene(sample1, sample2)
#             st.write(
#     f"Statistic: **{lev.statistic:.4f}**   |   "
#     f"p-value: **{format_pvalue(lev.pvalue)}**"
# )
#             if lev.pvalue < .05:
#                 st.warning("Reject H₀: the group variances are significantly different.")
#             else:
#                 st.success("Fail to reject H₀: no significant evidence of unequal variances.")

#             st.markdown("### 3️⃣ Final Group Comparison")
#             if sh1.pvalue >= .05 and sh2.pvalue >= .05:
#                 result = ttest_ind(sample1, sample2, equal_var=lev.pvalue >= .05)
#                 method = "Independent Two-Sample t-test"
#             else:
#                 result = mannwhitneyu(sample1, sample2, alternative="two-sided")
#                 method = "Mann-Whitney U test"

#             st.write(f"**Selected test:** {method}")
#             st.write(
#     f"Test statistic: **{result.statistic:.4f}**   |   "
#     f"p-value: **{format_pvalue(result.pvalue)}**"
# )
#             if result.pvalue < .05:
#                 st.error(f"❌ Reject H₀ at α = 0.05. There is statistically significant evidence that {pretty[metric_variable]} differs between the selected groups.")
#             else:
#                 st.success("✅ Fail to reject H₀ at α = 0.05. There is insufficient statistical evidence of a difference between the selected groups.")
#             st.caption("For Mann-Whitney U, the formal conclusion concerns a difference in distributions; medians are shown as descriptive statistics.")

#     else:
#         groups = test_data[group_variable].astype(str).unique().tolist()
#         if len(groups) < 3:
#             st.warning("ANOVA requires at least three groups.")
#         else:
#             samples = [test_data[test_data[group_variable].astype(str) == g][metric_variable] for g in groups]
#             anova = f_oneway(*samples)
#             st.markdown("### 📋 Group Means")
#             summary = test_data.assign(Group=test_data[group_variable].astype(str)).groupby("Group")[metric_variable].agg(["count", "mean", "median", "std"]).round(3)
#             st.dataframe(summary, use_container_width=True)
#             st.markdown("### 📐 One-Way ANOVA")
#             st.write(
#     f"F-statistic: **{anova.statistic:.4f}**   |   "
#     f"p-value: **{format_pvalue(anova.pvalue)}**"
# )
#             if anova.pvalue < .05:
#                 st.error("❌ Reject H₀ at α = 0.05. At least one group has a statistically different mean.")
#                 try:
#                     from statsmodels.stats.multicomp import pairwise_tukeyhsd
#                     tukey = pairwise_tukeyhsd(test_data[metric_variable], test_data[group_variable].astype(str), alpha=.05)
#                     tukey_df = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
#                     st.markdown("### 🔍 Tukey HSD Post-Hoc Comparison")
#                     st.dataframe(tukey_df, use_container_width=True)
#                 except Exception:
#                     st.info("Post-hoc comparison could not be generated.")
#             else:
#                 st.success("✅ Fail to reject H₀ at α = 0.05. There is insufficient evidence that the group means differ.")

# # ======================================================
# # TAB 3
# # ======================================================
# with tab3:
#     st.markdown('<div class="section-title">🏠 Multiple Linear Regression</div>', unsafe_allow_html=True)
#     st.write("The OLS model predicts median house value from the eight original numerical housing predictors.")

#     model_df = df[predictors + [target]].dropna()
#     X = sm.add_constant(model_df[predictors])
#     y = model_df[target]
#     model = sm.OLS(y, X).fit()

#     m1, m2, m3, m4 = st.columns(4)
#     m1.metric("R²", f"{model.rsquared:.4f}")
#     m2.metric("Adjusted R²", f"{model.rsquared_adj:.4f}")
#     m3.metric("Observations", f"{int(model.nobs):,}")
#     m4.metric("Residual Std. Error", f"{np.sqrt(model.mse_resid):.4f}")

#     st.markdown("### 📌 Model Coefficients")
#     coef_table = pd.DataFrame({
#         "Coefficient": model.params,
#         "p-value": [format_pvalue(p) for p in model.pvalues],
#         "CI Lower 95%": model.conf_int()[0],
#         "CI Upper 95%": model.conf_int()[1]
#     })
#     coef_table.index = ["Intercept" if x == "const" else pretty[x] for x in coef_table.index]
#     st.dataframe(
#         coef_table.style.format({
#             "Coefficient": "{:.5f}",
#             "CI Lower 95%": "{:.5f}",
#             "CI Upper 95%": "{:.5f}"
#         }),
#         use_container_width=True
#     )
#     st.caption("Each coefficient estimates the change in median house value for a one-unit predictor increase while holding the other predictors constant.")

#     st.markdown("---")
#     st.markdown("### 🎯 Live Prediction")
#     st.write("Enter district characteristics below. The fitted OLS model will generate a prediction with uncertainty intervals.")

#     input_values = {}
#     input_ranges = {
#         "MedInc": (float(df.MedInc.min()), float(df.MedInc.max()), float(df.MedInc.median()), .01),
#         "HouseAge": (float(df.HouseAge.min()), float(df.HouseAge.max()), float(df.HouseAge.median()), 1.),
#         "AveRooms": (float(df.AveRooms.quantile(.01)), float(df.AveRooms.quantile(.99)), float(df.AveRooms.median()), .01),
#         "AveBedrms": (float(df.AveBedrms.quantile(.01)), float(df.AveBedrms.quantile(.99)), float(df.AveBedrms.median()), .01),
#         "Population": (float(df.Population.quantile(.01)), float(df.Population.quantile(.99)), float(df.Population.median()), 1.),
#         "AveOccup": (float(df.AveOccup.quantile(.01)), float(df.AveOccup.quantile(.99)), float(df.AveOccup.median()), .01),
#         "Latitude": (float(df.Latitude.min()), float(df.Latitude.max()), float(df.Latitude.median()), .01),
#         "Longitude": (float(df.Longitude.min()), float(df.Longitude.max()), float(df.Longitude.median()), .01)
#     }

#     input_cols = st.columns(4)
#     for i, variable in enumerate(predictors):
#         low, high, default, step = input_ranges[variable]
#         with input_cols[i % 4]:
#             input_values[variable] = st.number_input(pretty[variable], min_value=low, max_value=high, value=default, step=step)

#     input_frame = pd.DataFrame([input_values])
#     prediction = model.get_prediction(sm.add_constant(input_frame, has_constant="add"))
#     ps = prediction.summary_frame(alpha=.05).iloc[0]

#     predicted = float(ps["mean"])
#     ci_low, ci_high = float(ps["mean_ci_lower"]), float(ps["mean_ci_upper"])
#     pi_low, pi_high = float(ps["obs_ci_lower"]), float(ps["obs_ci_upper"])

#     st.markdown("### 💡 Prediction Result")
#     house_value = predicted * 100000
#     confidence_low = ci_low * 100000
#     confidence_high = ci_high * 100000
#     prediction_low = pi_low * 100000
#     prediction_high = pi_high * 100000
#     r1, r2, r3 = st.columns(3)
#     with r1:
#        st.markdown(
#         f"""
#         <div class="prediction-card">
#             <div class="prediction-label">
#                 Predicted Median House Value
#             </div>
#             <div class="prediction-value">
#                 ${house_value:,.0f}
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     with r2:
#         st.markdown(
#         f"""
#         <div class="prediction-card">
#             <div class="prediction-label">
#                 95% Confidence Interval
#             </div>
#             <div class="prediction-value interval">
#                 ${confidence_low:,.0f}
#                 <span>–</span>
#                 ${confidence_high:,.0f}
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     with r3:
#         st.markdown(
#         f"""
#         <div class="prediction-card">
#             <div class="prediction-label">
#                 95% Prediction Interval
#             </div>
#             <div class="prediction-value interval">
#                 ${prediction_low:,.0f}
#                 <span>–</span>
#                 ${prediction_high:,.0f}
#             </div>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.info("The California Housing target is measured in units of $100,000, so the prediction is converted to dollars for easier interpretation.")

#     st.markdown("---")
#     st.markdown("### 🩺 Residual Diagnostics")
#     fitted, residuals = model.fittedvalues, model.resid
#     d1, d2 = st.columns(2)

#     with d1:
#         fig_res = px.scatter(x=fitted, y=residuals, opacity=.45, labels={"x": "Fitted Values", "y": "Residuals"}, title="Residuals vs Fitted Values")
#         fig_res.add_hline(y=0, line_dash="dash")
#         fig_res.update_layout(template="plotly_dark", height=450)
#         st.plotly_chart(fig_res, use_container_width=True)

#     with d2:
#         fig, ax = plt.subplots(figsize=(7, 5))
#         fig.patch.set_facecolor("#111827")
#         ax.set_facecolor("#111827")
#         qqplot(residuals, line="45", ax=ax)
#         ax.set_title("Q-Q Plot of OLS Residuals", color="white")
#         ax.set_xlabel("Theoretical Quantiles", color="white")
#         ax.set_ylabel("Sample Quantiles", color="white")
#         ax.tick_params(colors="white")
#         for spine in ax.spines.values():
#             spine.set_color("#475569")
#         st.pyplot(fig)
#         plt.close(fig)

#     jb = jarque_bera(residuals)
#     st.markdown("### 📐 Jarque-Bera Normality Test")
#     j1, j2 = st.columns(2)
#     j1.metric("JB Statistic", f"{jb.statistic:.4f}")
#     j2.metric("p-value", format_pvalue(jb.pvalue))
#     if jb.pvalue < .05:
#         st.error("❌ Reject H₀: the residuals show statistically significant evidence of deviation from normality.")
#     else:
#         st.success("✅ Fail to reject H₀: insufficient evidence that residuals deviate from normality.")

#     st.markdown("---")
#     st.markdown("### 🔢 Variance Inflation Factor (VIF)")
#     vif = pd.DataFrame({
#         "Predictor": predictors,
#         "VIF": [variance_inflation_factor(model_df[predictors].values, i) for i in range(len(predictors))]
#     })
#     vif["Interpretation"] = vif["VIF"].apply(lambda x: "Low multicollinearity" if x < 5 else "Moderate multicollinearity" if x < 10 else "High multicollinearity")
#     st.dataframe(vif.round(3), use_container_width=True, hide_index=True)
#     st.caption("VIF above 5 is commonly treated as a warning sign; values above 10 indicate a stronger multicollinearity concern.")

# st.markdown("---")
# st.markdown("<div style='text-align:center;color:#64748b;'>California Housing Statistical Dashboard • Applied Statistical Modeling</div>", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu, f_oneway, jarque_bera
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics.gofplots import qqplot
import matplotlib.pyplot as plt

def format_pvalue(p):
    """Display very small p-values without making them look like exactly zero."""
    if p == 0:
        return "< 1e-300"
    if p < 0.0001:
        return f"{p:.2e}"
    return f"{p:.4f}"

st.set_page_config(
    page_title="California Housing Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- WHITE LILAC + DARK BLUE UI --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --lilac: #F8F8F9;
    --navy: #111439;
    --indigo: #4F46E5;
    --violet: #7C3AED;
    --purple: #8B5CF6;
    --border: #E5E4EC;
    --muted: #686B82;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 88% 5%, rgba(124,58,237,.10), transparent 32%),
        radial-gradient(circle at 5% 75%, rgba(79,70,229,.07), transparent 28%),
        linear-gradient(135deg, #FFFFFF 0%, #F8F8F9 48%, #F2F0F9 100%);
    color: var(--navy);
}

[data-testid="stHeader"] {
    background: rgba(248,248,249,.86);
    backdrop-filter: blur(14px);
}

[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 1px solid #252951;
    box-shadow: 5px 0 24px rgba(17,20,57,.08);
}
[data-testid="stSidebar"] * { color: #F8F8F9 !important; }
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { color: #B9BBD0 !important; }

.block-container { max-width: 1500px; padding-top: 1.8rem; padding-bottom: 3rem; }

.hero {
    position: relative;
    overflow: hidden;
    padding: 2.25rem 2.5rem;
    margin-bottom: 1.45rem;
    border-radius: 22px;
    background: linear-gradient(120deg, #111439 0%, #191D50 42%, #4338A8 76%, #7C3AED 100%);
    color: white;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 18px 42px rgba(17,20,57,.18);
}
.hero::before {
    content: "";
    position: absolute;
    width: 360px; height: 360px;
    right: -130px; top: -180px;
    border-radius: 50%;
    background: rgba(255,255,255,.10);
}
.hero h1 {
    position: relative; z-index: 2;
    margin: 0 0 .4rem 0;
    font-size: 2.35rem; font-weight: 800;
    letter-spacing: -.035em; color: #FFFFFF;
    
}
.hero p {
    position: relative; z-index: 2;
    margin: 0; color: rgba(255,255,255,.78); font-size: 1rem;
}

.section-title {
    color: var(--navy); font-size: 1.22rem; font-weight: 750;
    margin: 1.25rem 0 .7rem;
}
.small-note, .section-subtitle { color: var(--muted); font-size: .9rem; }

[data-testid="stMetric"] {
    background: rgba(255,255,255,.94) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 15px !important;
    box-shadow: 0 5px 16px rgba(17,20,57,.045);
    transition: .18s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #CBC8EA !important;
    box-shadow: 0 12px 28px rgba(17,20,57,.08);
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important; font-size: .78rem !important; font-weight: 650 !important;
}
[data-testid="stMetricValue"] {
    color: var(--navy) !important; font-size: 1.75rem !important; font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border); border-radius: 14px;
    overflow: hidden; box-shadow: 0 5px 18px rgba(17,20,57,.045);
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background: #FFFFFF !important;
    color: var(--navy) !important;
    border-color: #DCDCE7 !important;
    border-radius: 10px !important;
}
.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stRadio label {
    color: var(--navy) !important; font-weight: 650 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 5px; background: rgba(255,255,255,.78);
    padding: 5px; border: 1px solid var(--border);
    border-radius: 13px; box-shadow: 0 4px 14px rgba(17,20,57,.035);
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border: none; border-radius: 9px;
    padding: 10px 17px; color: var(--muted); font-weight: 650;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #EEEAFE, #F3EEFF) !important;
    color: var(--navy) !important;
    box-shadow: inset 0 0 0 1px #DED8FA;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

.info-card, .bento-card {
    background: rgba(255,255,255,.90);
    border: 1px solid var(--border); border-radius: 15px;
    padding: 1rem 1.15rem; box-shadow: 0 5px 18px rgba(17,20,57,.045);
}

.prediction-card {
    background: linear-gradient(145deg, #FFFFFF 0%, #F8F7FF 100%);
    border: 1px solid #E3E0F5; border-top: 4px solid var(--indigo);
    border-radius: 16px; padding: 1.25rem 1.4rem;
    min-height: 140px; box-shadow: 0 7px 22px rgba(17,20,57,.055);
}
.prediction-label {
    color: var(--muted); font-size: .76rem; font-weight: 750;
    text-transform: uppercase; letter-spacing: .05em; margin-bottom: .6rem;
}
.prediction-value { color: var(--navy); font-size: 1.85rem; font-weight: 800; }
.prediction-value.interval { color: #5B21B6; font-size: 1.25rem; }

[data-testid="stAlert"] { border-radius: 12px; }
hr { border: none; border-top: 1px solid #E4E3EC; margin: 1.7rem 0; }

@media (max-width: 900px) {
    .hero h1 { font-size: 1.8rem; }
    .hero { padding: 1.7rem; }
}

    /* ===== FINAL CONTRAST OVERRIDES — DO NOT CHANGE PALETTE ===== */

    /* Main page: force dark-blue text where Streamlit otherwise injects white */
    [data-testid="stAppViewContainer"] .stMarkdown,
    [data-testid="stAppViewContainer"] .stMarkdown p,
    [data-testid="stAppViewContainer"] .stMarkdown span,
    [data-testid="stAppViewContainer"] .stMarkdown strong,
    [data-testid="stAppViewContainer"] .stText,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] h5,
    [data-testid="stAppViewContainer"] h6 {
        color: #111439 !important;
    }

    /* Tabs: Streamlit/BaseWeb can apply white text to inactive tabs */
    [data-testid="stAppViewContainer"] .stTabs [role="tab"],
    [data-testid="stAppViewContainer"] .stTabs [role="tab"] *,
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"],
    [data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"] *,
    [data-testid="stAppViewContainer"] .stTabs button,
    [data-testid="stAppViewContainer"] .stTabs button * {
        color: #111439 !important;
        -webkit-text-fill-color: #111439 !important;
    }

    /* Active tab uses the existing indigo accent only */
    [data-testid="stAppViewContainer"] .stTabs [aria-selected="true"],
    [data-testid="stAppViewContainer"] .stTabs [aria-selected="true"] *,
    [data-testid="stAppViewContainer"] .stTabs [role="tab"][aria-selected="true"],
    [data-testid="stAppViewContainer"] .stTabs [role="tab"][aria-selected="true"] * {
        color: #4F46E5 !important;
        -webkit-text-fill-color: #4F46E5 !important;
    }

    /* Radio buttons: fix the white labels shown in your screenshot */
    [data-testid="stAppViewContainer"] [data-testid="stRadio"] label,
    [data-testid="stAppViewContainer"] [data-testid="stRadio"] label *,
    [data-testid="stAppViewContainer"] [data-testid="stRadio"] p,
    [data-testid="stAppViewContainer"] [data-testid="stRadio"] span {
        color: #111439 !important;
        -webkit-text-fill-color: #111439 !important;
    }

    /* Selectbox, multiselect and number-input labels */
    [data-testid="stAppViewContainer"] [data-testid="stSelectbox"] label,
    [data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] label,
    [data-testid="stAppViewContainer"] [data-testid="stNumberInput"] label,
    [data-testid="stAppViewContainer"] [data-testid="stSelectbox"] label *,
    [data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] label *,
    [data-testid="stAppViewContainer"] [data-testid="stNumberInput"] label * {
        color: #111439 !important;
        -webkit-text-fill-color: #111439 !important;
    }

    /* Normal Streamlit body text */
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] strong {
        color: #111439 !important;
    }

    /* Captions remain the existing muted palette color */
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] * {
        color: #686B82 !important;
    }

    /* Alerts: readable dark-blue text on light alert surfaces */
    [data-testid="stAppViewContainer"] [data-testid="stAlert"] p,
    [data-testid="stAppViewContainer"] [data-testid="stAlert"] span,
    [data-testid="stAppViewContainer"] [data-testid="stAlert"] div {
        color: #111439 !important;
    }

    /* Sidebar remains the ORIGINAL dark-blue + white text */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label * {
        color: #F8F8F9 !important;
        -webkit-text-fill-color: #F8F8F9 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: #B9BBD0 !important;
        -webkit-text-fill-color: #B9BBD0 !important;
    }

</style>
""", unsafe_allow_html=True)

# -------------------- DATA --------------------
@st.cache_data
def load_data():
    data = pd.read_csv("data/california_housing.csv")
    data["AgeGroup"] = pd.cut(
        data["HouseAge"],
        bins=[0, 20, 40, np.inf],
        labels=["New", "Middle-aged", "Old"],
        include_lowest=True
    )
    data["IncomeGroup"] = pd.qcut(
        data["MedInc"],
        q=3,
        labels=["Low", "Medium", "High"],
        duplicates="drop"
    )
        # Convert categorical variables to normal strings
    data["AgeGroup"] = data["AgeGroup"].astype(str)
    data["IncomeGroup"] = data["IncomeGroup"].astype(str)
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset not found. Put california_housing.csv inside the data/ folder.")
    st.stop()

numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
predictors = [
    "MedInc", "HouseAge", "AveRooms", "AveBedrms",
    "Population", "AveOccup", "Latitude", "Longitude"
]
target = "MedHouseVal"
pretty = {
    "MedInc": "Median Income", "HouseAge": "House Age",
    "AveRooms": "Average Rooms", "AveBedrms": "Average Bedrooms",
    "Population": "Population", "AveOccup": "Average Occupancy",
    "Latitude": "Latitude", "Longitude": "Longitude",
    "MedHouseVal": "Median House Value"
}

# -------------------- HEADER --------------------
st.markdown("""

    <h1 style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;">
        🏠 California Housing Analytics
    </h1>
    <p>Interactive statistical exploration • hypothesis testing • OLS modelling • diagnostics</p>

""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.caption("Filter the dataset used in the exploration tab.")
st.sidebar.markdown("### 📌 Dataset")


selected_income = st.sidebar.multiselect(
    "Income group", ["Low", "Medium", "High"],
    default=["Low", "Medium", "High"]
)
selected_age = st.sidebar.multiselect(
    "House-age group", ["New", "Middle-aged", "Old"],
    default=["New", "Middle-aged", "Old"]
)

filtered_df = df[
    df["IncomeGroup"].astype(str).isin(selected_income) &
    df["AgeGroup"].astype(str).isin(selected_age)
].copy()

# -------------------- SUMMARY CARDS --------------------
c1, c2, c3, c4 = st.columns(4)
# c1.metric("📊 Total Records", f"{len(df):,}")
# c2.metric("🔎 Filtered Records", f"{len(filtered_df):,}")
# c3.metric("💰 Avg. House Value", f"{filtered_df[target].mean():.2f}" if len(filtered_df) else "—")
# c4.metric("💵 Avg. Income", f"{filtered_df['MedInc'].mean():.2f}" if len(filtered_df) else "—")
c1.metric("📊 Total Records", f"{len(df):,}")
c2.metric("🔎 Filtered Records", f"{len(filtered_df):,}")

avg_house_value = filtered_df[target].mean() * 100000
avg_income = filtered_df["MedInc"].mean() * 10000

c3.metric(
    "🏠 Avg. House Value",
    f"${avg_house_value:,.0f}"
)

c4.metric(
    "💵 Avg. Income",
    f"${avg_income:,.0f}"
)

tab1, tab2, tab3 = st.tabs([
    "📊 Data Exploration", "🧪 Hypothesis Testing Lab", "🏠 Live Prediction & Diagnostics"
])

# ======================================================
# TAB 1
# ======================================================
# ======================================================
# TAB 1 — DATA EXPLORATION
# ======================================================
with tab1:

    st.markdown(
        '<div class="section-title">Dataset Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.55, 1])

    with col1:
        st.dataframe(
            filtered_df.head(10),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.write("**Dataset dimensions**")
        st.write(f"Rows: **{len(df):,}**")
        st.write(f"Filtered rows: **{len(filtered_df):,}**")
        st.write(f"Columns: **{len(df.columns)}**")
        st.write(
            f"Missing values: **{int(df.isna().sum().sum())}**"
        )

        st.write("**Numerical variables**")
        st.caption(", ".join(numeric_columns))

    # Safety check
    if filtered_df.empty:

        st.warning(
            "⚠️ No records match the selected filters. "
            "Please select at least one Income Group and one House-age Group."
        )

    else:

        # ==================================================
        # DESCRIPTIVE STATISTICS
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📈 Descriptive Statistics</div>',
            unsafe_allow_html=True
        )

        desc = pd.DataFrame({
            "Mean": filtered_df[numeric_columns].mean(),
            "Median": filtered_df[numeric_columns].median(),
            "Std. Deviation": filtered_df[numeric_columns].std(),
            "IQR": (
                filtered_df[numeric_columns].quantile(0.75)
                - filtered_df[numeric_columns].quantile(0.25)
            ),
            "Skewness": filtered_df[numeric_columns].skew(),
            "Kurtosis": filtered_df[numeric_columns].kurt()
        }).round(3)

        st.dataframe(
            desc,
            use_container_width=True
        )

        # ==================================================
        # DISTRIBUTION
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📊 Distribution Explorer</div>',
            unsafe_allow_html=True
        )

        d1, d2 = st.columns([1, 2])

        with d1:

            hist_variable = st.selectbox(
                "Choose numerical variable",
                numeric_columns,
                format_func=lambda x: pretty[x],
                key="hist_variable"
            )

        with d2:

            hist_data = pd.to_numeric(
                filtered_df[hist_variable],
                errors="coerce"
            ).dropna()

            if len(hist_data) > 0:

                fig_hist = px.histogram(
                    x=hist_data,
                    nbins=45,
                    histnorm="probability density",
                    title=f"Distribution of {pretty[hist_variable]}"
                )

                fig_hist.update_traces(
                    marker_line_width=0.5
                )

                fig_hist.update_layout(
                    template="plotly_white",
                    height=430,
                    bargap=0.04,
                    xaxis_title=pretty[hist_variable],
                    yaxis_title="Probability Density",
                    margin=dict(l=50, r=20, t=60, b=50)
                )

                st.plotly_chart(
                    fig_hist,
                    use_container_width=True,
                    key="histogram_chart"
                )

            else:

                st.warning("No valid numeric data available for this variable.")

        # ==================================================
        # BOXPLOT
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📦 Boxplot & Outlier Explorer</div>',
            unsafe_allow_html=True
        )

        box_variable = st.selectbox(
            "Choose variable for boxplot",
            numeric_columns,
            index=numeric_columns.index(target),
            format_func=lambda x: pretty[x],
            key="box_variable"
        )

        box_data = pd.to_numeric(
            filtered_df[box_variable],
            errors="coerce"
        ).dropna()

        if len(box_data) > 0:

            fig_box = px.box(
                y=box_data,
                points="outliers",
                title=f"Boxplot of {pretty[box_variable]}"
            )

            fig_box.update_traces(
                marker_size=5,
                line_width=2
            )

            fig_box.update_layout(
                template="plotly_white",
                height=470,
                yaxis_title=pretty[box_variable],
                margin=dict(l=50, r=20, t=60, b=50)
            )

            st.plotly_chart(
                fig_box,
                use_container_width=True,
                key="boxplot_chart"
            )

            q1 = box_data.quantile(0.25)
            q3 = box_data.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outlier_count = int(
                (
                    (box_data < lower)
                    | (box_data > upper)
                ).sum()
            )

            o1, o2, o3 = st.columns(3)

            o1.metric(
                "Q1",
                f"{q1:.3f}"
            )

            o2.metric(
                "Q3",
                f"{q3:.3f}"
            )

            o3.metric(
                "Potential Outliers",
                f"{outlier_count:,}"
            )

            st.caption(
                "Outliers are identified using the "
                "1.5 × IQR rule. A flagged observation "
                "is not automatically an error."
            )

        # ==================================================
        # SCATTER PLOT
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">🔗 Relationship Explorer</div>',
            unsafe_allow_html=True
        )

        s1, s2 = st.columns(2)

        with s1:

            x_variable = st.selectbox(
                "X-axis",
                predictors,
                format_func=lambda x: pretty[x],
                key="x_variable"
            )

        with s2:

            y_variable = st.selectbox(
                "Y-axis",
                [target] + predictors,
                format_func=lambda x: pretty[x],
                key="y_variable"
            )

        scatter_columns = list(dict.fromkeys([
            x_variable,
            y_variable,
            "IncomeGroup",
            "HouseAge",
            "MedInc",
            "MedHouseVal"
        ]))

        scatter_data = filtered_df[scatter_columns].copy()

        scatter_data[x_variable] = pd.to_numeric(
            scatter_data[x_variable],
            errors="coerce"
        )

        scatter_data[y_variable] = pd.to_numeric(
            scatter_data[y_variable],
            errors="coerce"
        )

        scatter_data = scatter_data.dropna(
            subset=[x_variable, y_variable]
        )

        if len(scatter_data) > 0:

            fig_scatter = px.scatter(
                scatter_data,
                x=x_variable,
                y=y_variable,
                color="IncomeGroup",
                opacity=0.65,
                hover_data=[
                    "HouseAge",
                    "MedInc",
                    "MedHouseVal"
                ],
                title=(
                    f"{pretty[x_variable]} vs "
                    f"{pretty[y_variable]}"
                )
            )

            fig_scatter.update_layout(
                template="plotly_white",
                height=500,
                xaxis_title=pretty[x_variable],
                yaxis_title=pretty[y_variable],
                margin=dict(l=50, r=20, t=60, b=50)
            )

            st.plotly_chart(
                fig_scatter,
                use_container_width=True,
                key="scatter_chart"
            )

        # ==================================================
        # CORRELATION MATRIX
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">🔥 Correlation Matrix</div>',
            unsafe_allow_html=True
        )

        correlation_data = filtered_df[numeric_columns].apply(
            pd.to_numeric,
            errors="coerce"
        )

        corr = correlation_data.corr()

        if not corr.empty:

            fig_corr = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                title="Pearson Correlation Matrix",
                color_continuous_scale=["#111439", "#8B5CF6", "#F8F8F9"],
                zmin=-1,
                zmax=1
            )

            fig_corr.update_layout(
                template="plotly_white",
                height=650,
                margin=dict(l=50, r=50, t=70, b=50)
            )

            st.plotly_chart(
                fig_corr,
                use_container_width=True,
                key="correlation_chart"
            )

            strongest = (
                corr[target]
                .drop(target)
                .abs()
                .sort_values(ascending=False)
                .head(3)
            )

            st.info(
                "Strongest linear associations with "
                "Median House Value: "
                + ", ".join(
                    f"{pretty[i]} "
                    f"({corr.loc[i, target]:.2f})"
                    for i in strongest.index
                )
            )
# ======================================================
# TAB 2
# ======================================================
with tab2:
    st.markdown('<div class="section-title">🧪 Statistical Hypothesis Testing</div>', unsafe_allow_html=True)
    st.write("Choose the type of comparison, grouping variable and numerical metric. The test is calculated automatically at α = 0.05.")

    test_type = st.radio(
        "Choose analysis",
        ["Compare 2 Groups", "Compare 3+ Groups (One-Way ANOVA)"],
        horizontal=True
    )
    categorical_columns = ["IncomeGroup", "AgeGroup"]
    h1, h2 = st.columns(2)
    with h1:
        group_variable = st.selectbox(
            "Grouping variable", categorical_columns,
            format_func=lambda x: "Income Group" if x == "IncomeGroup" else "House Age Group"
        )
    with h2:
        metric_variable = st.selectbox(
            "Numerical metric", numeric_columns,
            index=numeric_columns.index(target),
            format_func=lambda x: pretty[x]
        )

    test_data = df[[group_variable, metric_variable]].dropna()

    if test_type == "Compare 2 Groups":
        groups = test_data[group_variable].astype(str).unique().tolist()
        selected_groups = st.multiselect("Select exactly two groups", groups, default=groups[:2])

        if len(selected_groups) != 2:
            st.warning("Please select exactly two groups.")
        else:
            g1, g2 = selected_groups
            sample1 = test_data[test_data[group_variable].astype(str) == g1][metric_variable]
            sample2 = test_data[test_data[group_variable].astype(str) == g2][metric_variable]

            st.markdown("### 📋 Group Summary")
            a, b = st.columns(2)
            with a:
                st.metric(f"{g1} mean", f"{sample1.mean():.3f}")
                st.write(f"Median: **{sample1.median():.3f}**  |  SD: **{sample1.std():.3f}**  |  n = **{len(sample1):,}**")
            with b:
                st.metric(f"{g2} mean", f"{sample2.mean():.3f}")
                st.write(f"Median: **{sample2.median():.3f}**  |  SD: **{sample2.std():.3f}**  |  n = **{len(sample2):,}**")

            st.markdown("### 1️⃣ Shapiro-Wilk Normality Test")
            n_shapiro = min(5000, len(sample1), len(sample2))
            sh1 = shapiro(sample1.sample(n=n_shapiro, random_state=42))
            sh2 = shapiro(sample2.sample(n=n_shapiro, random_state=42))
            normality = pd.DataFrame({
                "Group": [g1, g2],
                "Statistic": [f"{sh1.statistic:.4f}", f"{sh2.statistic:.4f}"],
                "p-value": [format_pvalue(sh1.pvalue), format_pvalue(sh2.pvalue)],
                "Decision": [
                    "Reject normality" if sh1.pvalue < .05 else "Fail to reject normality",
                    "Reject normality" if sh2.pvalue < .05 else "Fail to reject normality"
                ]
            })
            st.dataframe(normality, use_container_width=True, hide_index=True)

            st.markdown("### 2️⃣ Levene's Test for Equal Variances")
            lev = levene(sample1, sample2)
            st.write(
    f"Statistic: **{lev.statistic:.4f}**   |   "
    f"p-value: **{format_pvalue(lev.pvalue)}**"
)
            if lev.pvalue < .05:
                st.warning("Reject H₀: the group variances are significantly different.")
            else:
                st.success("Fail to reject H₀: no significant evidence of unequal variances.")

            st.markdown("### 3️⃣ Final Group Comparison")
            if sh1.pvalue >= .05 and sh2.pvalue >= .05:
                result = ttest_ind(sample1, sample2, equal_var=lev.pvalue >= .05)
                method = "Independent Two-Sample t-test"
            else:
                result = mannwhitneyu(sample1, sample2, alternative="two-sided")
                method = "Mann-Whitney U test"

            st.write(f"**Selected test:** {method}")
            st.write(
    f"Test statistic: **{result.statistic:.4f}**   |   "
    f"p-value: **{format_pvalue(result.pvalue)}**"
)
            if result.pvalue < .05:
                st.error(f"❌ Reject H₀ at α = 0.05. There is statistically significant evidence that {pretty[metric_variable]} differs between the selected groups.")
            else:
                st.success("✅ Fail to reject H₀ at α = 0.05. There is insufficient statistical evidence of a difference between the selected groups.")
            st.caption("For Mann-Whitney U, the formal conclusion concerns a difference in distributions; medians are shown as descriptive statistics.")

    else:
        groups = test_data[group_variable].astype(str).unique().tolist()
        if len(groups) < 3:
            st.warning("ANOVA requires at least three groups.")
        else:
            samples = [test_data[test_data[group_variable].astype(str) == g][metric_variable] for g in groups]
            anova = f_oneway(*samples)
            st.markdown("### 📋 Group Means")
            summary = test_data.assign(Group=test_data[group_variable].astype(str)).groupby("Group")[metric_variable].agg(["count", "mean", "median", "std"]).round(3)
            st.dataframe(summary, use_container_width=True)
            st.markdown("### 📐 One-Way ANOVA")
            st.write(
    f"F-statistic: **{anova.statistic:.4f}**   |   "
    f"p-value: **{format_pvalue(anova.pvalue)}**"
)
            if anova.pvalue < .05:
                st.error("❌ Reject H₀ at α = 0.05. At least one group has a statistically different mean.")
                try:
                    from statsmodels.stats.multicomp import pairwise_tukeyhsd
                    tukey = pairwise_tukeyhsd(test_data[metric_variable], test_data[group_variable].astype(str), alpha=.05)
                    tukey_df = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
                    st.markdown("### 🔍 Tukey HSD Post-Hoc Comparison")
                    st.dataframe(tukey_df, use_container_width=True)
                except Exception:
                    st.info("Post-hoc comparison could not be generated.")
            else:
                st.success("✅ Fail to reject H₀ at α = 0.05. There is insufficient evidence that the group means differ.")

# ======================================================
# TAB 3
# ======================================================
with tab3:
    st.markdown('<div class="section-title">🏠 Multiple Linear Regression</div>', unsafe_allow_html=True)
    st.write("The OLS model predicts median house value from the eight original numerical housing predictors.")

    model_df = df[predictors + [target]].dropna()
    X = sm.add_constant(model_df[predictors])
    y = model_df[target]
    model = sm.OLS(y, X).fit()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("R²", f"{model.rsquared:.4f}")
    m2.metric("Adjusted R²", f"{model.rsquared_adj:.4f}")
    m3.metric("Observations", f"{int(model.nobs):,}")
    m4.metric("Residual Std. Error", f"{np.sqrt(model.mse_resid):.4f}")

    st.markdown("### 📌 Model Coefficients")
    coef_table = pd.DataFrame({
        "Coefficient": model.params,
        "p-value": [format_pvalue(p) for p in model.pvalues],
        "CI Lower 95%": model.conf_int()[0],
        "CI Upper 95%": model.conf_int()[1]
    })
    coef_table.index = ["Intercept" if x == "const" else pretty[x] for x in coef_table.index]
    st.dataframe(
        coef_table.style.format({
            "Coefficient": "{:.5f}",
            "CI Lower 95%": "{:.5f}",
            "CI Upper 95%": "{:.5f}"
        }),
        use_container_width=True
    )
    st.caption("Each coefficient estimates the change in median house value for a one-unit predictor increase while holding the other predictors constant.")

    st.markdown("---")
    st.markdown("### 🎯 Live Prediction")
    st.write("Enter district characteristics below. The fitted OLS model will generate a prediction with uncertainty intervals.")

    input_values = {}
    input_ranges = {
        "MedInc": (float(df.MedInc.min()), float(df.MedInc.max()), float(df.MedInc.median()), .01),
        "HouseAge": (float(df.HouseAge.min()), float(df.HouseAge.max()), float(df.HouseAge.median()), 1.),
        "AveRooms": (float(df.AveRooms.quantile(.01)), float(df.AveRooms.quantile(.99)), float(df.AveRooms.median()), .01),
        "AveBedrms": (float(df.AveBedrms.quantile(.01)), float(df.AveBedrms.quantile(.99)), float(df.AveBedrms.median()), .01),
        "Population": (float(df.Population.quantile(.01)), float(df.Population.quantile(.99)), float(df.Population.median()), 1.),
        "AveOccup": (float(df.AveOccup.quantile(.01)), float(df.AveOccup.quantile(.99)), float(df.AveOccup.median()), .01),
        "Latitude": (float(df.Latitude.min()), float(df.Latitude.max()), float(df.Latitude.median()), .01),
        "Longitude": (float(df.Longitude.min()), float(df.Longitude.max()), float(df.Longitude.median()), .01)
    }

    input_cols = st.columns(4)
    for i, variable in enumerate(predictors):
        low, high, default, step = input_ranges[variable]
        with input_cols[i % 4]:
            input_values[variable] = st.number_input(pretty[variable], min_value=low, max_value=high, value=default, step=step)

    input_frame = pd.DataFrame([input_values])
    prediction = model.get_prediction(sm.add_constant(input_frame, has_constant="add"))
    ps = prediction.summary_frame(alpha=.05).iloc[0]

    predicted = float(ps["mean"])
    ci_low, ci_high = float(ps["mean_ci_lower"]), float(ps["mean_ci_upper"])
    pi_low, pi_high = float(ps["obs_ci_lower"]), float(ps["obs_ci_upper"])

    st.markdown("### 💡 Prediction Result")
    house_value = predicted * 100000
    confidence_low = ci_low * 100000
    confidence_high = ci_high * 100000
    prediction_low = pi_low * 100000
    prediction_high = pi_high * 100000
    r1, r2, r3 = st.columns(3)
    with r1:
       st.markdown(
        f"""
        <div class="prediction-card">
            <div class="prediction-label">
                Predicted Median House Value
            </div>
            <div class="prediction-value">
                ${house_value:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with r2:
        st.markdown(
        f"""
        <div class="prediction-card">
            <div class="prediction-label">
                95% Confidence Interval
            </div>
            <div class="prediction-value interval">
                ${confidence_low:,.0f}
                <span>–</span>
                ${confidence_high:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with r3:
        st.markdown(
        f"""
        <div class="prediction-card">
            <div class="prediction-label">
                95% Prediction Interval
            </div>
            <div class="prediction-value interval">
                ${prediction_low:,.0f}
                <span>–</span>
                ${prediction_high:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("The California Housing target is measured in units of $100,000, so the prediction is converted to dollars for easier interpretation.")

    st.markdown("---")
    st.markdown("### 🩺 Residual Diagnostics")
    fitted, residuals = model.fittedvalues, model.resid
    d1, d2 = st.columns(2)

    with d1:
        fig_res = px.scatter(x=fitted, y=residuals, opacity=.45, labels={"x": "Fitted Values", "y": "Residuals"}, title="Residuals vs Fitted Values")
        fig_res.add_hline(y=0, line_dash="dash")
        fig_res.update_layout(template="plotly_white", paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0)", font=dict(color="#111439"), height=450)
        st.plotly_chart(fig_res, use_container_width=True)

    with d2:
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor("#F8F8F9")
        ax.set_facecolor("#FFFFFF")
        qqplot(residuals, line="45", ax=ax)
        ax.set_title("Q-Q Plot of OLS Residuals", color="#111439")
        ax.set_xlabel("Theoretical Quantiles", color="#111439")
        ax.set_ylabel("Sample Quantiles", color="#111439")
        ax.tick_params(colors="#686B82")
        for spine in ax.spines.values():
            spine.set_color("#DCDCE7")
        st.pyplot(fig)
        plt.close(fig)

    jb = jarque_bera(residuals)
    st.markdown("### 📐 Jarque-Bera Normality Test")
    j1, j2 = st.columns(2)
    j1.metric("JB Statistic", f"{jb.statistic:.4f}")
    j2.metric("p-value", format_pvalue(jb.pvalue))
    if jb.pvalue < .05:
        st.error("❌ Reject H₀: the residuals show statistically significant evidence of deviation from normality.")
    else:
        st.success("✅ Fail to reject H₀: insufficient evidence that residuals deviate from normality.")

    st.markdown("---")
    st.markdown("### 🔢 Variance Inflation Factor (VIF)")
    vif = pd.DataFrame({
        "Predictor": predictors,
        "VIF": [variance_inflation_factor(model_df[predictors].values, i) for i in range(len(predictors))]
    })
    vif["Interpretation"] = vif["VIF"].apply(lambda x: "Low multicollinearity" if x < 5 else "Moderate multicollinearity" if x < 10 else "High multicollinearity")
    st.dataframe(vif.round(3), use_container_width=True, hide_index=True)
    st.caption("VIF above 5 is commonly treated as a warning sign; values above 10 indicate a stronger multicollinearity concern.")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#64748b;'>California Housing Statistical Dashboard • Applied Statistical Modeling</div>", unsafe_allow_html=True)
