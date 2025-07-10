import streamlit as st
import pandas as pd
import os, glob, plotly.express as px
import numpy as np

# 🌈 Styling and config
st.set_page_config(page_title="📱 PhonePe Pulse", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #0f0f0f;
        color: white;
    }
    .stApp {
        background-image: linear-gradient(to bottom right, #1f1f1f, #121212);
        color: white;
    }
    .css-1d391kg {background-color: #1e1e1e;}
    </style>
""", unsafe_allow_html=True)

# 📁 Paths
BASE_PATH = 'cleaned_data'
EDA_PATH = 'visualizations'
SQL_PATH = 'sqlQueries'

# 📦 Dataset mapping
dataset_map = {
    "Aggregated Transaction": "aggregated_transaction.csv",
    "Aggregated User": "aggregated_user.csv",
    "Aggregated Insurance": "aggregated_insurance.csv",

    "Map User": "map_user.csv",
    "Map Transaction": "map_transaction.csv",
    "Map Insurance": "map_insurance.csv",

    "Top User - District": "top_user_district.csv",
    "Top User - Pincode": "top_user_pincode.csv",
    "Top Transaction - District": "top_transaction_district.csv",
    "Top Transaction - Pincode": "top_transaction_pincodet.csv",
    "Top Insurance - District": "top_insurance_district.csv",
    "Top Insurance - Pincode": "top_insurance_pincode.csv",
}

dataset_descriptions = {
    "Aggregated User": "👥 Users data aggregated by state/year/quarter.",
    "Aggregated Transaction": "💸 Transaction amount & count over time.",
    "Aggregated Insurance": "🛡 Insurance counts and value by state.",

    "Map User": "📍 District-level user engagement metrics.",
    "Map Transaction": "📍 Transactions by district over time.",
    "Map Insurance": "📍 Insurance distribution by district.",

    "Top User - District": "🏆 Top districts by user count.",
    "Top User - Pincode": "🏆 Top pincode by user count.",
    "Top Transaction - District": "🏆 Top districts by transaction volume.",
    "Top Transaction - Pincode": "🏆 Top pincode by transaction volume.",
    "Top Insurance - District": "🏆 Top districts by insurance value.",
    "Top Insurance - Pincode": "🏆 Top pincode by insurance value.",
}

# 🧠 Sidebar Dataset Selector
st.sidebar.title("📂 Dataset Explorer")
selected_dataset = st.sidebar.selectbox("Select Dataset", list(dataset_map.keys()))
df = pd.read_csv(os.path.join(BASE_PATH, dataset_map[selected_dataset]))

# 🎯 Dynamic Filters (if columns exist)
if "state" in df.columns:
    selected_state = st.sidebar.selectbox("📍 Select State", sorted(df["state"].dropna().unique()))
    df = df[df["state"] == selected_state]
else:
    selected_state = None

if "year" in df.columns:
    selected_year = st.sidebar.selectbox("📅 Select Year", sorted(df["year"].dropna().unique()))
    df = df[df["year"] == selected_year]

if "quarter" in df.columns:
    selected_quarter = st.sidebar.selectbox("🕓 Select Quarter", sorted(df["quarter"].dropna().unique()))
    df = df[df["quarter"] == selected_quarter]

# 🔮 Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔎 EDA", "🧠 SQL Case Studies", "🗺 Geo Visualization"])

# --- Tab 1: Dashboard ---
with tab1:
    st.markdown(f"## {selected_dataset}")
    st.markdown(dataset_descriptions.get(selected_dataset, "📝 Dataset Preview"))

    st.dataframe(df.head(50), use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    if len(numeric_cols) >= 1:

        chart_type = st.selectbox("📊 Select Chart Type", ["Line", "Scatter", "Pie"])

        # Add space
        st.markdown("<br>", unsafe_allow_html=True) 

        x_axis = st.selectbox("📈 X-Axis", options=cat_cols + numeric_cols, key="x")
        # Add space
        st.markdown("<br>", unsafe_allow_html=True) 

        y_axis = st.selectbox("📉 Y-Axis", options=numeric_cols, key="y")
        # Add space
        st.markdown("<br>", unsafe_allow_html=True) 

        title = f"{y_axis} by {x_axis}"

        df = pd.read_csv(os.path.join(BASE_PATH, dataset_map[selected_dataset]))

        if chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, color=x_axis if x_axis in cat_cols else None,
                          template="plotly_dark", title=title)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=df[cat_cols[0]] if cat_cols else None,
                             template="plotly_dark", title=title)
        elif chart_type == "Pie":
            if x_axis in df.columns and y_axis in df.columns:
                pie_df = df.groupby(x_axis)[y_axis].sum().reset_index()
                fig = px.pie(pie_df, names=x_axis, values=y_axis, template="plotly_dark", title=f"{y_axis} Distribution by {x_axis}")
            else:
                st.warning("❗ Not enough data for pie chart.")
                fig = None

        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("❗ No numeric columns available for visualization.")

# --- Tab 2: EDA Visualizations ---
with tab2:
    st.markdown("## 🔍 Exploratory Data Analysis")
    eda_imgs = glob.glob(os.path.join(EDA_PATH, "*.png"))
    if not eda_imgs:
        st.info("No EDA images found in EDA folder.")
    for img_path in eda_imgs:
        st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
        st.markdown("---")


# --- Tab 3: SQL Case Studies ---
with tab3:
    st.markdown("## 🧠 SQL-Based Case Studies")
    sql_csvs = sorted(glob.glob(os.path.join(SQL_PATH, "*.csv")))
    sql_charts = {os.path.basename(f).replace(".png", ""): f for f in glob.glob(os.path.join(SQL_PATH, "*.png"))}

    if not sql_csvs:
        st.info("No SQL CSVs found in sql_outputs folder.")
    for csv_path in sql_csvs:
        name = os.path.basename(csv_path).replace(".csv", "").replace("_", " ").title()
        df = pd.read_csv(csv_path)
        st.subheader(f"📌 {name}")
        st.dataframe(df)

        chart_path = sql_charts.get(os.path.basename(csv_path).replace(".csv", ""))
        if chart_path:
            st.image(chart_path, use_container_width=True)
        st.markdown("---")


# --- Tab 4: Geo Visualization ---
with tab4:
    st.markdown("## 🗺 Geo Visualizations (Map View)")

    geo_datasets = ["Map User", "Map Transaction", "Map Insurance", "Top User", "Top Transaction", "Top Insurance"]
    selected_geo = st.selectbox("🧭 Choose Dataset", geo_datasets)

    # geo_df = pd.read_csv(os.path.join(BASE_PATH, dataset_map[selected_geo]))
    geo_df = pd.read_csv('cleaned_data\map_insurance.csv')
    geo_df["metric_log"] = np.log1p(geo_df["metric"])  # log1p handles 0 safely

    if all(col in geo_df.columns for col in ["latitude", "longitude"]):
        if "users" in geo_df.columns:
            size_col = "users"
        elif "count" in geo_df.columns:
            size_col = "count"
        elif "amount" in geo_df.columns:
            size_col = "amount"
        else:
            size_col = geo_df.select_dtypes(include="number").columns[-1]

        geo_df = geo_df.sort_values(by=size_col, ascending=False).head(1000)

        fig = px.scatter_geo(
            geo_df,
            lat="latitude",
            lon="longitude",
            color="metric_log",
            size="metric",
            hover_name="label",
            hover_data=["state", "year", "quarter", "metric"],
            title=f"{selected_geo} - Metric Map (Colored by Value)",
            template="plotly_dark",
            opacity=0.5,
            color_continuous_scale="plasma"
        )

        fig.update_geos(
            visible=False,
            resolution=50,
            scope="asia",
            showcountries=True,
            countrycolor="white",
            lataxis_range=[6, 38],
            lonaxis_range=[68, 98]
        )

        fig.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠ This dataset doesn't have latitude & longitude. Add them to enable geo visualizations.")