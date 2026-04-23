import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np

st.set_page_config(
    page_title="Kerala Logistics Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0f1117; }
  [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
  [data-testid="stSidebar"] * { color: #e6edf3 !important; }
  h1, h2, h3, h4 { color: #e6edf3 !important; }
  .metric-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 14px 18px; text-align: center; margin: 4px 0;
  }
  .metric-card .val { font-size: 1.6rem; font-weight: 700; color: #58a6ff; }
  .metric-card .lbl { font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: .05em; }
  .route-card {
    background: linear-gradient(135deg,#1c2a3a,#162032);
    border: 1px solid #388bfd55; border-radius: 12px; padding: 18px; margin-top: 12px;
  }
  .route-card h4 { color: #58a6ff; margin: 0 0 10px; font-size: 1rem; }
  .route-card .dist { font-size: 2rem; font-weight: 800; color: #f0883e; }
  .route-card .km { font-size: 0.85rem; color: #8b949e; }
  .badge {
    display:inline-block; border-radius:6px; padding:2px 10px; font-size:.75rem;
    font-weight:600; margin:2px;
  }
  .info-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
  .stButton button {
    background: #21262d; border: 1px solid #30363d; color: #e6edf3;
    border-radius: 8px; width: 100%;
  }
  .stButton button:hover { background: #30363d; border-color: #58a6ff; }
  .reset-btn button {
    background: #da3633 !important; border-color: #da3633 !important;
    color: white !important; font-weight: 600;
  }
  div[data-testid="stSelectbox"] label { color: #8b949e !important; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ─── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('distance.xlsx')
    df.columns = ['Sr', 'Distributor_Name', 'City', 'Pincode', 'State',
                  'TNVL', 'NLM', 'Mysore', 'Coimbatore', 'Kottayam']

    # City → lat/lon lookup (Kerala cities - comprehensive)
    city_coords = {
        'KOZHIKODE': (11.2588, 75.7804), 'PALAKKAD': (10.7867, 76.6548),
        'CHAVAKKAD': (10.5869, 76.0174), 'THRISSUR': (10.5276, 76.2144),
        'MUKKAM': (11.3130, 75.9350), 'VENGERI': (11.2450, 75.8000),
        'THALASSERY': (11.7530, 75.4940), 'ANGULARLY': (10.1963, 76.3973),
        'CERUTURUTY': (10.5400, 76.2000), 'KOZHINJAMPARA': (10.6700, 76.6000),
        'PATHAIKKARA': (10.6600, 76.6200), 'ERNAKULAM': (9.9816, 76.2999),
        'FEROKE': (11.1900, 75.8500), 'THIRUVANANTHAPURAM': (8.5241, 76.9366),
        'THENHIPPALAM': (11.0200, 75.9300), 'NORTH PARAVUR': (10.1360, 76.2130),
        'VENGARA': (11.0500, 75.9800), 'PAPPINISSERI': (11.9500, 75.3800),
        'PERUMBAVOOR': (10.1070, 76.4730), 'NATTAKAM': (9.5800, 76.6000),
        'CHOONDAL': (10.5700, 76.1800), 'KANNAMPULLY': (10.5276, 76.2144),
        'IDUKKI': (9.8488, 76.9724), 'ALUVA': (10.1000, 76.3500),
        'VENNALA': (9.9600, 76.3200), 'KAKKANAD': (10.0200, 76.3500),
        'KOCHI': (9.9312, 76.2673), 'ALAPPUZHA': (9.4981, 76.3388),
        'KOLLAM': (8.8932, 76.6141), 'MALAPPURAM': (11.0730, 76.0740),
        'KANNUR': (11.8745, 75.3704), 'KASARGOD': (12.4996, 74.9869),
        'KASARAGOD': (12.4996, 74.9869), 'IRINJALAKUDA': (10.3400, 76.2100),
        'KOTTAYAM': (9.5916, 76.5222), 'CHANGANACHERRY': (9.4480, 76.5430),
        'PATHANAMTHITTA': (9.2648, 76.7870), 'KARUNAGAPPALLY': (9.0590, 76.5360),
        'MAVELIKKARA': (9.2650, 76.5530), 'HARIPAD': (9.2360, 76.4680),
        'AROOR': (9.8700, 76.3400), 'EZHUKONE': (8.9000, 76.8000),
        'PERINAD': (8.8500, 76.8500), 'PUTHUVELY': (9.5500, 76.7000),
        'RANNI': (9.3833, 76.7833), 'PRAMADOM': (9.2000, 76.6000),
        'MATTANNUR': (11.9310, 75.5760), 'PAYYANUR': (12.0970, 75.2010),
        'CHALAD': (11.8700, 75.3500), 'KADIRUR': (12.0200, 75.4000),
        'VENGAPPALLY': (9.5500, 76.6800), 'PUTHUR': (10.5100, 76.2000),
        'OTTAPPALAM': (10.7697, 76.3786), 'VADAKARA': (11.5950, 75.5964),
        'KUTTIPPURAM': (10.9710, 75.9240), 'PARASSALA': (8.3650, 77.0790),
        'THAYALANGADI': (9.1000, 76.5500), 'ARUVAL': (9.8000, 76.4500),
        'KURUPUZHA': (9.0500, 76.5700), 'KADAPPATTOOR': (9.6000, 76.7200),
        'VENJARAMOODU': (8.5800, 77.0500), 'KOTTIYAM': (8.9000, 76.5700),
        'KARUNAGAPPALLI': (9.0590, 76.5360),
    }

    # Normalize city lookup
    def get_coords(city):
        key = city.strip().upper()
        # direct match
        if key in city_coords:
            return city_coords[key]
        # partial match
        for k, v in city_coords.items():
            if k in key or key in k:
                return v
        return (10.1632, 76.6413)  # Kerala center fallback

    df['lat'] = df['City'].apply(lambda c: get_coords(str(c))[0])
    df['lon'] = df['City'].apply(lambda c: get_coords(str(c))[1])

    # Assign region based on latitude
    def assign_region(row):
        lat = row['lat']
        city = str(row['City']).upper()
        if lat >= 11.5 or city in ['THALASSERY', 'PAPPINISSERI', 'KANNUR', 'KASARAGOD', 'THALASSERY']:
            return 'North Kerala Zone'
        elif lat >= 10.8:
            return 'Malabar Belt'
        elif lat >= 9.8:
            return 'Central Kerala Zone'
        elif 'IDUKKI' in city or 'MUNNAR' in city or 'KUMILY' in city or 'KATTAPPANA' in city:
            return 'Highland / Idukki Belt'
        elif lat < 9.8 and lat >= 9.0:
            return 'South Kerala Zone'
        else:
            return 'South Kerala Zone'

    df['Region'] = df.apply(assign_region, axis=1)

    # Override some by city
    highland_cities = ['IDUKKI', 'MUNNAR', 'KATTAPPANA', 'KUMILY', 'THODUPUZHA', 'NATTAKAM']
    for hc in highland_cities:
        df.loc[df['City'].str.upper().str.contains(hc, na=False), 'Region'] = 'Highland / Idukki Belt'

    return df

# ─── Plants / Depots ──────────────────────────────────────────────────────────
plants = {
    'TNVL': {'lat': 8.7714, 'lon': 77.7143, 'label': 'TNVL Plant', 'state': 'Tamil Nadu'},
    'NLM':  {'lat': 13.0827, 'lon': 80.2707, 'label': 'NLM Plant', 'state': 'Tamil Nadu'},
    'Mysore':      {'lat': 12.2958, 'lon': 76.6394, 'label': 'Mysore Depot',      'state': 'Karnataka'},
    'Coimbatore':  {'lat': 11.0168, 'lon': 76.9558, 'label': 'Coimbatore Depot',  'state': 'Tamil Nadu'},
    'Kottayam':    {'lat': 9.5916,  'lon': 76.5222, 'label': 'Kottayam Depot',    'state': 'Kerala'},
}

plant_colors = {
    'TNVL':       '#f0883e',
    'NLM':        '#3fb950',
    'Mysore':     '#bc8cff',
    'Coimbatore': '#ff7b72',
    'Kottayam':   '#ffa657',
}

region_colors = {
    'North Kerala Zone':     'rgba(88, 166, 255, 0.18)',
    'Malabar Belt':          'rgba(63, 185, 80, 0.18)',
    'Central Kerala Zone':   'rgba(188, 140, 255, 0.18)',
    'South Kerala Zone':     'rgba(255, 123, 114, 0.18)',
    'Highland / Idukki Belt':'rgba(255, 166, 87, 0.18)',
}
region_border = {
    'North Kerala Zone':     '#58a6ff',
    'Malabar Belt':          '#3fb950',
    'Central Kerala Zone':   '#bc8cff',
    'South Kerala Zone':     '#ff7b72',
    'Highland / Idukki Belt':'#ffa657',
}
region_marker_color = {
    'North Kerala Zone':     '#58a6ff',
    'Malabar Belt':          '#3fb950',
    'Central Kerala Zone':   '#bc8cff',
    'South Kerala Zone':     '#ff7b72',
    'Highland / Idukki Belt':'#ffa657',
}

# Kerala approximate bounding boxes per region (lat ranges)
region_bounds = {
    'North Kerala Zone':      {'lat_min': 11.5, 'lat_max': 12.8, 'lon_min': 74.9, 'lon_max': 76.0},
    'Malabar Belt':           {'lat_min': 10.8, 'lat_max': 11.5, 'lon_min': 75.4, 'lon_max': 76.4},
    'Central Kerala Zone':    {'lat_min': 9.8,  'lat_max': 10.8, 'lon_min': 76.0, 'lon_max': 77.0},
    'South Kerala Zone':      {'lat_min': 8.3,  'lat_max': 9.8,  'lon_min': 76.4, 'lon_max': 77.3},
    'Highland / Idukki Belt': {'lat_min': 9.4,  'lat_max': 10.5, 'lon_min': 76.6, 'lon_max': 77.4},
}

def region_geojson():
    """Build simple rectangular GeoJSON for each region."""
    features = []
    for name, b in region_bounds.items():
        coords = [[
            [b['lon_min'], b['lat_min']], [b['lon_max'], b['lat_min']],
            [b['lon_max'], b['lat_max']], [b['lon_min'], b['lat_max']],
            [b['lon_min'], b['lat_min']]
        ]]
        features.append({
            "type": "Feature",
            "id": name,
            "properties": {"name": name},
            "geometry": {"type": "Polygon", "coordinates": coords}
        })
    return {"type": "FeatureCollection", "features": features}

def build_map(df, selected_region=None, selected_plant=None, selected_dist=None):
    fig = go.Figure()

    geojson = region_geojson()

    # ── Region fills ──────────────────────────────────────────────────────────
    for feat in geojson['features']:
        rname = feat['properties']['name']
        coords = feat['geometry']['coordinates'][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]

        is_selected = (selected_region == rname)
        opacity = 0.35 if is_selected else 0.12
        line_width = 2.5 if is_selected else 1.2
        color_hex = region_border[rname]

        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode='lines',
            fill='toself',
            fillcolor=f'rgba(88,166,255,0.2)',
            line=dict(color=color_hex, width=line_width),
            name=rname,
            hovertemplate=f'<b>{rname}</b><extra></extra>',
            showlegend=False,
        ))

        # Region label
        mid_lat = (max(lats) + min(lats)) / 2
        mid_lon = (max(lons) + min(lons)) / 2
        fig.add_trace(go.Scattermapbox(
            lat=[mid_lat], lon=[mid_lon],
            mode='text',
            text=[rname],
            textfont=dict(size=10, color=color_hex),
            hoverinfo='skip',
            showlegend=False,
        ))

    # ── Distributors ──────────────────────────────────────────────────────────
    if selected_region:
        region_df = df[df['Region'] == selected_region]
        for _, row in region_df.iterrows():
            is_sel = (selected_dist is not None and
                      row['Distributor_Name'] == selected_dist)
            color = region_marker_color[row['Region']]
            fig.add_trace(go.Scattermapbox(
                lat=[row['lat']], lon=[row['lon']],
                mode='markers',
                marker=dict(
                    size=14 if is_sel else 9,
                    color=color,
                    opacity=1.0 if is_sel else 0.8,
                    symbol='circle',
                ),
                name=row['Distributor_Name'],
                customdata=[[row['Distributor_Name'], row['City'], row['Region']]],
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>'
                    '📍 %{customdata[1]}<br>'
                    '🗺️ %{customdata[2]}<extra></extra>'
                ),
                showlegend=False,
            ))

    # ── Plants / Depots ───────────────────────────────────────────────────────
    for pname, p in plants.items():
        is_sel = (selected_plant == pname)
        ptype = 'Plant' if pname in ('TNVL', 'NLM') else 'Depot'
        fig.add_trace(go.Scattermapbox(
            lat=[p['lat']], lon=[p['lon']],
            mode='markers+text',
            marker=dict(
                size=20 if is_sel else 14,
                color=plant_colors[pname],
                opacity=1.0,
                symbol='star' if pname in ('TNVL', 'NLM') else 'square',
            ),
            text=[pname],
            textposition='top right',
            textfont=dict(size=11, color=plant_colors[pname]),
            name=f'{pname} ({ptype})',
            customdata=[[p['label'], p['state'], ptype]],
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                '📍 %{customdata[1]}<br>'
                f'🏭 {ptype}<extra></extra>'
            ),
            showlegend=True,
        ))

    # ── Route line ────────────────────────────────────────────────────────────
    if selected_plant and selected_dist is not None:
        dist_row = df[df['Distributor_Name'] == selected_dist]
        if not dist_row.empty and selected_plant in df.columns:
            dist_row = dist_row.iloc[0]
            p = plants[selected_plant]
            dist_km = dist_row[selected_plant]
            mid_lat = (p['lat'] + dist_row['lat']) / 2
            mid_lon = (p['lon'] + dist_row['lon']) / 2

            # Dashed animated-style route
            fig.add_trace(go.Scattermapbox(
                lat=[p['lat'], mid_lat, dist_row['lat']],
                lon=[p['lon'], mid_lon, dist_row['lon']],
                mode='lines+markers+text',
                line=dict(width=3, color='#f0883e'),
                marker=dict(size=[0, 12, 0], color='#f0883e', symbol=['circle','circle','circle']),
                text=['', f'📦 {dist_km:.1f} km', ''],
                textfont=dict(size=13, color='#f0883e'),
                textposition='top center',
                hovertemplate=f'<b>Route</b><br>Distance: {dist_km:.1f} km<extra></extra>',
                showlegend=False,
                name='Route',
            ))

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=10.5, lon=76.2),
            zoom=6.5,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#0f1117',
        plot_bgcolor='#0f1117',
        legend=dict(
            bgcolor='#161b22',
            bordercolor='#30363d',
            borderwidth=1,
            font=dict(color='#e6edf3', size=11),
            x=0.01, y=0.99,
            xanchor='left', yanchor='top',
        ),
        height=680,
        uirevision='static',
    )
    return fig

# ─── Session state ────────────────────────────────────────────────────────────
for key, default in [
    ('selected_region', None), ('selected_plant', None),
    ('selected_dist', None), ('click_step', 'plant'),
]:
    if key not in st.session_state:
        st.session_state[key] = default

df = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Kerala Logistics")
    st.markdown("---")

    st.markdown("### 🔍 Filters")
    region_opts = ['All Regions'] + sorted(df['Region'].unique())
    sel_region_filter = st.selectbox('Region', region_opts)
    if sel_region_filter != 'All Regions':
        st.session_state.selected_region = sel_region_filter

    plant_opts = ['Select Plant/Depot…'] + list(plants.keys())
    sel_plant_filter = st.selectbox('Plant / Depot', plant_opts)
    if sel_plant_filter != 'Select Plant/Depot…':
        st.session_state.selected_plant = sel_plant_filter
        st.session_state.click_step = 'dist'

    st.markdown("---")
    st.markdown("### 🎯 Selection Mode")
    if st.session_state.click_step == 'plant':
        st.info("**Step 1:** Select a Plant or Depot from the sidebar above")
    else:
        st.info("**Step 2:** Select a Distributor below")

    # Distributor selector (only when region + plant chosen)
    if st.session_state.selected_region and st.session_state.selected_plant:
        region_dists = df[df['Region'] == st.session_state.selected_region]['Distributor_Name'].tolist()
        dist_opts = ['Select Distributor…'] + region_dists
        sel_dist = st.selectbox('Distributor', dist_opts)
        if sel_dist != 'Select Distributor…':
            st.session_state.selected_dist = sel_dist

    st.markdown("---")
    with st.container():
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("🔄 Reset All Selections"):
            st.session_state.selected_region = None
            st.session_state.selected_plant = None
            st.session_state.selected_dist = None
            st.session_state.click_step = 'plant'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗂️ Region Legend")
    for rname, color in region_border.items():
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
            f'<div style="width:14px;height:14px;background:{color};border-radius:3px;flex-shrink:0;"></div>'
            f'<span style="font-size:0.8rem;color:#e6edf3;">{rname}</span></div>',
            unsafe_allow_html=True
        )
    st.markdown("### 🏭 Plant/Depot Legend")
    for pname, color in plant_colors.items():
        ptype = 'Plant' if pname in ('TNVL', 'NLM') else 'Depot'
        icon = '⭐' if pname in ('TNVL', 'NLM') else '■'
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">'
            f'<div style="width:14px;height:14px;background:{color};border-radius:3px;flex-shrink:0;"></div>'
            f'<span style="font-size:0.8rem;color:#e6edf3;">{icon} {pname} ({ptype})</span></div>',
            unsafe_allow_html=True
        )

# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown("## 📦 Kerala Logistics Dashboard")

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
region_dist_count = len(df[df['Region'] == st.session_state.selected_region]) if st.session_state.selected_region else len(df)
with col1:
    st.markdown(f'<div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Total Distributors</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="val">5</div><div class="lbl">Plants & Depots</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="val">5</div><div class="lbl">Regions</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="val">{region_dist_count}</div><div class="lbl">{"Region" if st.session_state.selected_region else "All"} Distributors</div></div>', unsafe_allow_html=True)
with col5:
    if st.session_state.selected_plant and st.session_state.selected_dist:
        dist_row = df[df['Distributor_Name'] == st.session_state.selected_dist]
        if not dist_row.empty:
            km = dist_row.iloc[0][st.session_state.selected_plant]
            st.markdown(f'<div class="metric-card"><div class="val" style="color:#f0883e;">{km:.0f}</div><div class="lbl">Route Distance (km)</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-card"><div class="val">—</div><div class="lbl">Route Distance (km)</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-card"><div class="val">—</div><div class="lbl">Route Distance (km)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Map + Info Panel
map_col, info_col = st.columns([3, 1])

with map_col:
    fig = build_map(
        df,
        selected_region=st.session_state.selected_region,
        selected_plant=st.session_state.selected_plant,
        selected_dist=st.session_state.selected_dist,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with info_col:
    st.markdown("### 📋 Details")

    # Selected Plant info
    if st.session_state.selected_plant:
        p = plants[st.session_state.selected_plant]
        ptype = 'Plant' if st.session_state.selected_plant in ('TNVL', 'NLM') else 'Depot'
        color = plant_colors[st.session_state.selected_plant]
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid {color}55;border-radius:10px;padding:14px;margin-bottom:12px;">
          <div style="color:{color};font-weight:700;font-size:0.9rem;">🏭 {ptype} Selected</div>
          <div style="color:#e6edf3;font-size:1.1rem;font-weight:700;margin-top:4px;">{st.session_state.selected_plant}</div>
          <div style="color:#8b949e;font-size:0.8rem;">{p['label']}</div>
          <div style="color:#8b949e;font-size:0.8rem;">📍 {p['state']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Selected Region
    if st.session_state.selected_region:
        rcolor = region_border[st.session_state.selected_region]
        r_count = len(df[df['Region'] == st.session_state.selected_region])
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid {rcolor}55;border-radius:10px;padding:14px;margin-bottom:12px;">
          <div style="color:{rcolor};font-weight:700;font-size:0.9rem;">🗺️ Region Active</div>
          <div style="color:#e6edf3;font-size:1rem;font-weight:700;margin-top:4px;">{st.session_state.selected_region}</div>
          <div style="color:#8b949e;font-size:0.8rem;">{r_count} distributors</div>
        </div>
        """, unsafe_allow_html=True)

    # Selected Distributor
    if st.session_state.selected_dist:
        dist_row = df[df['Distributor_Name'] == st.session_state.selected_dist]
        if not dist_row.empty:
            d = dist_row.iloc[0]
            rcolor = region_marker_color[d['Region']]
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid {rcolor}55;border-radius:10px;padding:14px;margin-bottom:12px;">
              <div style="color:{rcolor};font-weight:700;font-size:0.9rem;">📦 Distributor</div>
              <div style="color:#e6edf3;font-size:0.9rem;font-weight:700;margin-top:4px;">{d['Distributor_Name']}</div>
              <div style="color:#8b949e;font-size:0.8rem;">📍 {d['City']}, {d['Pincode']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Route card
    if st.session_state.selected_plant and st.session_state.selected_dist:
        dist_row = df[df['Distributor_Name'] == st.session_state.selected_dist]
        if not dist_row.empty and st.session_state.selected_plant in df.columns:
            d = dist_row.iloc[0]
            km = d[st.session_state.selected_plant]
            ptype = 'Plant' if st.session_state.selected_plant in ('TNVL', 'NLM') else 'Depot'
            st.markdown(f"""
            <div class="route-card">
              <h4>🛣️ Route Analysis</h4>
              <div style="color:#8b949e;font-size:0.75rem;">FROM</div>
              <div style="color:{plant_colors[st.session_state.selected_plant]};font-weight:700;">
                {st.session_state.selected_plant} ({ptype})
              </div>
              <div style="color:#8b949e;font-size:0.75rem;margin-top:8px;">TO</div>
              <div style="color:#e6edf3;font-weight:600;font-size:0.9rem;">{d['Distributor_Name']}</div>
              <div style="color:#8b949e;font-size:0.75rem;">{d['City']}</div>
              <div style="margin-top:14px;">
                <div class="dist">{km:.1f}</div>
                <div class="km">km (road estimate)</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Distances from selected distributor to all plants
    if st.session_state.selected_dist:
        dist_row = df[df['Distributor_Name'] == st.session_state.selected_dist]
        if not dist_row.empty:
            d = dist_row.iloc[0]
            st.markdown("#### All Distances")
            for pname, pdata in plants.items():
                if pname in df.columns:
                    km_val = d[pname]
                    ptype = 'Plant' if pname in ('TNVL', 'NLM') else 'Depot'
                    color = plant_colors[pname]
                    is_sel = pname == st.session_state.selected_plant
                    border = f"border:1.5px solid {color};" if is_sel else ""
                    st.markdown(f"""
                    <div style="background:#1c2028;border-radius:8px;padding:8px 12px;margin:4px 0;{border}display:flex;justify-content:space-between;align-items:center;">
                      <div>
                        <span style="color:{color};font-weight:600;font-size:0.85rem;">{pname}</span>
                        <span style="color:#8b949e;font-size:0.7rem;"> {ptype}</span>
                      </div>
                      <span style="color:#f0883e;font-weight:700;font-size:0.9rem;">{km_val:.0f} km</span>
                    </div>
                    """, unsafe_allow_html=True)

# ─── Bottom: Region Summary Table ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Region Summary")

summary_cols = st.columns(5)
for i, (rname, rcolor) in enumerate(region_border.items()):
    rdf = df[df['Region'] == rname]
    avg_tnvl = rdf['TNVL'].mean()
    avg_nlm = rdf['NLM'].mean()
    avg_mys = rdf['Mysore'].mean()
    avg_cbe = rdf['Coimbatore'].mean()
    avg_ktm = rdf['Kottayam'].mean()
    with summary_cols[i]:
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid {rcolor}44;border-radius:10px;padding:12px;font-size:0.78rem;">
          <div style="color:{rcolor};font-weight:700;margin-bottom:8px;font-size:0.8rem;">{rname}</div>
          <div style="color:#8b949e;">{len(rdf)} distributors</div>
          <div style="margin-top:8px;color:#e6edf3;">Avg distances:</div>
          <div style="color:{plant_colors['TNVL']};">TNVL: {avg_tnvl:.0f} km</div>
          <div style="color:{plant_colors['NLM']};">NLM: {avg_nlm:.0f} km</div>
          <div style="color:{plant_colors['Mysore']};">Mysore: {avg_mys:.0f} km</div>
          <div style="color:{plant_colors['Coimbatore']};">CBE: {avg_cbe:.0f} km</div>
          <div style="color:{plant_colors['Kottayam']};">KTM: {avg_ktm:.0f} km</div>
        </div>
        """, unsafe_allow_html=True)
