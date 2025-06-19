import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="River Water Quality Dashboard", page_icon=":bar_chart:", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.title("Predicting River Water Quality using Environmental Indicators")

# File upload
f1 = st.file_uploader("Upload a CSV/XLSX file", type=["csv", "xlsx", "xls"])
if f1 is not None:
    df = pd.read_csv(f1)
else:
    default_path = "sample_water_quality_data.csv"
    df = pd.read_csv(default_path)
    st.info("Using default dataset from local path.")
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])

# Sidebar filters
st.sidebar.header("Filter Data")
stations = st.sidebar.multiselect("Select Stations", options=df['Station'].unique(), default=df['Station'].unique())
start_date = st.sidebar.date_input("Start Date", df['Date'].min())
end_date = st.sidebar.date_input("End Date", df['Date'].max())

filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
                 (df['Date'] <= pd.to_datetime(end_date)) & 
                 (df['Station'].isin(stations))]

# Main content
with st.container():
    st.subheader("Dataset Overview")
    st.write(f"Showing {len(filtered_df)} records.")
    st.dataframe(filtered_df, use_container_width=True)

    # KPIs
    st.subheader("Key Water Quality Indicators (Averages)")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Avg pH", f"{filtered_df['pH'].mean():.2f}" if 'pH' in filtered_df else "N/A")
    k2.metric("Avg DO (mg/l)", f"{filtered_df['DO'].mean():.2f}" if 'DO' in filtered_df else "N/A")
    k3.metric("Avg BOD (mg/l)", f"{filtered_df['BOD'].mean():.2f}" if 'BOD' in filtered_df else "N/A")
    k4.metric("Avg WQI", f"{filtered_df['WQI'].mean():.2f}" if 'WQI' in filtered_df else "N/A")

# Charts section
st.subheader("Visual Insights")

# Group by Station and sum BOD
station_bod_df = filtered_df.groupby(by=['Station'], as_index=False)["BOD"].sum()

# Layout columns for side-by-side charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Station-wise Total BOD")
    fig1 = px.bar(
        station_bod_df,
        x='Station',
        y='BOD',
        text=station_bod_df['BOD'].apply(lambda x: f"{x:.2f}"),
        template='seaborn',
        color='BOD'
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("WQI Distribution by Station")
    station_wqi_df = filtered_df.groupby('Station', as_index=False)['WQI'].mean()
    fig2 = px.pie(
        station_wqi_df,
        values='WQI',
        names='Station',
        hole=0.5,
        title='Average WQI Share by Station'
    )
    fig2.update_traces(textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

cl1, cl2 = st.columns(2)

# Column 1: Category Data
with cl1:
    with st.expander("Water Quality Categories View"):
        # Create categories based on WQI
        bins = [0, 50, 100, 150, 200]  # Example bins for WQI
        labels = ['Poor', 'Fair', 'Good', 'Excellent']  # Example labels for WQI categories

        # Create a new column 'Category' by binning 'WQI' values
        category_df = filtered_df.copy()
        category_df['Category'] = pd.cut(category_df['WQI'], bins=bins, labels=labels, right=False)

        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name='water_quality_categories.csv', mime='text/csv', help='Click here to download data as CSV file')
# WQI by Station
    st.subheader("Average WQI by Station")
    if 'WQI' in filtered_df.columns:
        station_avg = filtered_df.groupby('Station')['WQI'].mean().reset_index()
        fig2 = px.bar(station_avg, x='Station', y='WQI', color='WQI', title='WQI Across Stations')
        st.plotly_chart(fig2, use_container_width=True)

    # Time Series Trends
    st.subheader("Time Series Trends")
    possible_params = ['pH', 'DO', 'BOD', 'Turbidity', 'WQI']
    existing_params = [param for param in possible_params if param in filtered_df.columns]
    if existing_params:
        fig = px.line(filtered_df, x="Date", y=existing_params, title="Water Parameters Over Time")
        st.plotly_chart(fig, use_container_width=True)

st.subheader('Time Series Analysis of WQI')
filtered_df['month_year'] = filtered_df['Date'].dt.to_period('M')

# Group by 'month_year' and sum the WQI (Corrected the column name here)
linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].astype(str))['WQI'].sum()).reset_index()

# Create a line chart using Plotly
fig1 = px.line(linechart, x='month_year', y='WQI', labels={'WQI': 'Water Quality Index'}, height=500, width=1000, template='gridon')

# Display the chart in Streamlit
st.plotly_chart(fig1, use_container_width=True)
with st.expander('View Data of Time Series'):
    st.write(linechart.T.style.background_gradient(cmap='Blues'))

    # Convert the DataFrame to CSV and enable the download button
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name='Timeseries.csv', mime='text/csv')
with st.container():
    st.subheader('Station-wise WQI Distribution')
    # Group the data by station and calculate the average WQI for each station
    station_wqi_df = filtered_df.groupby('Station', as_index=False)['WQI'].mean()
    
    
# Scatter plot: Relationship between BOD and pH, using Temperature as point size
data1 = px.scatter(filtered_df, x='BOD', y='pH', size='Temperature')

# Update the layout and titles for the chart
data1.update_layout(
    title=dict(
        text='Relationship between BOD and pH using Scatter Plot',
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(
            text='BOD (mg/l)',
            font=dict(size=19)
        )
    ),
    yaxis=dict(
        title=dict(
            text='pH',
            font=dict(size=19)
        )
    )
)



st.subheader(" WQI vs Key Chemical Parameters")
if all(col in filtered_df.columns for col in ['WQI', 'pH', 'DO', 'BOD']):
        fig_ph = px.scatter(filtered_df, x='pH', y='WQI', trendline="ols", title="WQI vs pH")
        st.plotly_chart(fig_ph, use_container_width=True)

        fig_do = px.scatter(filtered_df, x='DO', y='WQI', trendline="ols", title="WQI vs DO")
        st.plotly_chart(fig_do, use_container_width=True)

        fig_bod = px.scatter(filtered_df, x='BOD', y='WQI', trendline="ols", title="WQI vs BOD")
        st.plotly_chart(fig_bod, use_container_width=True)
else:
        st.warning("One or more required columns (WQI, pH, DO, BOD) are missing.")



st.subheader("WQI vs Key Chemical Parameters with Threshold Lines")

# Check if required columns exist
required_columns = ['WQI', 'pH', 'DO', 'BOD']

def add_threshold_lines(fig):
    # Excellent: WQI ≥ 90
    fig.add_hline(y=90, line_dash="dash", line_color="green")
    fig.add_annotation(x=0.5, y=90, xref="paper", yref="y", text="Excellent (≥90)",
                       showarrow=False, font=dict(size=12, color="green"), align="center", 
                       yshift=10)  # Manually add annotation

    # Good: WQI 70–90
    fig.add_hline(y=70, line_dash="dash", line_color="orange")
    fig.add_annotation(x=0.5, y=70, xref="paper", yref="y", text="Good (70–90)",
                       showarrow=False, font=dict(size=12, color="orange"), align="center", 
                       yshift=10)  # Manually add annotation

    # Poor: WQI < 70
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.add_annotation(x=0.5, y=0, xref="paper", yref="y", text="Poor (<70)",
                       showarrow=False, font=dict(size=12, color="red"), align="center", 
                       yshift=10)  # Manually add annotation

    return fig



if all(col in filtered_df.columns for col in required_columns):
    
    # --- WQI vs pH ---
    fig_ph = px.scatter(filtered_df, x='pH', y='WQI',
                        trendline="ols",
                        title="WQI vs pH",
                        labels={'pH': 'pH Level', 'WQI': 'Water Quality Index'})
    fig_ph = add_threshold_lines(fig_ph)
    st.plotly_chart(fig_ph, use_container_width=True)

    # --- WQI vs DO ---
    fig_do = px.scatter(filtered_df, x='DO', y='WQI',
                        trendline="ols",
                        title="WQI vs Dissolved Oxygen (DO)",
                        labels={'DO': 'DO (mg/L)', 'WQI': 'Water Quality Index'})
    fig_do = add_threshold_lines(fig_do)
    st.plotly_chart(fig_do, use_container_width=True)

    # --- WQI vs BOD ---
    fig_bod = px.scatter(filtered_df, x='BOD', y='WQI',
                         trendline="ols",
                         title="WQI vs Biological Oxygen Demand (BOD)",
                         labels={'BOD': 'BOD (mg/L)', 'WQI': 'Water Quality Index'})
    fig_bod = add_threshold_lines(fig_bod)
    st.plotly_chart(fig_bod, use_container_width=True)

else:
    st.warning("One or more required columns (WQI, pH, DO, BOD) are missing from the dataset.")
# Display the scatter plot in Streamlit
st.plotly_chart(data1, use_container_width=True)
scv=df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data',data=csv,file_name="Data.csv",mime="text/csv")