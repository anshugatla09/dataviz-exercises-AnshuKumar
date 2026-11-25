import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion
DATA = Path(__file__).resolve().parent.parent / "data" / "world_happiness_2023.csv"
df = pd.read_csv(DATA)
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']
global_avg = df['Score'].mean()

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-global_avg:+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

left, right = st.columns(2)

# Chart 1 — top N countries (from Step 5)
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white',
             title=f'Happiest {top_n} Countries in 2023 - {selected_region}',
             height=600)
fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 8.0]))
left.plotly_chart(fig, width='stretch')

# Chart 2 — NEW: each region's average vs the global average.
# The meaningful midpoint is the global average (difference = 0):
# blue = happier than the world average, red = less happy.
region_avg = df.groupby('Region', as_index=False)['Score'].mean()
region_avg['Diff'] = region_avg['Score'] - global_avg
region_avg = region_avg.sort_values('Diff')

fig2 = px.bar(region_avg, x='Diff', y='Region', orientation='h',
              color='Diff',
              color_continuous_scale='RdBu',      # diverging scale
              color_continuous_midpoint=0,         # centre the colours on 0
              labels={'Diff': 'Difference from global average', 'Region': ''},
              template='plotly_white',
              title='Regional Happiness vs Global Average (2023)',
              height=600)

# mark and label the midpoint
fig2.add_vline(x=0, line_dash='dash', line_color='grey')
fig2.add_annotation(x=0, y=1.0, yref='paper', yanchor='bottom',
                    text=f'Global average = {global_avg:.2f}',
                    showarrow=False, font=dict(color='grey', size=11))

fig2.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                   coloraxis_showscale=False)
right.plotly_chart(fig2, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")
