import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as graphing
from export import generate_ansys_apdl

from materials import WALL_MATERIALS
from physics import check_biot, generate_weather_curves, calculate_hourly_heat_loss

st.set_page_config(page_title="Suraksha Awas", layout="wide")

st.title("Suraksha Awas: Thermal Shelter Optimizer")
st.markdown("Automated 24-Hour Diurnal Heat Loss & Logistics Calculator")
st.divider()

st.markdown("""
Stage 2 Targets-

1. Exporting **Detailed ANSYS parameter file**, for FEA confirmation of Design.

2. Account for Phase Change Materials Latent Heat, Specific Heats Etc

3. Bringing in Green House effect with SHGC Windows

4. Account for Window and Door sizes

5. Account for Heat Radiated from Soldiers Body

6. Real weather data about temperature, wind speed, air density, altitude

7. Track OVER HEATING at Noon
""")
st.divider()


col1, col2, col3 = st.columns(3)

with col1:

    st.subheader("1. Architecture")
    l = st.number_input("Length (m)", 4.0)
    b = st.number_input("Breadth (m)", 4.0)
    h = st.number_input("Height (m)", 2.5)

    thickness = st.number_input("Wall Thickness (m)", 0.10)

with col2:
    st.subheader("2. Glazing & Materials")

    wimdow_area = st.number_input("South Window Area (m²)", 0.0, 10.0, 2.0)
    shgc = st.slider("Solar Heat Gain Coefficient (SHGC)", 0.0, 1.0, 0.6)
    active_material = st.selectbox("Wall Material", list(WALL_MATERIALS.keys()))
    h_conv = st.number_input("Convection Coeff (h)",10)

with col3:
    st.subheader("3. Environment")
    target_temp = st.slider("Target Inside Temp (°C)", 5, 25, 15)
    t_max = st.number_input("Daytime High Temp (°C)", 5)
    t_min = st.number_input("Nighttime Low Temp (°C)", -25)
    peak_solar = st.number_input("Peak Solar Irradiance (W/m²)", 1000)

surface_area = (2 * l * h) + (2 * b * h) + (l * b) - wimdow_area

T_outside, solar_irradiance = generate_weather_curves(t_min, t_max, peak_solar)
hours = np.arange(0, 24)

st.divider()
st.subheader("Material Efficiency Comparison")

comparison_data = []
for mat_name, k_val in WALL_MATERIALS.items():
    biot_val, err_margin = check_biot(h_conv, thickness, k_val)
    watts, kerosene = calculate_hourly_heat_loss(
        target_temp, T_outside, solar_irradiance, surface_area, thickness, k_val, wimdow_area, shgc, err_margin
    )
    if biot_val<= 0.1:
        biot_status = "Valid"
    else:
        biot_status = "High (+15% Penalty)"
    comparison_data.append({
        "Material": mat_name,
        "k-Value": k_val,
        "Biot Status": f"{round(biot_val, 2)} - {biot_status}",
        "Kerosene/Day (Liters)": round(sum(kerosene), 2)
    })









df = pd.DataFrame(comparison_data)

def highlight_selected(row):
    if row['Material'] == active_material:
        return ['background-color: rgba(0, 255, 0, 0.4)'] * len(row)
    return [''] * len(row)

st.dataframe(df.style.apply(highlight_selected, axis=1))

st.divider()
st.subheader(f"24-Hour Thermal Profile: {active_material}")

k_active = WALL_MATERIALS[active_material]
active_biot, active_err = check_biot(h_conv, thickness, k_active)
active_watts, active_kerosene = calculate_hourly_heat_loss(
    target_temp, T_outside, solar_irradiance, surface_area, thickness, k_active, wimdow_area, shgc, active_err
)

col_a, col_b = st.columns(2)
with col_a:
    st.metric(label="Net Heat Lost (24h)", value=f"{round(sum(active_watts)/1000, 1)} kW")
with col_b:
    st.metric(label="Kerosene Required (24h)", value=f"{round(sum(active_kerosene), 1)} Liters")


st.divider()
st.subheader("Exporting ADPL")
ansys_script_text = generate_ansys_apdl(l,b,h,thickness,active_material,k_active)

st.markdown("Export current geometry and material parameters to ANSYS Mechanical for 3D FEA meshing.")

st.download_button(
    label="⬇️ Download ANSYS APDL Script (.mac)",
    data=ansys_script_text,
    file_name=f"suraksha_shelter_{active_material}.mac",
    mime="text/plain"
)





fig = graphing.Figure()
fig.add_trace(graphing.Scatter(x=hours, y=T_outside, mode='lines+markers', name='Outside Temp (°C)', line=dict(color='cyan')))
fig.add_trace(graphing.Scatter(x=hours, y=[target_temp]*24, mode='lines', name='Target Inside Temp (°C)', line=dict(color='green', dash='dash')))

oil_scaled = [k * 10 for k in active_kerosene]
fig.add_trace(graphing.Bar(x=hours, y=oil_scaled, name='Kerosene Burn Rate (Scaled x10)', marker_color='orange', opacity=0.7))

fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Temperature (°C)", template="plotly_dark")
st.plotly_chart(fig)