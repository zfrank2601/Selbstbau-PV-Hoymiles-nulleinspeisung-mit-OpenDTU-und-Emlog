import requests, time
from requests.auth import HTTPBasicAuth

# Diese Daten müssen angepasst werden: zeile 5 - 12
serial = "112100000000" # Seriennummern der Hoymiles Wechselrichter
maximum_wr = 350 # Maximum ausgabe des wechselrichters

dtuIP = '10.26.x.x' # IP Adresse von OpenDTU
dtuNutzer = 'admin' # OpenDTU Nutzername
dtuPasswort = 'openDTU42' # OpenDTU Passwort

emlogIP = '10.26.x.x' #IP Adresse von Emlog


while True:
    # Nimmt Daten von der openDTU Rest-API und übersetzt sie in ein json-Format
    r = requests.get(url = f'http://{dtuIP}/api/livedata/status/inverters' ).json()

    # Selektiert spezifische Daten aus der json response
    reachable   = r['inverters'][0]['reachable'] # ist DTU erreichbar ?
    producing   = int(r['inverters'][0]['producing']) # produziert der Wechselrichter etwas ?
    altes_limit = int(r['inverters'][0]['limit_absolute']) # wo war das alte Limit gesetzt
    power_dc    = r['inverters'][0]['DC']['0']['Power DC']['v']  # Lieferung DC vom Panel
    power       = r['inverters'][0]['AC']['0']['Power']['v'] # Abgabe BKW AC in Watt

    # Nimmt Daten von der Shelly 3EM Rest-API und übersetzt sie in ein json-Format
    e = requests.get(url = f'http://{emlogIP}/pages/getinformation.php?export&meterindex=1' ).json()
    grid_sum    = e['Wirkleistung_Bezug']['Leistung170'] # Gesamtleistung170
    setpoint    = 0     # Neues Limit in Watt

    # Setzt ein limit auf das Wechselrichter
    def setLimit(Serial, Limit):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'''data={{"serial":"{Serial}", "limit_type":0, "limit_value":{Limit}}}'''  #    AbsolutNonPersistent = 0x0000, // 0 | RelativNonPersistent = 0x0001, // 1 | AbsolutPersistent = 0x0100, // 256 |  RelativPersistent = 0x0101 // 257
        newLimit = requests.post(url=f'http://{dtuIP}/api/limit/config', data=payload, auth=HTTPBasicAuth(dtuNutzer, dtuPasswort), headers=headers)
        print('Konfiguration Status:', newLimit.json()['type'])

    # Werte setzen
    print("aktueller Bezug - Haus:   ",grid_sum)
    if reachable:
        # Setzen Sie den Grenzwert auf den höchsten Wert, wenn er über dem zulässigen Höchstwert liegt.
        # wir weniger bezogen als maximum_wr dann neues Limit ausrechnen
        if (grid_sum) <= 0:  # Aktueller Bezug aus dem Netz. Falls negativ wird ins Netz eingespeist 
            setpoint = grid_sum + power - 5  #Limit -5Watt
            print("setpoint Bezug:",grid_sum,"+ Erzeugung: ",power,"-5 ")
            print("neues Limit berechnet auf ",setpoint,"W")

        if  grid_sum >= 5: # Bezug größer 5 Watt
            setpoint = maximum_wr
            print("setpoint:", setpoint,"W  gesetzt")
            print("neues Limit festgelegt auf ",setpoint)

        print("setze Einspeiselimit auf: ",setpoint, "W")

        # Limit bleibt gleich 
        if setpoint == altes_limit:
            print("setpoint nicht setzen, da Limit wie zuvor")

        # Limit geändert    
        if setpoint != altes_limit:
            print("setpoint setzen, da geändert")
            setLimit(serial, setpoint)
            print("Solarzellenstrom:",power,"  Setpoint:",setpoint,"W")

        time.sleep(5) # wait

    # Wenn der Wechselrichter nicht erreicht werden kann, wird der limit auf maximum gestellt
    if setpoint == 0: setpoint = grid_sum
    if not reachable: setpoint = maximum_wr
