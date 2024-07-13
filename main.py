import numpy as np
import matplotlib.pyplot as plt

def CommandeOnOff(_tMax, _tMin, _tAct, _tPrev):
    if _tPrev < _tAct:
        if _tAct > _tMax:
            return 0
        else:
            return 1
    
    else:
        if _tAct > _tMin:
            return 0
        else:
            return 1

# Paramètres
V = 12              # Tension en volts (V)
R = 1.5             # Résistance en ohms (Ω)
P = V**2 / R        # Puissance de la résistance en watts (W)
retardCapteur = 3.5   # Retard du capteur dû à la dissipation thermique vers le capteur (s)

# Consigne
deltaTMax = 1
deltaTMin = -1

m = 0.6534   # Masse du lit d'impression (kg)
c = 900  # Capacité thermique massique de l'aluminium en J/kg°C (eau)
T_initial = 20  # Température initiale en degrés Celsius (°C)
T_ambiante = 25  # Température ambiante en degrés Celsius (°C)
h_c = 12  # Coefficient de convection thermique en W/m²°C
A = 0.1   # Surface d'échange thermique en mètres carrés (m²)
dt = 0.1  # Intervalle de temps en secondes (s)
t_max = 6000  # Temps maximum en secondes (s)

# Initialisation
temps = np.arange(0, t_max + dt, dt)
consigne = np.zeros_like(temps)
temperature = np.zeros_like(temps)
tabPEff = np.zeros_like(temps)
tabConv = np.zeros_like(temps)
temperature[0] = T_initial

for i in range(0, len(consigne)):
    if i < (len(consigne) / 2):
        consigne[i] = 65
    else:
        consigne[i] = 60

# Simulation
for i in range(1, len(temps)):
    #print(tabP[i])
    #print(i)
    P_convection = h_c * A * (temperature[i-1] - T_ambiante)
    tabConv[i-1] = P_convection
    
    P_effective = (P * CommandeOnOff(consigne[i] + deltaTMax, consigne[i] + deltaTMin, temperature[i - 1 - int(retardCapteur / dt)], temperature[i - 2 - int(retardCapteur / dt)])) - P_convection
    tabPEff[i-1] = P_effective
    
    dT = (P_effective * dt) / (m * c)
    temperature[i] = temperature[i-1] + dT
    
# Calcul performance
# Pour avoir une idée de la performance et la précision du système on va calucler l'aire entre la consigne et la température réelle
Aire = 0
for i in range(1, len(temps)):
    if consigne[i - 1] > consigne [i]:
        consigneMax = consigne[i - 1]
        consigneMin = consigne[i]
    else:
        consigneMax = consigne[i]
        consigneMin = consigne[i - 1]
    
    if temperature[i - 1] > temperature[i]:
        temperatureMax = temperature[i - 1]
        temperatureMin = temperature[i]
    else:
        temperatureMax = temperature[i]
        temperatureMin = temperature[i - 1]
        
    if temperatureMax > consigneMax:
        offset = consigneMax
    else:
        offset = temperatureMax
    
    print('TempMax: ', temperatureMax, '   tempMin: ', temperatureMin, '    consignMax: ', consigneMax, '    consigneMin: ', consigneMin)
    print('aire réel: ', abs(temperatureMax - consigneMax) * dt)
    print('aire en moins: ', (pow(temperatureMax - temperatureMin, 2)/2) + (pow(consigneMax - consigneMin, 2) / 2), '\n')
        
    Aire = Aire + (abs(temperatureMax - consigneMax) * dt) - ((pow(temperatureMax - temperatureMin, 2) / 2) + (pow(consigneMax - consigneMin, 2) / 2))
     
print(Aire)

tabConv[len(temps) - 1] = tabConv[len(temps) - 2]
tabPEff[len(temps) - 1] = tabPEff[len(temps) - 2]

# Résultats
plt.plot(temps, temperature, 'g', label='Température')
plt.plot(temps, tabPEff, 'r', label='Convection')
plt.plot(temps, consigne, 'b', label='Consigne')
plt.xlabel('Temps (s)')
plt.ylabel('Température (°C)')
plt.title('Évolution de la température de la résistance de chauffe')
plt.grid(True)
plt.show()
