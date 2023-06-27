
from numpy import *
import matplotlib 
from matplotlib.pyplot import *


matplotlib.use('tkagg')


duree_simu = 1000 # durée de la simulation en secondes
temps_de_boucle = 0.02 # periode de l'algorithme en seconde
temperature_consigne = 30 # température de consigne
index_start = 2 # demarage de la simulation (eviter de sortir des bornes du tableau avec des index négatifs)

########## Constantes physiques ############
V_Alim = 24 # tension d'alimentation de la resistance chauffante en V
Resistance = 10 # resistance  de la resistance chauffante en Ohm

coeff_conv = 5 # coefficient de convexion
ambiant_T = 20 # temperature de l'ai embiant
capacite_thermique = 100 # capacité thermiquer du lit chauffant

delta_mesure = 0.0 # retard de mesure en seconde de la sonde

########## Constantes PID ############
# Coefficients du PID
kp = 1
ki = 0.1
kd = 0
I_max = 20


########## variables globales modèl physiques ############



########## variables globales PID ############

#old_T = ambiant_T 
#I_eT = 0 # Integrale de l'erruer de tezmpérature


# évolution de la température en fonction du temp et de la puissance de chauffe
# _dt : temps ecoulé depuis la boucle précédente
# _T : température réel de l'instant t
# _pow : puissance de chauffe
def evol_T(_dt, _T, _pow) :
    dissip_pow = (_T - ambiant_T) * coeff_conv 
    new_T = _T + ((_pow - dissip_pow) * _dt) / capacite_thermique
    return new_T, dissip_pow # température  à l'instant t+_dt

# asservissement PID
# _dt : temps ecoulé depuis la boucle précédente
# _T : température mesurée
# _Tc : température de conssigne
def pid(_dt, _T, _Tc, _old_T, _I_eT) :
    
    dT = (_T - _old_T)/_dt #Calcule de la dérive de la tempéradure 
    eT = _Tc - _T #Calcule de l'erreur de température
    _I_eT += ki*eT*_dt # Caclcul de l'integrale de l'ereure de température
    if(_I_eT > I_max):
        _I_eT = I_max
    if(_I_eT < 0):
        _I_eT = 0
    # calcul du PID
    cmd = kp * eT + _I_eT + kd * dT 
    
    if(cmd < 0):
        cmd = 0
    if(cmd > 1):
        cmd = 1

    # enregistrement de _T pour la boucle suivante
    #old_T = _T
    return cmd, _I_eT


#convertire la commande, rapport cyclique entre 0 et 1, en puissance de chauffe en W
# _cmd : rapport cyclique entre 0 et 1
# output : power ; puissance de chauffe en W
def cmd_to_power(_cmd):
    power = _cmd * V_Alim * V_Alim / Resistance
    return power

if __name__ == '__main__':
    # N : nombre de pas de simulation
    N = (int) (duree_simu / temps_de_boucle) + index_start 

    # Initialisation des tableaux de stockage des données
    T = zeros(N)  # température
    Tm = zeros(N) # température capté par la sonde
    cmd = zeros(N)  # rapport cyclique de commande
    power = zeros(N) # puissance de chauffe
    dissi_pow = zeros(N)# puissance dissipée

    t = zeros(N) # temp écoulé en seconde

    I_eT = zeros(N) #intégrale de l'erreur
    # retard de mesure de la sond en pas de simulation
    offset_mesure = int(delta_mesure / temps_de_boucle)

    dt = temps_de_boucle

    #initialiser les premières valeurs qui ne font pas partie de la simulation
    for k in range(index_start):
        T[k] = ambiant_T
        Tm[k] = ambiant_T
        cmd[k] = 0
        power[k] = 0
        I_eT[k] = 0
        t[k] = t[k-1] + dt

    # première étape de la simulation, la sonde ne capte pas encore l'évolution de la température
    for k in range(index_start,offset_mesure if offset_mesure > index_start else index_start):
        Tm[k] = ambiant_T
        cmd[k], I_eT[k]= pid(dt, T[0], temperature_consigne, T[0], I_eT[k-1])
        power[k] = cmd_to_power(cmd[k])
        T[k], dissi_pow[k] = evol_T(dt, T[k-1], power[k])
        t[k] = t[k-1] + dt

    #suite de la simulation
    for k in range(offset_mesure if offset_mesure > index_start else index_start,N):
        
        #calcul du PID
        Tm[k] = T[k-offset_mesure-1]
        cmd[k], I_eT[k]= pid(dt, Tm[k], temperature_consigne, Tm[k-1], I_eT[k-1])

        #enregistrement de la valme
        power[k] = cmd_to_power(cmd[k])
        T[k], dissi_pow[k] = evol_T(dt, T[k-1], power[k])
        t[k] = t[k-1] + dt

    print("offset_mesure : %d" % offset_mesure)

    plot(t, T,'b',label='T')
    plot(t, Tm,'g',label='Tm')
    title('T')
    plot(t, 30*cmd,'r',label='cmd')
    legend(loc="best")
    title('cmd')
    #figure()
    #plot(t, power)
    #title('power')
    #figure()
    figure()
    plot(t, I_eT)
    title('I_eT')
    figure()
    plot(t, dissi_pow)
    title('dissi_pow')
    show()
        

#__main()