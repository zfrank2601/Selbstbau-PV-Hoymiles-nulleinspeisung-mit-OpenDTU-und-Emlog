# Nulleinspeisung Hoymiles HM-350 mit OpenDTU & Emlog via Python Steuerung


Dies ist ein Python-Skript, das den aktuellen Hausverbrauch mit Emlog ausliest, die Nulleinspeisung berechnet und die Ausgangsleistung eines Hoymiles-Wechselrichters mit Hilfe der OpenDTU entsprechend anpasst. Somit wird kein unnötiger Strom ins Betreibernetz abgegeben.


## Autoren und Anerkennung
- Dieses Skript ist ein Fork von https://github.com/Selbstbau-PV/Selbstbau-PV-Hoymiles-nulleinspeisung-mit-OpenDTU-und-Shelly3EM, das wiederum von: https://gitlab.com/p3605/hoymiles-tarnkappe angepasst von Shelly3M auf Emlog
- Ein großes Lob und Dank an die OpenDTU community: https://github.com/tbnobody/OpenDTU

Shelly3EM-Infos finden Sie hier: https://selbstbau-pv.de/wissensbasis/nulleinspeisung-hoymiles-hm-1500-mit-opendtu-python-steuerung/

Zu Emlog kommen demnächst Infos.

Version vom 11.03.23
  - div. Fixes, da Emlog den wirklichen Bezug darstellt. Solarproduktion ist dort schon eingerechnet.
  - limit_type=0 da, bei limit_type=1 der "relative" Wert gesetzt werden muss.

Version  vom 13.03.23
  - Änderungen an aktueller OpenDTU-Api mit übernommen

Version vom 17.03.23
  - Script optimiert, Änderungen des WR-Limits optimiert (habe nur nen HM350)
