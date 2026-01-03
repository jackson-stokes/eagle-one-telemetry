import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Init page setup
st.set_page_config(
    page_title="Eagle One: Cloud Monitor", 
    layout="wide"
)

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    st.error("Configuration file 'config.json' not found.")
    st.stop()

# Loading the data from CSV file
@st.cache_data
def load_data():
    try:
        file_path = config['machine_info']['output_file']
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    
df = load_data()

# Sidebar / Filters
st.sidebar.header("Filter Telemetry")
min_quality = st.sidebar.slider("Filter by Quality Score", 0.0, 10.0, 0.0)

if not df.empty:
    filtered_df = df[df['quality_score'] >= min_quality]
else:
    filtered_df = df
    

# Main Dashboard UI
st.title("Eagle One: Live Telemetry")
st.markdown(f"**Machine ID:** {config['machine_info']['id']}")

if df.empty:
    st.error("Data file not found. Run 'data_generator.py' first.")
    st.stop()
    
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
avg_quality = filtered_df['quality_score'].mean()
total_shots = len(filtered_df)
avg_pressure = filtered_df['pressure_bar'].mean()

# 3 Quality Buckets
critical_count = len(filtered_df[filtered_df['quality_score'] < 7.0])
warning_count = len(filtered_df[(filtered_df['quality_score'] >= 7.0)
                                & (filtered_df['quality_score'] < 8.0)])
good_count = len(filtered_df[filtered_df['quality_score'] >= 8.0])

col1.metric("Total shots", total_shots)
col2.metric("Avg Pressure", f"{avg_pressure:.2f} bar")

delta_color = "normal" if avg_quality > 8.0 else "inverse"
col3.metric("Health Score", f"{avg_quality:.1f} / 10", delta_color=delta_color)
col4.metric("Warnings (7-8)", warning_count, delta_color="off") 
col5.metric("Critical (< 7)", critical_count, delta_color="inverse")

st.markdown("---")

# Chart Row 1: Pressure vs Extraction Time
col_left, col_right = st.columns([2.5, 1], gap="medium")

with col_left:
    st.subheader("Extraction Precision Analysis")
    fig_scatter = px.scatter(
        filtered_df,
        x='extraction_sec',
        y='pressure_bar',
        color='quality_score',
        size='quality_score',
        height=400,
        hover_data=['temp_celsius', 'quality_score'],
        color_continuous_scale='RdYlGn',
        title="Shot Quality Analysis",
        labels={'extraction_sec': 'Shot Time (sec)', 
                'pressure_bar': 'Pressure (bar)'}
    )
    
    # Box to represent "target zone"
    target_p = config['targets']['pressure']
    target_t = config['targets']['extraction_time']
    
    fig_scatter.add_shape(type="rect",
        x0=target_t - 2.5, x1=target_t + 2.5, 
        y0=target_p - 0.5, y1=target_p + 0.5,
        line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot"),
        label=dict(text="Target Zone", font=dict(size=10))
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("Distribution")
    
    fig_histogram = px.histogram(
        filtered_df, 
        x='quality_score',
        nbins=20,
        title="Quality Distribution", 
        height=400
    )
    st.plotly_chart(fig_histogram, use_container_width=True)
    
# Chart Row 2: Temperature Drift
st.subheader("Boiler Temperature Stability")

fig_line = px.line(filtered_df, x='timestamp', y='temp_celsius', 
                   title="Boiler Temp Over Time", markers=True)

alert_temp = config['targets']['temperature'] - 0.7
fig_line.add_hline(y=alert_temp, line_dash='dash', line_color='red', annotation_text="Low Temp Alert")

st.plotly_chart(fig_line, use_container_width=True)

#Expand Data
with st.expander("View Raw Sensor Logs"):
    st.dataframe(filtered_df.sort_values(by='timestamp', ascending=False))

