from materials import KEROSENE_J_PER_L as kpl

def check_biot(h_cofficient, thickness, k_wall):
    biot_numer = (h_cofficient*thickness)/k_wall

    if biot_numer>0.01:
        return biot_numer, 1.15
    return biot_numer

def calculate_hourly_heat_loss(target_temp, t_outside, area, thickness, k_wall, err):
    heat_lossWatts = []
    kerosene = []
    for t in t_outside:
        if t < target_temp:
            q_loss = (k_wall * area * (target_temp - t))/thickness

            joules_lost = q_loss * 3600
            litres = (joules_lost/kpl * err)
        else:
            Q_loss = 0
            liters = 0
            
        heat_lossWatts.append(Q_loss)
        kerosene.append(liters)

