import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import duckdb
import altair as alt

db_path = '../data/subway_data.duckdb'
conn = duckdb.connect(db_path)

#####################  Queries


busiest_stations_output = conn.execute("""
    SELECT * 
    FROM busiest_statios
""").fetchall()

busiest_stations_lat_lon_output = conn.execute("""
    SELECT 
        borough,
        station_complex,
        CAST(latitude AS FLOAT) as latitude,
        CAST(longitude AS FLOAT) as longitude,
        rider_count
    FROM busiest_stations_lat_lon
""").fetchall()

dow_output = conn.execute("""
    SELECT * 
    FROM day_of_week
""").fetchall()

##################### Dataframes

busiest_stations_df = pd.DataFrame(busiest_stations_output, columns=['borough', 'station_complex', 'rider_count'])
busiest_stations_lat_lon_df = pd.DataFrame(busiest_stations_lat_lon_output, columns=['borough', 'station_complex', 'latitude', 'longitude', 'rider_count'])
dow_output_df = pd.DataFrame(dow_output, columns=['borough', 'ride_date', 'rider_count'])


##################### Page configuration and styling

st.set_page_config(
    page_title="NYC Subway Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


##################### Sidebar

with st.sidebar:
    st.title('🚇 NYC Subway Dashboard')
    st.markdown('---')
    
    
    # Make the borough selector more prominent with default value
    st.markdown("### Select Borough")
    boroughs = sorted(busiest_stations_df['borough'].unique())
    option = st.selectbox(
        'Choose a borough to filter the data:',
        options=boroughs,
        index=0
    )
    
    # Add some key metrics in the sidebar
    st.markdown('---')
    st.markdown("### Quick Stats")
    
    total_riders = busiest_stations_df['rider_count'].sum()
    total_stations = len(busiest_stations_df)
    
    st.metric("Total Riders", f"{total_riders:,.0f}", border=True)
    st.metric("Total Stations", f"{total_stations:,.0f}", border=True)

##################### Main Content

# Header section
st.title("NYC Subway Analytics Dashboard")
st.markdown("*New York City's subway system*")
st.markdown("---")

# Top row metrics
metric_col1, metric_col2, metric_col3= st.columns(3)

# Calculate metrics
if option:
    filtered_data = busiest_stations_df[busiest_stations_df['borough'] == option]
else:
    filtered_data = busiest_stations_df

with metric_col1:
    avg_daily_riders = filtered_data['rider_count'].mean()
    st.metric("Average Daily Riders", f"{avg_daily_riders:,.0f}", border=True)

with metric_col2:
    peak_riders = filtered_data['rider_count'].max()
    st.metric("Peak Riders", f"{peak_riders:,.0f}", border=True)

with metric_col3:
    total_riders = filtered_data['rider_count'].sum()
    st.metric("Total Riders", f"{total_riders:,.0f}", border=True)


st.markdown("---")

##################### TOP columns

top_col1, top_col2 = st.columns(2, gap='small')

with top_col1:
    # Station ridership dataframe with progress bars
    st.dataframe(filtered_data.sort_values(by='rider_count', ascending=False),
                column_order=("station_complex", "rider_count"),
                hide_index=True,
                width=None,
                column_config={
                "station_complex": st.column_config.TextColumn(
                    "Station",
                ),
                "rider_count": st.column_config.ProgressColumn(
                    "Rider Count",
                    format="%f",
                    min_value=0,
                    max_value=max(filtered_data.rider_count),
                    )}
                )

        
with top_col2:
    # Seasonal rider count line chart

    filtered_dow_df = dow_output_df[dow_output_df['borough'] == option]
    title = f'Seasonal Rider Count: {option}'

    fig = px.bar(filtered_dow_df.sort_values(by="ride_date"), 
                  x='ride_date',
                  y='rider_count',
                  color='borough',  # Add color by borough
                  title=title)

    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Day of Week",
        yaxis_title="Average Rider Count",
        margin=dict(t=30, l=10, r=10, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

##################### Bottom Plot

# Create a heatmap of ridership by day of week
weekly_riders = conn.execute("""
    SELECT 
        day_of_week,
        borough,
        AVG(rider_count) as avg_riders
    FROM day_of_week
    GROUP BY day_of_week, borough
""").fetchall()

weekly_df = pd.DataFrame(weekly_riders, columns=['day_of_week', 'borough', 'avg_riders'])
weekly_df = weekly_df[weekly_df['borough'] == option]
weekly_pivot = weekly_df.pivot(index='day_of_week', columns='borough', values='avg_riders')

fig_heatmap = px.imshow(weekly_pivot,
                       title='Average Daily Ridership by Borough',
                       color_continuous_scale='viridis')

fig_heatmap.update_layout(
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    margin=dict(t=30, l=10, r=10, b=10)
)

st.plotly_chart(fig_heatmap, use_container_width=True)

