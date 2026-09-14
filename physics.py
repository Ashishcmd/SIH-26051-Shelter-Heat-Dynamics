import math
from materials import KEROSENE_J_PER_L as kpl

def check_biot(h_cofficient, thickness, k_wall):
    biot_numer = (h_cofficient * thickness) / k_wall
    if biot_numer > 0.1:
        return biot_numer, 1.15
    return biot_numer, 1.0

def generate_weather_curves(t_min, t_max, peak_solar):
    t_outside = []
    solar_irradiance = []
    
    t_mean = (t_max + t_min) / 2
    t_amp = (t_max - t_min) / 2
    
    for hour in range(24):
        temp = t_mean - t_amp * math.cos(math.pi * (hour - 4) / 12)
        t_outside.append(temp)
        
        if 6 <= hour <= 18:
            sun = peak_solar * math.cos(math.pi * (hour - 12) / 12)
            solar_irradiance.append(max(0, sun))
        else:
            solar_irradiance.append(0)
            
    return t_outside, solar_irradiance

def calculate_hourly_heat_loss(target_temp, t_outside, solar_irradiance, area, thickness, k_wall, window_area, shgc, err):
    heat_lossWatts = []
    kerosene = []
    
    for i in range(24):
        t = t_outside[i]
        sun_intensity = solar_irradiance[i]
        
        if t < target_temp:
            q_loss = (k_wall * area * (target_temp - t)) / thickness
        else:
            q_loss = 0
            
        q_solar = sun_intensity * window_area * shgc
        
        net_loss = q_loss - q_solar
        
        if net_loss > 0:
            joules_lost = net_loss * 3600
            liters = (joules_lost / kpl) * err
        else:
            liters = 0
            
        heat_lossWatts.append(max(0, net_loss))
        kerosene.append(liters)
        
    return heat_lossWatts, kerosene