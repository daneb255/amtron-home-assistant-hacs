# Amtron Home Assistant Integration

Eine HACS Custom Integration für die Mennekes Amtron Wallbox mit Netzwerkanbindung.

## Funktionen

- 📊 **Status-Sensoren** für Ladestand, Leistung, Strom und mehr
- ⚙️ **Steuerelement** für Ladenodus, Ladeaction und andere Parameter
- 🔄 **Automatische Updates** alle 30 Sekunden
- 📈 **Statistik-Endpunkte** für Tag, Woche, Monat, Jahr
- 🏷️ **RFID-Whitelist-Management** per Service
- 📋 **Ladehistorie** per Service
- 🔌 **Lokal nur** – keine Cloud, kein Internet erforderlich

## Installation

### 1. HACS-basierte Installation (empfohlen)

1. Öffne Home Assistant und navigiere zu **Settings** → **Devices & Services** → **HACS**
2. Klicke auf **Custom Repositories** (oben rechts)
3. Gebe folgendes ein:
   - **Repository URL**: `https://github.com/lephisto/amtron`
   - **Category**: `Integration`
4. Klicke **Create**
5. Suche nach "Amtron Wallbox" und klicke **Install**
6. Starte Home Assistant neu

### 2. Manuelle Installation

1. Lade das Repository herunter oder clone es:

   ```bash
   git clone https://github.com/lephisto/amtron.git
   ```

2. Kopiere den Integrationscode in dein Home-Assistant-Verzeichnis:

   ```bash
   cp -r amtron/custom_components/amtron ~/.homeassistant/custom_components/
   ```

3. Starte Home Assistant neu

## Konfiguration

### Über die UI (empfohlen)

1. Gehe zu **Settings** → **Devices & Services** → **Integrations**
2. Klicke **Create Integration** und suche nach "Amtron"
3. Fülle die Einstellungen aus:
   - **Host / IP**: IP-Adresse oder Hostname der Wallbox (z. B. `192.168.1.100`)
   - **Use Modbus-TCP**: Aktivieren, wenn Daten über Modbus (Port 502) gelesen werden sollen
   - **DevKey / APP-PIN**: Nur erforderlich, wenn **Use Modbus-TCP** deaktiviert ist
   - **PIN2** (Optional): Nur nötig, wenn du Whitelist/ChargeRecords verwenden willst
   - **Name**: Ein Name für die Wallbox in Home Assistant
   - **Port**: Standard HTTP: `25000`, Standard Modbus: `502`
   - **Base Path**: Standard: `/MHCP/1.0` (ändern nur wenn nötig)

4. Bestätige die Konfiguration

## Verfügbare Entitäten

### Sensoren

- Wallbox Name, Modell, Firmware
- Aktueller Ladenodus, Ladezustand
- Leistung, Strom, Energie geladen
- Tarifanzeige, Tarif-Kosten
- Solar-Anteil

### Bedienelemente

- **Charging Mode** (Select): Wechsel zwischen Remote, HomeManager, Time
- **Charging Control** (Select): Start, Pause, Continue, Terminate
- **Auto Charge** (Switch): Automatisches Laden aktivieren
- **Excess Energy Only** (Switch): Nur mit Überschussenergie laden
- **Remote Current** (Number): Maximaler Ladestrom (0–32 A)
- **Battery Capacity** (Number): EV-Batteriekapazität für Energy Manager
- **Energy Demand** (Number): Wunsch-Lademenge in Wh
- **Remaining Time** (Number): Verbleibende Zeit in Minuten
- **Solar Price** (Number): Preis für Solarenergie

Hinweis: Im Modbus-Modus sind nur Funktionen aktiv, die laut Modbus-Registertabelle schreibbar sind (z. B. Charging Control, Remote Current).

### Services

#### `amtron.add_whitelist`

Fügt einen RFID-Tag zur Whitelist hinzu (Autorisierung).

```yaml
service: amtron.add_whitelist
data:
  device_id: <Wallbox Device ID>
  uid: "04AB12CD34EF56"
  name: "Mein Auto"
```

#### `amtron.remove_whitelist`

Entfernt einen RFID-Tag aus der Whitelist.

```yaml
service: amtron.remove_whitelist
data:
  device_id: <Wallbox Device ID>
  uid: "04AB12CD34EF56"
```

#### `amtron.get_chargerecords`

Ruft Ladehistorie ab (Unix-Timestamps).

```yaml
service: amtron.get_chargerecords
data:
  device_id: <Wallbox Device ID>
  start_time: 1609459200
  end_time: 1609545600
```

## Anforderungen

- Home Assistant ≥ 2024.1.0
- Mennekes Amtron Wallbox mit Netzwerk-Modul
- Lokale Netzwerkverbindung zur Wallbox
- DevKey (APP-PIN) aus der Gerätedokumentation
- Optionale PIN2 für Whitelist/ChargeRecords-Zugriff

## Troubleshooting

### Integration wird nicht gefunden

- Stelle sicher, dass HACS installiert ist und die Integrationsliste aktualisiert wurde
- Home Assistant neu starten

### "Cannot connect" Fehler

- Prüfe, ob die Wallbox unter der angegebenen IP erreichbar ist: `ping <IP>`
- Prüfe, ob die DevKey korrekt eingegeben wurde
- Prüfe, dass die Wallbox im selben Netzwerk ist
- Aktiviere den WiFi-Zugang in der Wallbox-App, falls nötig

### Whitelist/ChargeRecords funktionieren nicht

- PIN2 ist erforderlich, um auf diese Endpunkte zuzugreifen
- Überprüfe, dass PIN2 korrekt eingegeben wurde

## API-Dokumentation

Detaillierte API-Dokumentation findest du in der [GitHub-API-Dokumentation](https://github.com/lephisto/amtron/tree/master/docs/api).

## Support & Beiträge

- **Issues**: [GitHub Issues](https://github.com/lephisto/amtron/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/lephisto/amtron/discussions)

## Lizenz

Siehe [LICENSE](../LICENSE)
