
from numpy import *
import matplotlib 
from matplotlib.pyplot import *


matplotlib.use('tkagg')


duree_simu = 1800 # durée de la simulation en secondes
temps_de_boucle = 0.1 # periode de l'algorithme en seconde
temperature_consigne = 60 # température de consigne
index_start = 2 # demarage de la simulation (eviter de sortir des bornes du tableau avec des index négatifs)

########## Constantes physiques ############
V_Alim = 12 # tension d'alimentation de la resistance chauffante en V
Resistance = 1.5 # resistance  de la resistance chauffante en Ohm

coeff_conv = 0.2 # coefficient de convexion
ambiant_T = 20 # temperature de l'ai embiant

capacite_thermique_massique = 900 # capacité thermique de l'aluminium en W/kg*K
densite = 2700 # densité du du lit en kg/m3
volume_lit = 0.22 * 0.22 * 0.005 # volume du lit en m3
masse_lit = densite * volume_lit

capacite_thermique = masse_lit * capacite_thermique_massique # capacité thermique du lit chauffant

delta_mesure = 0.0 # retard de mesure en seconde de la sonde

########## Constantes PID ############
# Coefficients du PID  
#  *(Resistance/(V_Alim * V_Alim )) permet de rendre les coefficient indépendents de la resistance et tension d'alimentation
kp = 1      *(Resistance/(V_Alim * V_Alim ))
ki = 0.1    *(Resistance/(V_Alim * V_Alim ))
kd = 0      *(Resistance/(V_Alim * V_Alim ))
I_max = 20  *(Resistance/(V_Alim * V_Alim ))


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

def onOff(_T, _Tc, _oldCmd) :
	if (_oldCmd == 1) :
		cmd = 1
		
		if (_T > _Tc * 1.01) :
			cmd = 0
	
	else :
		cmd = 0
		
		if (_T < _Tc * 0.99) :
			cmd = 1
	
	return cmd

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
        #cmd[k], I_eT[k]= pid(dt, T[0], temperature_consigne, T[0], I_eT[k-1])
        cmd[k] = 1
        power[k] = cmd_to_power(cmd[k])
        T[k], dissi_pow[k] = evol_T(dt, T[k-1], power[k])
        t[k] = t[k-1] + dt

    #suite de la simulation
    for k in range(offset_mesure if offset_mesure > index_start else index_start,N):
        
        if ((k * temps_de_boucle) < 1000) :
            #calcul du PID
            Tm[k] = T[k-offset_mesure-1]
            #cmd[k], I_eT[k]= pid(dt, Tm[k], temperature_consigne, Tm[k-1], I_eT[k-1])
            cmd[k] = onOff(Tm[k], temperature_consigne, cmd[k-1])

        #enregistrement de la valme
        power[k] = cmd_to_power(cmd[k])
        T[k], dissi_pow[k] = evol_T(dt, T[k-1], power[k])
        t[k] = t[k-1] + dt

    print("offset_mesure : %d" % offset_mesure)
    print("Capacité thermique : %d" % capacite_thermique)

    plot(t, T,'b',label='T')
    plot(t, Tm,'g',label='Tm')
    title('T')
    plot(t, cmd,'r',label='cmd')
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