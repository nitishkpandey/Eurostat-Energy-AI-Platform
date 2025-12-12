import os

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from ml.forecast_utils import run_forecast
from llm_app.chatbot import answer_question


# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(
    page_title="Eurostat Energy AI Platform",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------
# CUSTOM CSS
# -----------------------------------------------------------
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --background-color: #0e1117;
        --card-background: rgba(255, 255, 255, 0.05);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--card-background);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Improve spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: var(--card-background);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--card-background);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>⚡ Eurostat Energy AI Platform</h1>
    <p>Advanced Analytics • ML Forecasting • AI-Powered Insights</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# DB CONNECTION
# -----------------------------------------------------------
@st.cache_resource
def get_engine():
    db_user = os.getenv("DB_USER", "energy_user")
    db_pass = os.getenv("DB_PASS", "energy_pass")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "energy")

    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


engine = get_engine()


@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_sql("SELECT * FROM observations", engine)
    except ProgrammingError:
        return pd.DataFrame()

    df["year"] = pd.to_datetime(df["time"]).dt.year
    df["geo"] = df["country_code"]
    df["indicator"] = df["indicator_code"]

    return df


data = load_data()

if data.empty:
    st.warning(
        "⏳ No data found in the database yet.\n\n"
        "The ETL pipeline is processing. Please refresh this page in a moment."
    )
    st.stop()

# -----------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Global Filters")
    
    # Year range filter
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    
    year_filter = st.slider(
        "Year Range",
        min_year,
        max_year,
        (min_year, max_year),
        help="Filter data by year range"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Data Info")
    st.metric("Total Records", f"{len(data):,}")
    st.metric("Countries", len(data["geo"].unique()))
    st.metric("Indicators", len(data["indicator"].unique()))
    st.metric("Year Span", f"{min_year} - {max_year}")
    
    st.markdown("---")
    st.markdown("### 🔄 Actions")
    if st.button("🔃 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Filter data by sidebar year range
filtered_data = data[data["year"].between(year_filter[0], year_filter[1])]

# -----------------------------------------------------------
# UI TABS
# -----------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview Dashboard",
    "🔍 Data Explorer",
    "🔮 Forecasting",
    "🤖 AI Insights"
])

# -----------------------------------------------------------
# TAB 1 — OVERVIEW DASHBOARD
# -----------------------------------------------------------
with tab1:
    # KPI Metrics
    st.markdown("### 📈 Key Performance Indicators")
    
    latest_year = filtered_data["year"].max()
    prev_year = latest_year - 1
    
    # Calculate metrics
    latest_gep = filtered_data[
        (filtered_data["year"] == latest_year) &
        (filtered_data["indicator"] == "GEP")
    ]["value"].sum()
    
    prev_gep = filtered_data[
        (filtered_data["year"] == prev_year) &
        (filtered_data["indicator"] == "GEP")
    ]["value"].sum()
    
    gep_change = ((latest_gep - prev_gep) / prev_gep * 100) if prev_gep > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total GEP (Latest Year)",
            f"{latest_gep:,.0f} GWh",
            f"{gep_change:+.1f}%",
            help="Gross Electricity Production"
        )
    
    with col2:
        top_producer = filtered_data[
            (filtered_data["year"] == latest_year) &
            (filtered_data["indicator"] == "GEP")
        ].nlargest(1, "value")
        
        if not top_producer.empty:
            st.metric(
                "Top Producer",
                top_producer.iloc[0]["country_name"],
                f"{top_producer.iloc[0]['value']:,.0f} GWh"
            )
    
    with col3:
        avg_gep = filtered_data[
            (filtered_data["year"] == latest_year) &
            (filtered_data["indicator"] == "GEP")
        ]["value"].mean()
        
        st.metric(
            "Average GEP",
            f"{avg_gep:,.0f} GWh",
            help="Average across all countries"
        )
    
    with col4:
        countries_count = filtered_data[
            (filtered_data["year"] == latest_year) &
            (filtered_data["indicator"] == "GEP")
        ]["geo"].nunique()
        
        st.metric(
            "Countries Reporting",
            countries_count
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Countries by GEP")
        
        df_latest = filtered_data[
            (filtered_data["year"] == latest_year) &
            (filtered_data["dataset_code"] == "nrg_cb_e") &
            (filtered_data["indicator"] == "GEP")
        ]
        
        if not df_latest.empty:
            top_gep = (
                df_latest.groupby(["geo", "country_name"])["value"]
                .mean()
                .reset_index()
                .sort_values("value", ascending=False)
                .head(10)
            )
            
            fig = px.bar(
                top_gep,
                x="value",
                y="country_name",
                orientation="h",
                color="value",
                color_continuous_scale="Viridis",
                labels={"value": "GEP (GWh)", "country_name": "Country"},
                title=f"Gross Electricity Production - {latest_year}"
            )
            
            fig.update_layout(
                showlegend=False,
                height=400,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No GEP data available for the selected period.")
    
    with col2:
        st.markdown("#### 📈 Germany GEP Trend")
        
        germany_gep = filtered_data[
            (filtered_data["geo"] == "DE") &
            (filtered_data["dataset_code"] == "nrg_cb_e") &
            (filtered_data["indicator"] == "GEP")
        ][["year", "value"]].drop_duplicates().sort_values("year")
        
        if not germany_gep.empty:
            fig = px.line(
                germany_gep,
                x="year",
                y="value",
                markers=True,
                labels={"value": "GEP (GWh)", "year": "Year"},
                title="Year-over-Year Electricity Production"
            )
            
            fig.update_traces(
                line=dict(color="#667eea", width=3),
                marker=dict(size=8)
            )
            
            fig.update_layout(
                height=400,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No GEP data available for Germany.")


# -----------------------------------------------------------
# TAB 2 — DATA EXPLORER
# -----------------------------------------------------------
with tab2:
    st.markdown("### 🔍 Interactive Data Explorer")
    
    countries = sorted(filtered_data["geo"].unique())
    indicators = sorted(filtered_data["indicator"].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_geo = st.selectbox(
            "🌍 Select Country",
            countries,
            help="Choose a country to explore"
        )
    
    with col2:
        selected_indicator = st.selectbox(
            "📊 Select Indicator",
            indicators,
            help="Choose an energy indicator"
        )
    
    df_filtered = filtered_data[
        (filtered_data["geo"] == selected_geo) &
        (filtered_data["indicator"] == selected_indicator)
    ]
    
    if not df_filtered.empty:
        # Time series chart
        st.markdown("#### 📈 Time Series Analysis")
        
        fig = px.line(
            df_filtered.sort_values("year"),
            x="year",
            y="value",
            markers=True,
            labels={"value": "Value", "year": "Year"},
            title=f"{selected_indicator} - {selected_geo}"
        )
        
        fig.update_traces(
            line=dict(color="#667eea", width=3),
            marker=dict(size=10)
        )
        
        fig.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison chart
        st.markdown("#### 🌐 Top 10 Countries Comparison")
        
        top_df = filtered_data[
            filtered_data["indicator"] == selected_indicator
        ]
        
        if not top_df.empty:
            top_countries = (
                top_df.groupby(["geo", "country_name"])["value"]
                .mean()
                .reset_index()
                .sort_values("value", ascending=False)
                .head(10)
            )
            
            fig = px.bar(
                top_countries,
                x="country_name",
                y="value",
                color="value",
                color_continuous_scale="Plasma",
                labels={"value": "Average Value", "country_name": "Country"},
                title=f"Average {selected_indicator} by Country"
            )
            
            fig.update_layout(
                showlegend=False,
                height=400,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("#### 📋 Raw Data")
        st.dataframe(
            df_filtered[["year", "country_name", "indicator_label", "value", "unit_label"]]
            .sort_values("year", ascending=False),
            use_container_width=True,
            height=300
        )
    else:
        st.info("No data available for this combination of filters.")


# -----------------------------------------------------------
# TAB 3 — FORECASTING
# -----------------------------------------------------------
with tab3:
    st.markdown("### 🔮 ML-Powered Forecasting")
    st.markdown("Generate future predictions using XGBoost and Exponential Smoothing models.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        country = st.selectbox(
            "🌍 Select Country",
            sorted(data["geo"].unique()),
            key="f1"
        )
    
    with col2:
        indicator = st.selectbox(
            "📊 Select Indicator",
            sorted(data["indicator"].unique()),
            key="f2"
        )
    
    if st.button("🚀 Generate Forecast", use_container_width=True):
        with st.spinner("🔄 Training models and generating forecast..."):
            forecast_df, model_used = run_forecast(data, country, indicator)
        
        if not forecast_df.empty:
            st.success(f"✅ Forecast complete! Model used: **{model_used}**")
            
            # Create forecast visualization
            fig = go.Figure()
            
            historical = forecast_df[forecast_df["type"] == "historical"]
            forecast = forecast_df[forecast_df["type"] == "forecast"]
            
            fig.add_trace(go.Scatter(
                x=historical["year"],
                y=historical["value"],
                mode="lines+markers",
                name="Historical",
                line=dict(color="#667eea", width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast["year"],
                y=forecast["value"],
                mode="lines+markers",
                name="Forecast",
                line=dict(color="#ff7f0e", width=3, dash="dash"),
                marker=dict(size=8, symbol="diamond")
            ))
            
            fig.update_layout(
                title=f"Forecast: {indicator} - {country}",
                xaxis_title="Year",
                yaxis_title="Value",
                height=500,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            with st.expander("📊 View Forecast Data"):
                st.dataframe(
                    forecast_df,
                    use_container_width=True
                )
        else:
            st.warning("⚠️ Insufficient data to generate forecast for this selection.")


# -----------------------------------------------------------
# TAB 4 — AI INSIGHTS (RAG)
# -----------------------------------------------------------
with tab4:
    st.markdown("### 🤖 AI-Powered Insights Assistant")
    st.markdown("Ask natural language questions about European energy data.")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - Which country's GEP is rising fastest?
        - Which regions have declining final energy consumption?
        - Show countries with stable GEP trends
        - What is the average energy production in Europe?
        - Compare energy consumption across sectors
        """)
    
    # Chat interface
    user_q = st.text_input(
        "Your question:",
        placeholder="e.g., Which country has the highest electricity production?",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        ask_button = st.button("🔍 Ask AI", use_container_width=True)
    
    if ask_button and user_q:
        with st.spinner("🤔 Analyzing data..."):
            result = answer_question(user_q)
        
        # Display answer in a nice card
        st.markdown("---")
        st.markdown("#### 💡 Answer")
        st.markdown(result["answer"])
        
        if result.get("mode"):
            st.caption(f"🔧 Analysis mode: {result['mode']}")
    elif ask_button:
        st.warning("Please enter a question first.")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.6); padding: 1rem;'>
    <p>Data Source: <strong>Eurostat REST API</strong> | 
    Built with ❤️ using Streamlit, PostgreSQL, XGBoost & AI</p>
</div>
""", unsafe_allow_html=True)