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
#    power_dc    = r['inverters'][0]['0']['Power DC']['v']  # Lieferung DC vom Panel
    power       = r['inverters'][0]['AC']['0']['Power']['v'] # Abgabe BKW AC in Watt
#print("altes_limit",altes_limit,"+power",power)
    # Nimmt Daten von der Shelly 3EM Rest-API und übersetzt sie in ein json-Format
    e = requests.get(url = f'http://{emlogIP}/pages/getinformation.php?export&meterindex=1' ).json()
    grid_sum    = e['Wirkleistung_Bezug']['Leistung170'] # Gesamtleistung170
    setpoint    = 0     # Neues Limit in Watt

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
    print("aktueller Erzeugung - Solar  : ", power)
    print("neues Limit berechnet auf    : ", setpoint)
    if reachable:
        # Setzen Sie den Grenzwert auf den höchsten Wert, wenn er über dem zulässigen Höchstwert liegt.
        if ( setpoint >= maximum_wr or verbrauch > verbrauch_min ):
            print("setze Maximum                : ", maximum_wr)
            setpoint = maximum_wr

        # falls setpoint zu weit vom aktuellen Limit abweicht
        if ( setpoint < altes_limit - untere_abw or setpoint > altes_limit + obere_abw ):
            print("setze Wechselrichterlimit auf: ", setpoint)
            # neues limit setzen

        if  ( setpoint >  altes_limit or setpoint < altes_limit):
            print("aktiviere Setpoint           : ",setpoint)
            setLimit(serial, setpoint)
        else:
            print("Setpoint unverändert         : ",setpoint)
    print("------------------------------------------")
    time.sleep(sleep_time) # wait


    if setpoint == 0: setpoint = grid_sum
    if not reachable: setpoint = maximum_wr
