import requests, time
from requests.auth import HTTPBasicAuth

# Diese Daten müssen angepasst werden: zeile 5 - 17
serial = "1120000000" # Seriennummern der Hoymiles Wechselrichter
maximum_wr = 350 # Maximum ausgabe des wechselrichters

dtuIP = '10.x.x.x' # IP Adresse von OpenDTU
dtuNutzer = 'admin' # OpenDTU Nutzername
dtuPasswort = 'password' # OpenDTU Passwort

emlogIP = '10.x.x.x' #IP Adresse von EMLOG
zielwert = 5 # geplanter Bezug aus Netz
obere_abw = 10 # erlaubte Abweichung über den Zielwert
untere_abw = 10 # erlaubte Abweichung unter den Zielwert
sleep_time = 9 # Sleep_Time des Scripts
verbrauch_min = 50 #wenn Verbrauch größer dann auf maximum_wr

while True:
    # Nimmt Daten von der openDTU Rest-API und übersetzt sie in ein json-Format
    r = requests.get(url = f'http://{dtuIP}/api/livedata/status/inverters' ).json()

    # Selektiert spezifische Daten aus der json response
    reachable   = r['inverters'][0]['reachable'] # ist DTU erreichbar ?
    producing   = int(r['inverters'][0]['producing']) # produziert der Wechselrichter etwas ?
    altes_limit = int(r['inverters'][0]['limit_absolute']) # wo war das alte Limit gesetzt
    voltage_ac      = r['inverters'][0]['AC']['0']['Voltage']['v']  # Spannung DC vom Panel
    voltage_dc      = r['inverters'][0]['DC']['0']['Voltage']['v']  # Spannung DC vom Panel
    power_dc        = r['inverters'][0]['AC']['0']['Power DC']['v'] # Lieferung DC vom Panel
    power       = r['inverters'][0]['AC']['0']['Power']['v'] # Abgabe BKW AC in Watt
    frequency       = r['inverters'][0]['AC']['0']['Frequency']['v'] #
    efficiency       = r['inverters'][0]['AC']['0']['Efficiency']['v'] #
    temperature       = r['inverters'][0]['INV']['0']['Temperature']['v'] # Abgabe BKW AC in Watt    
    e = requests.get(url = f'http://{emlogIP}/pages/getinformation.php?export&meterindex=1' ).json()
    grid_sum    = e['Wirkleistung_Bezug']['Leistung170'] # Gesamtleistung170
    bezugkwh    = e['Kwh_Bezug']['Kwh182'] #Bezug182
    setpoint    = 0     # Neues Limit in Watt
    tagesleistung   = r['total']['YieldDay']['v']                   # Tagesleistung aller Strings
    gesamtleistung  = r['total']['YieldTotal']['v']                 # Gesamtleistung aller Strings

    # Setzt ein limit auf das Wechselrichter
    def setLimit(Serial, Limit):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'''data={{"serial":"{Serial}", "limit_type":0, "limit_value":{Limit}}}'''
        newLimit = requests.post(url=f'http://{dtuIP}/api/limit/config', data=payload, auth=HTTPBasicAuth(dtuNutzer, dtuPasswort), headers=headers)
        print('Konfiguration Status:', newLimit.json()['type'])

    # Werte setzen
    verbrauch = grid_sum + power
    setpoint= verbrauch - zielwert
    print("aktueller Bezug - Wohnung kpl: ", verbrauch)
    print("aktueller Bezug - Stromzähler: ", grid_sum)
    print("aktuelle  Erzeugung - Solar  : ", power)
    print("neues Limit berechnet auf    : ", setpoint)
    if reachable:
        # Setzen Sie den Grenzwert auf den höchsten Wert, wenn er über dem zulässigen Höchstwert liegt.
        if ( setpoint >= maximum_wr or verbrauch > verbrauch_min ):
            print("setze Maximum                : ", maximum_wr)
            setpoint = maximum_wr

        # falls setpoint zu weit vom aktuellen Limit abweicht
        if ( setpoint < altes_limit - untere_abw or setpoint > altes_limit + obere_abw ):
            print("setze Wechselrichterlimit auf: ", setpoint)
            setLimit(serial, setpoint)

        if  ( setpoint >  altes_limit or setpoint < altes_limit):
            print("aktiviere Setpoint           : ",setpoint)
            setLimit(serial, setpoint)
        else:
            print("Setpoint unverändert         : ",setpoint)
    print("------------------------------------------")
    time.sleep(sleep_time) # wait


    if setpoint == 0: setpoint = grid_sum
    if not reachable: setpoint = maximum_wr
