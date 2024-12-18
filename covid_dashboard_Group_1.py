import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure correct paths and provide feedback if files are missing
DATA_DIR = os.path.join(os.getcwd(), "data")  # Adjust as needed for your file structure

# Button to clear cache
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.experimental_rerun()
    st.success("Cache has been cleared successfully!")

# Load datasets
@st.cache_data
def load_data():
    try:
        country_data = pd.read_csv(os.path.join(DATA_DIR, "country_wise_latest.csv"))
        time_series_data = pd.read_csv(os.path.join(DATA_DIR, "covid_19_clean_complete.csv"))
        daywise_data = pd.read_csv(os.path.join(DATA_DIR, "day_wise.csv"))
        usa_data = pd.read_csv(os.path.join(DATA_DIR, "usa_county_wise.csv"))
    except FileNotFoundError as e:
        st.error(f"File not found: {e.filename}")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        st.stop()
    return country_data, time_series_data, daywise_data, usa_data

# Load data
country_data, time_series_data, daywise_data, usa_data = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.subheader("Interactive COVID-19 Dashboard")
page = st.sidebar.radio("Select a Page:", [
    "Project Overview", "New Cases vs Total Cases", "Deaths vs Recoveries",
    "Fastest Growing Countries", "Worst Affected Countries", "Active Cases Over Time",
    "Top Recovery Rate Countries", "Region-wise Analysis", "Daily Trends Analysis", "Interactive Map", "Summary"
])

# Project Overview
if page == "Project Overview":
    st.image("https://etplanning.co.uk/wp-content/uploads/2021/11/0D53D150-A297-4C1A-94FD-C4948A14C4452-1200x350-1.png", width=100)
    st.title("COVID-19 Analytics Dashboard")
    st.subheader("Project Title: Global COVID-19 Analysis with Interactivity")
    st.write("""
    **Team Members:**
    - Muhammad Ridho Sunation - 1301213038
    - Radithya Fatih Danadyaksa - 1301213332
    - Bayu Seno Nugroho  - 1301213270
    """)
    st.write("**Tools Used**: Streamlit, Pandas, Plotly")

    # Download Dataset
    st.write("### Download Datasets:")
    for name, df in zip(["Country Data", "Time-Series Data", "Daywise Data", "USA Data"],
                        [country_data, time_series_data, daywise_data, usa_data]):
        st.download_button(f"Download {name}", data=df.to_csv(index=False).encode('utf-8'), file_name=f"{name.lower().replace(' ', '_')}.csv")

# New Cases vs Total Cases
elif page == "New Cases vs Total Cases":
    st.header("New Cases vs Total Cases")
    st.write("Visualizing the relationship between daily new cases and total confirmed cases globally.")

    country_data['New Cases'] = country_data['Confirmed'] - country_data['Deaths'] - country_data['Recovered']
    fig = px.scatter(country_data, x="Confirmed", y="New Cases", 
                     size="New Cases", color="Country/Region", 
                     title="New Cases vs Total Confirmed Cases", hover_name="Country/Region")
    st.plotly_chart(fig)

# Deaths vs Recoveries
elif page == "Deaths vs Recoveries":
    st.header("Deaths vs Recoveries")
    st.write("Analyzing the global death and recovery percentages.")

    total_deaths = daywise_data['Deaths'].iloc[-1]
    total_recovered = daywise_data['Recovered'].iloc[-1]
    fig = px.pie(names=["Deaths", "Recovered"], values=[total_deaths, total_recovered],
                 title="Global Deaths vs Recoveries Percentage")
    st.plotly_chart(fig)

# Fastest Growing Countries
elif page == "Fastest Growing Countries":
    st.header("Top 10 Countries with Fastest Growth Rates")
    st.write("Countries with the highest percentage increase in confirmed cases.")

    country_data['Growth Rate (%)'] = (country_data['Confirmed'] / country_data['Confirmed'].mean()) * 100
    fastest_growing = country_data.nlargest(10, 'Growth Rate (%)')
    fig = px.bar(fastest_growing, x="Country/Region", y="Growth Rate (%)", color="Growth Rate (%)",
                 title="Top 10 Fastest Growing Countries", hover_name="Country/Region")
    st.plotly_chart(fig)

# Worst Affected Countries
elif page == "Worst Affected Countries":
    st.header("Top 5 Worst Affected Countries")
    st.write("### By Active Cases and Deaths")

    top_active = country_data.nlargest(5, 'Active')
    top_deaths = country_data.nlargest(5, 'Deaths')

    col1, col2 = st.columns(2)
    with col1:
        fig_active = px.bar(top_active, x="Country/Region", y="Active", color="Active", title="Top 5 Active Cases", hover_name="Country/Region")
        st.plotly_chart(fig_active)
    with col2:
        fig_deaths = px.bar(top_deaths, x="Country/Region", y="Deaths", color="Deaths", title="Top 5 Deaths", hover_name="Country/Region")
        st.plotly_chart(fig_deaths)

# Top Recovery Rate Countries
elif page == "Top Recovery Rate Countries":
    st.header("Top 10 Countries by Recovery Rate")
    st.write("Highlighting countries with the highest recovery rates globally.")

    country_data['Recovery Rate (%)'] = (country_data['Recovered'] / country_data['Confirmed']) * 100
    top_recovery = country_data.nlargest(10, 'Recovery Rate (%)')
    fig = px.bar(top_recovery, x="Country/Region", y="Recovery Rate (%)", color="Recovery Rate (%)",
                 title="Top 10 Countries by Recovery Rate", hover_name="Country/Region")
    st.plotly_chart(fig)

# Region-wise Analysis
elif page == "Region-wise Analysis":
    st.header("Region-wise COVID-19 Analysis")
    st.write("Select a continent or region to analyze COVID-19 metrics.")

    region = st.selectbox("Select Region:", country_data['WHO Region'].unique())
    filtered_region = country_data[country_data['WHO Region'] == region]

    col1, col2 = st.columns(2)
    with col1:
        fig_cases = px.bar(filtered_region, x="Country/Region", y="Confirmed", color="Confirmed", title=f"Confirmed Cases in {region}")
        st.plotly_chart(fig_cases)
    with col2:
        fig_deaths = px.bar(filtered_region, x="Country/Region", y="Deaths", color="Deaths", title=f"Deaths in {region}")
        st.plotly_chart(fig_deaths)

# Daily Trends Analysis
elif page == "Daily Trends Analysis":
    st.header("Daily Trends of COVID-19 Cases")
    st.write("Select a country to analyze daily trends of confirmed, deaths, and recovered cases.")

    selected_country = st.selectbox("Select Country:", time_series_data['Country/Region'].unique())
    country_daily = time_series_data[time_series_data['Country/Region'] == selected_country]

    fig_trend = px.line(country_daily, x="Date", y=["Confirmed", "Deaths", "Recovered"],
                        title=f"Daily COVID-19 Trends in {selected_country}", labels={"value": "Cases", "variable": "Category"})
    st.plotly_chart(fig_trend)

# Active Cases Over Time
elif page == "Active Cases Over Time":
    st.header("Active Cases Over Time")
    st.write("Tracking global active cases over time.")

    daywise_data['Active'] = daywise_data['Confirmed'] - daywise_data['Deaths'] - daywise_data['Recovered']
    fig = px.line(daywise_data, x="Date", y="Active", title="Global Active COVID-19 Cases Over Time")
    st.plotly_chart(fig)

# Interactive Map
elif page == "Interactive Map":
    st.header("Interactive COVID-19 Map")
    st.write("Explore global COVID-19 data on an interactive map.")

    country_data_map = country_data.copy()
    fig = px.choropleth(country_data_map, locations="Country/Region", locationmode="country names",
                        color="Confirmed", hover_name="Country/Region",
                        title="Global COVID-19 Confirmed Cases", color_continuous_scale="Reds")
    st.plotly_chart(fig)

# Summary Section
elif page == "Summary":
    st.header("Analysis Summary")
    st.write("""
    **Key Insights:**
    - **New Cases vs Total Cases**: Countries with higher total confirmed cases also tend to report higher new cases, highlighting active outbreaks.
    - **Deaths vs Recoveries**: Globally, recoveries significantly outnumber deaths, indicating medical progress.
    - **Fastest Growing Countries**: Certain countries show exceptionally high growth rates, requiring immediate intervention.
    - **Top Recovery Rate**: Some countries demonstrate impressive recovery percentages, reflecting healthcare resilience.
    - **Region-wise Analysis**: Certain regions are experiencing higher confirmed cases and death rates, indicating a need for targeted interventions.
    - **Daily Trends Analysis**: Tracking daily confirmed, death, and recovery trends gives a clear picture of ongoing COVID-19 progression.
    - **Interactive Map**: Provides a global perspective on the spread of COVID-19, highlighting regional disparities.
    """)
    st.write("### Conclusion:")
    st.write("Analyzing these trends highlights the importance of global cooperation, vaccination, and safety measures to manage COVID-19 effectively.")
