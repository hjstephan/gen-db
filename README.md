# Gen Full-Stack - Biological Network Database

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

**Full-Stack-Anwendung zur Speicherung, Verwaltung und Analyse biologischer Netzwerke mit PostgreSQL-Backend, FastAPI-REST-API und modernem Web-Frontend.**

Nutzt den [Subgraph Algorithmus](https://github.com/hjstephan/subgraph) (O(n³)) zur effizienten Suche nach strukturellen Ähnlichkeiten in metabolischen Pfaden, Protein-Interaktionsnetzwerken und Gen-Regulationsnetzwerken.


## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Architektur](#-architektur)
- [Schnellstart](#-schnellstart)
- [Installation](#-installation)
- [API-Dokumentation](#-api-dokumentation)
- [Beispiel-Workflows](#-beispiel-workflows)
- [Datenbank-Schema](#-datenbank-schema)
- [Konfiguration](#-konfiguration)
- [Entwicklung](#-entwicklung)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)



## ✨ Features

### Kernfunktionalität
- ✅ **Netzwerk-Verwaltung**: Erstellen, Abrufen, Aktualisieren, Löschen biologischer Netzwerke
- ✅ **Subgraph-Suche**: Finde alle Netzwerke in der DB, die ein Query-Netzwerk enthalten
- ✅ **Automatische Signaturen**: Vorberechnung von Spalten-Signaturen beim Speichern
- ✅ **Intelligentes Pre-Filtering**: Nur relevante Kandidaten (nach node_count, edge_count) werden verglichen
- ✅ **Subgraph Algorithmus**: O(n³) durch zyklische Rotationen

### Technologie
- 🚀 **FastAPI Backend**: Moderne, schnelle REST-API mit automatischer OpenAPI-Dokumentation
- 🗄️ **PostgreSQL**: Robuste relationale Datenbank mit JSONB-Support für Matrizen
- 🎨 **Responsive Frontend**: Modern UI mit HTML5, CSS3 und Vanilla JavaScript
- 🐳 **Docker-Ready**: PostgreSQL-Container mit docker-compose
- 📊 **Adjacency Matrix Format**: Effiziente Speicherung als 2D-Arrays

### Biologische Anwendungen
- 🧬 Metabolische Pfad-Analyse (KEGG, Reactome)
- 🔬 Protein-Interaktionsnetzwerke (STRING, BioGRID)
- 🧪 Gen-Regulationsnetzwerke
- 💊 Medikamenten-Wirkstoff-Vergleiche
- 🦠 Vergleichende Systembiologie zwischen Organismen



## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                            │
│                   (http://localhost:8000)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   app.py     │  │  database.py │  │   crud.py    │       │
│  │  REST API    │→ │  Connection  │→ │  + Subgraph  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Docker)                   │
│  ┌──────────────────────┐  ┌────────────────────────┐       │
│  │ biological_networks  │  │  network_matrices      │       │
│  │ - network_id (PK)    │  │  - network_id (FK)     │       │
│  │ - name               │  │  - node_labels[]       │       │
│  │ - network_type       │  │  - adjacency_matrix[][]│       │
│  │ - organism           │  │  - signature_array[]   │       │
│  └──────────────────────┘  └────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Datenfluss bei Subgraph-Suche:**
1. User gibt Query-Matrix im Frontend ein
2. Frontend sendet POST /api/networks/search
3. Backend lädt Kandidaten aus PostgreSQL (Pre-Filter)
4. Für jeden Kandidaten: SubgraphComparator.compare()
5. Nur Matches (keep_B, keep_either) werden zurückgegeben
6. Frontend zeigt Ergebnisse an



## 🚀 Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/hjstephan/gen-db.git
cd gen-db

# 2. PostgreSQL starten
sudo docker-compose up -d

# 3. Python-Umgebung einrichten
cd backend
python3 -m venv venv
source venv/bin/activate

# 4. Dependencies installieren
pip install -r requirements-dev.txt

# 5. Backend starten
python3 -m backend.app

# 6. Browser öffnen
open http://localhost:8000
```

**Das war's!** Die Anwendung läuft jetzt mit Beispieldaten (Glycolysis, DNA_Damage_Response).



## 📦 Installation

### Voraussetzungen

- Python 3.8 oder höher
- Docker & Docker Compose (für PostgreSQL)
- Git

### Schritt-für-Schritt

#### 1. Repository klonen
```bash
git clone https://github.com/hjstephan/gen-db.git
cd gen-db
```

#### 2. PostgreSQL-Datenbank starten
```bash
docker-compose up -d
```

Überprüfe den Status:
```bash
docker ps | grep gen_postgres
```

#### 3. Datenbank initialisieren (automatisch beim ersten Start)
Das `init_db.sql` Skript wird automatisch ausgeführt und erstellt:
- Tabellen `biological_networks` und `network_matrices`
- Indizes für Performance
- Beispieldaten (Glycolysis, DNA_Damage_Response)

Manuelle Überprüfung:
```bash
docker exec -it gen_postgres psql -U dbuser -d gen
gen=# \dt
gen=# SELECT name, node_count FROM biological_networks;
gen=# \q
```

#### 4. Python-Backend einrichten
```bash
cd backend

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

Dies installiert:
- FastAPI & Uvicorn (Web-Framework)
- psycopg2-binary (PostgreSQL-Adapter)
- numpy (Matrix-Operationen)

#### 5. Backend starten
```bash
python app.py
```

Erwartete Ausgabe:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 6. Frontend öffnen
Öffne deinen Browser und navigiere zu:
```
http://localhost:8000
```



## 📚 API-Dokumentation

Die API bietet automatische OpenAPI-Dokumentation unter:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpunkte

#### GET /api/networks
Hole alle gespeicherten Netzwerke.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "network_id": 1,
      "name": "Glycolysis",
      "network_type": "metabolic",
      "organism": "Homo sapiens",
      "node_count": 7,
      "edge_count": 6,
      "node_labels": ["Glucose", "G6P", "F6P", "FBP", "DHAP", "G3P", "Pyruvate"],
      "created_at": "2025-01-14T10:30:00"
    }
  ]
}
```

#### GET /api/networks/{network_id}
Hole spezifisches Netzwerk mit Adjacency Matrix.

**Response:**
```json
{
  "success": true,
  "data": {
    "network_id": 1,
    "name": "Glycolysis",
    "node_labels": ["Glucose", "G6P", "F6P"],
    "adjacency_matrix": [[0,1,0], [0,0,1], [0,0,0]],
    "signature_array": [1, 130, 260]
  }
}
```

#### POST /api/networks
Erstelle neues Netzwerk.

**Request Body:**
```json
{
  "name": "My_Pathway",
  "network_type": "metabolic",
  "organism": "E. coli",
  "description": "Custom pathway",
  "node_labels": ["A", "B", "C"],
  "adjacency_matrix": [[0,1,0], [0,0,1], [0,0,0]]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "network_id": 3,
    "name": "My_Pathway",
    "node_count": 3,
    "edge_count": 2,
    "signature_hash": "a1b2c3..."
  }
}
```

#### POST /api/networks/search
Suche nach Subgraph-Matches.

**Request Body:**
```json
{
  "node_labels": ["Glucose", "G6P"],
  "adjacency_matrix": [[0,1], [0,0]]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "network_id": 1,
      "name": "Glycolysis",
      "match_type": "subgraph",
      "subgraph_result": "keep_B"
    }
  ]
}
```

**Match-Typen:**
- `exact`: Query ist identisch mit Kandidat (keep_either)
- `subgraph`: Query ist Subgraph von Kandidat (keep_B)

#### DELETE /api/networks/{network_id}
Lösche Netzwerk (CASCADE löscht auch Matrix).

**Response:**
```json
{
  "success": true,
  "message": "Network deleted"
}
```

#### GET /api/health
Health-Check für Monitoring.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```



## 💡 Beispiel-Workflows

### Workflow 1: Metabolischen Pfad speichern und suchen

**1. Erstelle vollständigen Glykolyse-Pfad**
```javascript
// Im Frontend: "Neues Netzwerk erstellen"
Name: "Full_Glycolysis"
Typ: metabolic
Organismus: Homo sapiens
Knoten: Glucose, G6P, F6P, FBP, DHAP, G3P, Pyruvate

Adjacency Matrix: 7x7
[0,1,0,0,0,0,0]
[0,0,1,0,0,0,0]
[0,0,0,1,0,0,0]
[0,0,0,0,1,1,0]
[0,0,0,0,0,1,0]
[0,0,0,0,0,0,1]
[0,0,0,0,0,0,0]
```

**2. Erstelle partiellen Pfad**
```javascript
Name: "Partial_Glycolysis"
Knoten: Glucose, G6P, F6P

Adjacency Matrix: 3x3
[0,1,0]
[0,0,1]
[0,0,0]
```

**3. Suche nach partiellem Pfad**
- Wechsle zu Tab "Subgraph-Suche"
- Gib "Glucose, G6P, F6P" als Such-Knoten ein
- Matrix: wie oben
- Klicke "Subgraph suchen"

**Ergebnis:** Findet "Full_Glycolysis" als Match! ✅

### Workflow 2: Protein-Interaktionsnetzwerk analysieren

**1. DNA-Schaden-Antwort-Netzwerk**
```javascript
Name: "DNA_Damage_Full"
Typ: protein
Organismus: Homo sapiens
Knoten: p53, MDM2, ATM, DNA-PK, CHK2

Matrix: 5x5 (siehe Beispieldaten)
```

**2. Suche nach p53-MDM2-Interaktion**
```javascript
Knoten: p53, MDM2
Matrix: [[0,1], [1,0]]  // Bidirektionale Interaktion
```

**Ergebnis:** Findet "DNA_Damage_Full" ✅

### Workflow 3: Vergleichende Analyse

**Verwende Python-Script:**
```python
import requests
import numpy as np

# Lade E. coli Glykolyse
response = requests.get('http://localhost:8000/api/networks/1')
ecoli_network = response.json()['data']

# Lade H. sapiens Glykolyse
response = requests.get('http://localhost:8000/api/networks/2')
human_network = response.json()['data']

# Vergleiche direkt
from subgraph import SubgraphComparator
comp = SubgraphComparator()

result = comp.compare(
    np.array(ecoli_network['adjacency_matrix']),
    np.array(human_network['adjacency_matrix'])
)

print(f"Vergleich: {result}")
# Output: keep_either (identisch) oder keep_B (Human enthält E. coli)
```



## 🗄️ Datenbank-Schema

### Tabelle: `biological_networks`
```sql
CREATE TABLE biological_networks (
    network_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    network_type VARCHAR(50),      -- 'metabolic', 'protein', 'gene_regulation'
    organism VARCHAR(100),
    description TEXT,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabelle: `network_matrices`
```sql
CREATE TABLE network_matrices (
    network_id INTEGER PRIMARY KEY REFERENCES biological_networks(network_id) ON DELETE CASCADE,
    node_labels TEXT[] NOT NULL,           -- Array: ['Glucose', 'G6P', ...]
    adjacency_matrix INTEGER[][] NOT NULL, -- 2D-Array: [[0,1,0], [0,0,1], ...]
    signature_array BIGINT[] NOT NULL,     -- Vorberechnete Signaturen
    signature_hash VARCHAR(64)             -- SHA-256 Hash
);
```

### Indizes
```sql
CREATE INDEX idx_networks_type ON biological_networks(network_type);
CREATE INDEX idx_networks_organism ON biological_networks(organism);
CREATE INDEX idx_networks_node_count ON biological_networks(node_count);
CREATE INDEX idx_matrices_hash ON network_matrices(signature_hash);
```



## ⚙️ Konfiguration

### Datenbank-Verbindung

Bearbeite `backend/database.py`:
```python
DATABASE_CONFIG = {
    'dbname': 'gen',
    'user': 'dbuser',
    'password': 'dbpassword',
    'host': 'localhost',
    'port': 5432
}
```

Für Produktion: Verwende Umgebungsvariablen!
```python
import os

DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'gen'),
    'user': os.getenv('DB_USER', 'dbuser'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}
```

### CORS-Konfiguration

Für externe Frontends, bearbeite `backend/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Spezifische Domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```



## 🛠️ Entwicklung

### Lokale Entwicklungsumgebung

```bash
# PostgreSQL im Hintergrund
docker-compose up -d

# Backend mit Auto-Reload
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Frontend (statisch über FastAPI)
# Bearbeite frontend/index.html
# Änderungen sind sofort sichtbar bei Reload
```

### Tests ausführen

```bash
cd backend
pytest tests/
```

### Code-Style

```bash
# Black Formatter
black backend/*.py

# Linting
flake8 backend/*.py

# Type Checking
mypy backend/*.py
```

### Debugging

**Backend-Logs:**
```bash
# Im Terminal, wo app.py läuft
# Zeigt Subgraph-Suche Debug-Output:
🔍 Subgraph-Suche: 2 Kandidaten für Query (n=3, e=2)
  ✅ Match: Full_Glycolysis (keep_B)
  ❌ No match: DNA_Damage (keep_both)
✨ Gefunden: 1 Matches
```

**Datenbank-Abfragen:**
```bash
docker exec -it gen_postgres psql -U dbuser -d gen

gen=# SELECT name, node_count, edge_count FROM biological_networks;
gen=# SELECT network_id, signature_hash FROM network_matrices;
```



## 🚢 Deployment

### Produktion mit Docker

**1. Erstelle `Dockerfile` für Backend:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Update `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: gen
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - gen_network

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      - postgres
    networks:
      - gen_network

networks:
  gen_network:

volumes:
  postgres_data:
```

**3. Mit Environment-File:**
```bash
# .env
DB_USER=dbuser
DB_PASSWORD=secure_password_here
```

**4. Starten:**
```bash
docker-compose up -d --build
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
    }
}
```

### SSL mit Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com
```



## 🐛 Troubleshooting

### PostgreSQL startet nicht
```bash
# Prüfe, ob Port 5432 belegt ist
lsof -i :5432

# Stoppe und entferne Container
docker-compose down
docker-compose up -d
```

### Backend-Verbindungsfehler
```bash
# Prüfe DB-Verbindung
docker exec -it gen_postgres psql -U dbuser -d gen -c "SELECT 1"

# Prüfe Backend-Logs
docker logs gen_backend  # falls Docker
# oder im Terminal, wo app.py läuft
```

### Frontend lädt nicht
```bash
# Prüfe, ob Backend läuft
curl http://localhost:8000/api/health

# Prüfe Browser-Konsole (F12) für JavaScript-Fehler
```

### Langsame Suche
```bash
# Prüfe Anzahl der Netzwerke
docker exec -it gen_postgres psql -U dbuser -d gen \
  -c "SELECT COUNT(*) FROM biological_networks"

# Erstelle fehlende Indizes
docker exec -it gen_postgres psql -U dbuser -d gen \
  -c "CREATE INDEX IF NOT EXISTS idx_networks_node_count ON biological_networks(node_count)"
```
