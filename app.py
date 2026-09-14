import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from materials import WALL_MATERIALS
from physics import check_biot, calculate_hourly_heat_loss

st.set_page_config(page_title="Suraksha Awas", layout="wide")

st.title("Suraksha-Awas: Thermal Shelter Optimizer")
st.markdown("Automated 24-Hour Diurnal Heat Loss & Logistics Calculator for High-Altitude Deployments")
st.divider()
st.markdown("Stage 2 Targets-")
st.markdown("1. Exporting Detailed ANSYS parameter file, for FEA(Finite Element Analysis) for confirmation of Design.")
st.markdown("2. Account for Phase Change Materials Latent Heat, Specific Heats Etc")
st.markdown("3. Bringing in Green House effect with SHGC Windows")
st.markdown("4. Account for Window and Door sizes")
st.markdown("5. Account for Heat Radiated from Soliders Body")
st.markdown("6. Real weather data about tempreature, wind speed, air density, altitude")

st.divider()

st.subheader("1. Shelter Specifications")
col1, col2, col3, col4 = st.columns(4)

with col1:
    l = st.number_input("Length (m)", 2.0,10.0,4.0)
with col2:
    b = st.number_input("Breadth (m)",2.0,10.0,4.0)
with col3:
    h = st.number_input("Height (m)",2.0,5.0,2.5)
with col4:
    thickness = st.number_input("Wall Thickness (m)", 0.05, 0.30,0.10)

col5, col6, col7 = st.columns(3)
with col5:
    target_temp = st.slider("Target Inside Temp (°C)", 5, 25, 15)
with col6:
    h_conv = st.number_input("Convection Coeff (h)",10)
with col7:
    active_material = st.selectbox("Select Material to Graph below:", list(WALL_MATERIALS.keys()))

surface_area = (2 * l * h) + (2 * b * h) + (l * b)

hours = np.arange(0, 24)
T_outside = np.array([-15, -17, -19, -20, -21, -20, -18, -15, -10, -5, -2, 2, 5, 4, 1, -2, -5, -8, -10, -12, -13, -14, -14, -15])

st.divider()
st.subheader("2. Material Efficiency Comparison")

comparison_data = []

for mat_name, k_val in WALL_MATERIALS.items():
    biot_val, err_margin = check_biot(h_conv, thickness, k_val)
    watts, kerosene = calculate_hourly_heat_loss(target_temp, T_outside, surface_area, thickness, k_val, err_margin)
    
    total_kero = sum(kerosene)
    
    biot_status = "Valid (<0.1)" if biot_val <= 0.1 else f"High ({biot_val:.1f}) +15% Penalty"
    
    comparison_data.append({
        "Material": mat_name,
        "k-Value (W/mK)": k_val,
        "Biot Number Status": biot_status,
        "Total Kerosene/Day (Liters)": round(total_kero, 2)
    })

df = pd.DataFrame(comparison_data)

def highlight_selected(row):
    if row['Material'] == active_material:
        return ['background-color: rgba(0, 255, 0, 0.2)'] * len(row)
    return [''] * len(row)

st.dataframe(df.style.apply(highlight_selected, axis=1), use_container_width=True)

st.divider()
st.subheader(f"3. 24-Hour Profile: {active_material}")

k_active = WALL_MATERIALS[active_material]
active_biot, active_err = check_biot(h_conv, thickness, k_active)
active_watts, active_kerosene = calculate_hourly_heat_loss(target_temp, T_outside, surface_area, thickness, k_active, active_err)

col_a, col_b = st.columns(2)
with col_a:
    st.metric(label="Heat Lost (24h)", value=f"{sum(active_watts)/1000:.1f} kW")
with col_b:
    st.metric(label="Kerosene Required (24h)", value=f"{sum(active_kerosene):.2f} Liters")

# The Plotly Chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=hours, y=T_outside, mode='lines+markers', name='Outside Temp (°C)', line=dict(color='cyan')))
fig.add_trace(go.Scatter(x=hours, y=[target_temp]*24, mode='lines', name='Target Inside Temp (°C)', line=dict(color='green', dash='dash')))

scaled_kerosene = [k * 10 for k in active_kerosene]
fig.add_trace(go.Bar(x=hours, y=scaled_kerosene, name='Kerosene Burn Rate (Scaled x10)', marker_color='orange', opacity=0.5))

fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Temperature (°C)", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)