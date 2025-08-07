#!/usr/bin/env python3
"""
IoT Data Dashboard - Shows data from BigQuery
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
from google.cloud import bigquery
import os

# Configure Streamlit page
st.set_page_config(
    page_title="IoT Data Dashboard - BigQuery",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Cloud configuration
PROJECT_ID = "zeltask-staging-464722"

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_bigquery_data(hours_back=2):
    """Get data from BigQuery"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        query = f"""
        SELECT 
            device_id,
            timestamp,
            temperature,
            vibration,
            building,
            floor,
            room,
            device_type,
            is_anomaly
        FROM `{PROJECT_ID}.iot_data.sensor_readings`
        WHERE timestamp >= '{start_time.isoformat()}'
        ORDER BY timestamp DESC
        LIMIT 5000
        """
        
        df = client.query(query).to_dataframe()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
        
    except Exception as e:
        st.error(f"Error fetching data from BigQuery: {e}")
        return pd.DataFrame()

def main():
    st.title("🏭 IoT Sensor Dashboard")
    st.markdown("**Real-time Data from BigQuery Database**")
    st.markdown("*Data flows: IoT Simulator → Pub/Sub → Data Consumer → BigQuery → Dashboard*")
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Time range selection
    hours_back = st.sidebar.slider("Hours of data to show", 1, 24, 2)
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30 seconds)", value=True)
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Fetch data from BigQuery
    with st.spinner("Fetching data from BigQuery..."):
        df = get_bigquery_data(hours_back)
    
    if df.empty:
        st.warning("No data available in BigQuery.")
        st.info("Make sure the IoT simulator and data consumer are running.")
        if auto_refresh:
            time.sleep(30)
            st.rerun()
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Readings", len(df))
    
    with col2:
        unique_devices = df['device_id'].nunique()
        st.metric("Active Devices", unique_devices)
    
    with col3:
        avg_temp = df['temperature'].mean()
        st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
    
    with col4:
        avg_vibration = df['vibration'].mean()
        st.metric("Avg Vibration", f"{avg_vibration:.2f} mm/s")
    
    # Anomaly detection metrics if available
    if 'is_anomaly' in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            anomaly_count = df['is_anomaly'].sum()
            anomaly_rate = (anomaly_count / len(df)) * 100 if len(df) > 0 else 0
            st.metric("Anomalies Detected", f"{anomaly_count} ({anomaly_rate:.1f}%)")
        
        with col2:
            if anomaly_count > 0:
                latest_anomaly = df[df['is_anomaly'] == True]['timestamp'].max()
                if pd.notna(latest_anomaly):
                    st.metric("Latest Anomaly", latest_anomaly.strftime('%H:%M:%S'))
    
    # Time series charts
    st.subheader("📈 Sensor Readings Over Time")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature chart
            fig_temp = px.line(
                df.head(1000), 
                x='timestamp', 
                y='temperature',
                color='device_id',
                title="Temperature Over Time",
                labels={'temperature': 'Temperature (°C)'},
                height=400
            )
            fig_temp.update_layout(showlegend=False)  # Hide legend for cleaner look
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Vibration chart
            fig_vib = px.line(
                df.head(1000), 
                x='timestamp', 
                y='vibration',
                color='device_id',
                title="Vibration Over Time",
                labels={'vibration': 'Vibration (mm/s RMS)'},
                height=400
            )
            fig_vib.update_layout(showlegend=False)  # Hide legend for cleaner look
            st.plotly_chart(fig_vib, use_container_width=True)
    
    # Device distribution
    st.subheader("🏢 Device Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Devices by building
        building_counts = df['building'].value_counts()
        fig_building = px.pie(
            values=building_counts.values,
            names=building_counts.index,
            title="Readings by Building"
        )
        st.plotly_chart(fig_building, use_container_width=True)
    
    with col2:
        # Device types
        if 'device_type' in df.columns:
            device_type_counts = df['device_type'].value_counts()
            fig_device_type = px.bar(
                x=device_type_counts.index,
                y=device_type_counts.values,
                title="Readings by Device Type"
            )
            fig_device_type.update_layout(
                xaxis_title="Device Type",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_device_type, use_container_width=True)
    
    # Recent readings table
    st.subheader("📋 Recent Readings from BigQuery")
    
    # Show recent readings
    display_df = df[['device_id', 'timestamp', 'temperature', 'vibration', 'building', 'floor', 'room']].copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df = display_df.sort_values('timestamp', ascending=False).head(20)
    st.dataframe(display_df, use_container_width=True)
    
    # Data summary
    st.subheader("📊 Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Temperature Statistics:**")
        temp_stats = df['temperature'].describe()
        st.write(temp_stats)
    
    with col2:
        st.write("**Vibration Statistics:**")
        vib_stats = df['vibration'].describe()
        st.write(vib_stats)
    
    # Data freshness info
    if not df.empty:
        latest_reading = df['timestamp'].max()
        time_since_latest = datetime.now() - latest_reading.to_pydatetime().replace(tzinfo=None)
        
        st.sidebar.markdown("---")
        st.sidebar.write("**Data Freshness:**")
        st.sidebar.write(f"Latest reading: {latest_reading.strftime('%H:%M:%S')}")
        st.sidebar.write(f"Time since latest: {int(time_since_latest.total_seconds())} seconds ago")
    
    # Auto refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
