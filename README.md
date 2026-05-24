# Mennekes Amtron Wallbox – Home Assistant HACS Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-%3E%3D2024.1-blue.svg)](https://www.home-assistant.io)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-green.svg)](LICENSE)

Steuere und überwache deine **Mennekes Amtron Wallbox** direkt in Home Assistant – lokal, ohne Cloud, ohne YAML. Diese HACS Custom Integration bindet Amtron-Ladestationen mit Netzwerkanbindung (AMTRON Compact, AMTRON Charge Control) vollständig in dein Smart-Home ein.

> **Basiert auf** [lephisto/amtron](https://github.com/lephisto/amtron) – die reverse-engineerte API-Dokumentation stammt von dort und bildet die Grundlage dieser Integration.

---

## Voraussetzungen

- Home Assistant ≥ 2024.1
- [HACS](https://hacs.xyz) installiert
- Mennekes Amtron Wallbox mit aktivierter Netzwerkanbindung (WLAN/LAN)
- APP-PIN / DevKey aus den Geräteeinstellungen

---

## Installation

### Via HACS (empfohlen)

1. Öffne Home Assistant → **Einstellungen** → **HACS**
2. Klicke auf **Benutzerdefinierte Repositories** (oben rechts)
3. Füge das Repository hinzu:
   - **URL**: `https://github.com/daneb255/amtron-home-assistant-hacs`
   - **Kategorie**: `Integration`
4. Klicke **Hinzufügen**, suche dann nach **"Amtron Wallbox"** und installiere die Integration
5. Starte Home Assistant neu

### Manuell

```bash
git clone https://github.com/daneb255/amtron-home-assistant-hacs.git
cp -r amtron-home-assistant-hacs/custom_components/amtron ~/.homeassistant/custom_components/
# Home Assistant neu starten
```

---

## Einrichtung

1. **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Suche nach **"Amtron"**
3. Fülle die Felder aus:

| Feld | Beschreibung | Beispiel |
| --- | --- | --- |
| Host / IP | IP-Adresse der Wallbox im Netzwerk | `192.168.1.100` |
| DevKey / APP-PIN | Aus den Geräteeinstellungen | `1234` |
| PIN2 | Optional – für Whitelist-Zugriff | – |
| Name, Port, Base Path | Standardwerte in der Regel korrekt | – |

---

## Funktionsumfang

| Kategorie | Details |
| --- | --- |
| **Sensoren (20+)** | Ladestatus, Ladeleistung (kW), Energie (kWh), Sitzungsstatistik, Netzspannung, Temperatur |
| **Steuerelemente (5+)** | Lademodus, Maximalstrom, Solar-Priority, Phasenwahl |
| **Services** | RFID-Whitelist verwalten, Ladehistorie abrufen |
| **Lokal & privat** | Reine LAN/WLAN-Kommunikation – keine Cloud, keine externen Server |
| **UI-basiert** | Vollständige Einrichtung über die Home Assistant Oberfläche, kein YAML nötig |

---

## Dokumentation

Detaillierte Infos zu allen Entities, Service-Aufrufen, Troubleshooting und API-Anforderungen:

- [Entity- & Service-Dokumentation](custom_components/amtron/README.md)
- [Reverse-Engineered API-Docs (lephisto/amtron)](https://github.com/lephisto/amtron/tree/master/docs/api) – inkl. Node-RED Flows, Grafana Dashboards und Telegraf Configs

---

## Support & Issues

- **Integrationsfehler**: [GitHub Issues](https://github.com/daneb255/amtron-home-assistant-hacs/issues)
- **API-Fragen**: [lephisto/amtron Issues](https://github.com/lephisto/amtron/issues)

---

## Lizenz

MIT – siehe [LICENSE](LICENSE)
