# IoT Challenge 3 - Node-RED, MQTT, ZigBee CSV, LoRaWAN

Questo repository raccoglie il materiale per la Challenge 3 del corso IoT.
La challenge e' divisa in due parti:

- Part 1: implementazione di un flow Node-RED che usa MQTT, legge `challenge3.csv`, produce CSV, pubblica dati ZigBee e aggiorna ThingSpeak.
- Part 2: esercizio LoRaWAN su packet success rate con modello ALOHA.

Deadline indicata nelle slide:

```text
12 maggio 2026, 23:59
```

## Contenuto della cartella `docs`

### Materiale della challenge

- `docs/Challenge3.pdf`
  - PDF ufficiale della challenge.
  - 20 pagine.
  - Contiene specifiche Node-RED, esercizio LoRaWAN, deliverable, formato CSV, regole di consegna e deadline.

- `docs/Challenge3_parsing.md`
  - Parsing dettagliato del PDF.
  - Include descrizione pagina per pagina, testo estratto, interpretazione visuale delle slide e sintesi operativa.

- `docs/challenge3.csv`
  - Dataset da processare in Node-RED.
  - 5218 righe.
  - `Packet Number` va da `0` a `5217`.
  - Colonne:

```text
Packet Number
Device Name Source
Device Type Source
Source Address
Destination Address
Device Name Destination
Device Type Destination
Source Address ZigBee
Device Name ZigBee Source
Device Type ZigBee Source
Destination Address ZigBee
Device Name ZigBee Destination
Device Type ZigBee Destination
Human Command
Human Command Origin
Packet Type
Command String
```

- `docs/transcript challenge presentatio.txt`
  - Trascrizione della presentazione della challenge.
  - Chiarimenti principali:
    - ThingSpeak va limitato a un invio ogni 20 secondi.
    - Il limite di 200 vale sui messaggi ID ricevuti dalla subscription, non necessariamente sul numero di righe/costi/chart generati.
    - Per l'esercizio LoRaWAN va usato il modello ALOHA.

### Materiale di lezione

- `docs/4. MQTT.pdf`
  - Slide sul protocollo MQTT.
  - Contenuti utili:
    - MQTT e' publish/subscribe.
    - C'e' un broker e ci sono client publisher/subscriber.
    - Mosquitto si puo' usare come broker locale.
    - Comando generico per avviare Mosquitto:

```powershell
mosquitto -p 1884 -v
```

    - Comando subscriber:

```powershell
mosquitto_sub -h localhost -p 1884 -t challenge3/id_generator -v
```

    - Comando publisher:

```powershell
mosquitto_pub -h localhost -p 1884 -t challenge3/id_generator -m "{`"id`":7123,`"timestamp`":1710930219}"
```

- `docs/5. Node-Red.pdf`
  - Slide su ThingSpeak e Node-RED.
  - Contenuti utili:
    - Node-RED si avvia con `node-red`.
    - UI locale:

```text
http://localhost:1880
```

    - Nodi utili per la challenge:
      - `inject`
      - `function`
      - `mqtt in`
      - `mqtt out`
      - `file`
      - `http request`
      - `delay`
      - `debug`
      - `ui_chart`
    - ThingSpeak accetta update HTTP con:

```text
https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE
```

    - ThingSpeak limita gli update a circa un messaggio ogni 20/30 secondi.

- `docs/6. LoRa.pdf`
  - Slide su LoRa e LoRaWAN.
  - Contenuti utili:
    - LoRa usa parametri come spreading factor, bandwidth, coding rate, transmission power e carrier frequency.
    - A SF piu' alto corrispondono maggiore range/sensibilita' ma anche maggiore airtime.
    - Le collisioni dipendono dalla sovrapposizione temporale.
    - Per ALOHA:

```text
success rate = exp(-2 * N * lambda * airtime)
```

    - `N` e' il numero di nodi.
    - `lambda` e' il rate di trasmissione per nodo.
    - `airtime` e' il tempo in aria del pacchetto.

- `docs/transcript lecture.txt`
  - Trascrizione breve/parziale di una lezione.
  - Conferma in modo generico che il bit rate dipende da spreading factor, coding rate e bandwidth.

- `docs/transcript lecture 2.txt`
  - Trascrizione molto breve/parziale.
  - Non aggiunge requisiti operativi specifici per la challenge.

### Notebook LoRaSim

- `docs/LoRasim.ipynb`
  - Notebook completo per simulazioni LoRaSim.
  - Contiene funzione:

```python
def aloha_der(n_nodes, t, rate=1e-6):
    return math.exp(-2 * n_nodes * rate * t)
```

  - Conferma la formula ALOHA da usare per stimare il delivery/success rate.

- `docs/LoRasim_empty.ipynb`
  - Template vuoto/parziale del notebook LoRaSim.
  - Contiene setup e funzioni base.

### Esempi Node-RED

- `docs/node-red_examples.zip`
  - Archivio con flow Node-RED di esempio.

- `docs/node-red_examples_unzipped/`
  - Archivio estratto.
  - File presenti:
    - `random-number.txt`
    - `node-red-dashboard-thingspeak.txt`
    - `node-red-exec-thingspeak.txt`
    - `node-red-alert_template.txt`
    - `node-red-alert_solution`
    - `node-red-shell_template.txt`
    - `node-red-shell_solution.txt`

Contenuti utili dagli esempi:

- `random-number.txt`
  - Esempio `inject -> function -> http request` per inviare dati random a ThingSpeak.

- `node-red-dashboard-thingspeak.txt`
  - Esempio con `delay`, `http request`, `ui_gauge`, `ui_chart`.
  - Utile per capire come costruire i chart richiesti.

- `node-red-exec-thingspeak.txt`
  - Esempio di rate limiter con `delay` e invio ThingSpeak.
  - Nota importante: nella challenge il rate limiter per i messaggi richiesti va configurato in queue, non drop.

- `node-red-alert_template.txt`
  - Esempio di `http request` seguito da nodo `json` e `function`.

### Render PDF

- `docs/pdf_render_check/`
  - Cartella generata per verificare visivamente alcune pagine chiave del PDF.
  - Contiene render PNG di pagine importanti:
    - `page-01.png`
    - `page-04.png`
    - `page-05.png`
    - `page-07.png`
    - `page-09.png`
    - `page-10.png`
    - `page-11.png`
    - `page-12.png`
    - `page-16.png`
    - `page-17.png`
    - `page-20.png`

## Setup ambiente

### Mosquitto

Mosquitto e' il broker MQTT locale.
Per questa challenge deve ascoltare su porta `1884`.

Avvio:

```powershell
mosquitto -p 1884 -v
```

Nel log devono comparire righe simili:

```text
Opening ipv4 listen socket on port 1884.
Opening ipv6 listen socket on port 1884.
mosquitto version ... running
```

Test subscriber:

```powershell
mosquitto_sub -h localhost -p 1884 -t challenge3/id_generator -v
```

Test publisher:

```powershell
mosquitto_pub -h localhost -p 1884 -t challenge3/id_generator -m "{`"id`":7123,`"timestamp`":1710930219}"
```

Se il subscriber riceve il JSON, il broker e' pronto.

Nota: `localhost:1884` non va aperto nel browser. Quella porta parla MQTT, non HTTP.

### Node-RED

Avvio:

```powershell
node-red
```

Aprire nel browser:

```text
http://localhost:1880
```

Per i chart installare la dashboard:

```text
Menu -> Manage palette -> Install -> node-red-dashboard
```

### Script di avvio automatico

E' disponibile uno script Python per avviare Mosquitto e Node-RED insieme:

```powershell
conda run -n iot-challenge python scripts\start_challenge_env.py
```

Lo script:

- avvia Mosquitto su `localhost:1884`;
- avvia Node-RED su `localhost:1880`;
- scrive i log in `logs/`;
- si ferma con `Ctrl+C`, chiudendo i processi avviati dallo script.

Se Node-RED deve usare esplicitamente il flow del repository:

```powershell
conda run -n iot-challenge python scripts\start_challenge_env.py --flow code\flows.json
```

Se Mosquitto o Node-RED sono gia' aperti, lo script rileva la porta occupata e non avvia un duplicato.

### Segreti locali

Non committare la Write API Key di ThingSpeak dentro `code/flows.json`.
Il flow legge la chiave da variabile d'ambiente:

```text
THINGSPEAK_WRITE_API_KEY
```

Per configurarla localmente, copia `.env.example` in `.env` e inserisci la tua key:

```powershell
Copy-Item .env.example .env
notepad .env
```

Il file `.env` e' gia' ignorato da Git tramite `.gitignore`.
Lo script `scripts/start_challenge_env.py` carica `.env` e passa la variabile a Node-RED.

## Part 1 - Flow Node-RED richiesto

### Ramo 1: generatore ID

Creare un flow che ogni secondo pubblichi un messaggio MQTT sul broker locale.

Broker:

```text
localhost
port 1884
```

Topic:

```text
challenge3/id_generator
```

Payload:

```json
{"id": 7123, "timestamp": 1710930219}
```

Regole:

- `id` casuale tra `0` e `30000`.
- `timestamp` in UNIX timestamp.
- Frequenza: 1 messaggio ogni 1 secondo.
- Ogni messaggio inviato va scritto anche in `id_log.csv`.

Formato `id_log.csv`:

```csv
No.,ID,TIMESTAMP
```

Esempio:

```csv
1,7123,152952003
```

### Ramo 2: subscription e selezione CSV

Sottoscriversi al topic:

```text
challenge3/id_generator
```

Per ogni messaggio ricevuto:

1. Estrarre `id`.
2. Calcolare:

```text
N = id % 5218
```

3. Cercare in `challenge3.csv` la riga con:

```text
Packet Number = N
```

4. Processare massimo 200 ID ricevuti.

Chiarimento dalla presentazione:

- Il limite di 200 vale sugli ID ricevuti dalla subscription.
- I messaggi ignorati contano comunque.
- Le righe/costi/chart generati possono essere piu' di 200, perche' sono conseguenze del processing.

### Caso ZBEE_ZCL

Se `Command String` contiene un layer `ZBEE_ZCL`, pubblicare un messaggio MQTT.

Topic corretto, chiarito nel thread:

```text
ZigBee/<Device Name ZigBee Source>
```

Esempio:

```text
ZigBee/Coordinator
```

Il `msg.topic` deve coincidere con `msg.payload.topic`.

Payload richiesto:

```json
{
  "timestamp": "CURRENT_TIMESTAMP",
  "id": "SUB_ID",
  "wpan.src": "SRC_ADDR",
  "wpan.dst": "DST_ADDR",
  "zbee.src": "ZB_SRC_ADDR",
  "zbee.dst": "ZB_DST_ADDR",
  "topic": "ZigBee/ZB_SRC_DEV_NAME",
  "payload": "CMD_STR"
}
```

Origine dei campi:

- `CURRENT_TIMESTAMP`: UNIX timestamp al momento della publish.
- `SUB_ID`: ID ricevuto dalla subscription.
- `SRC_ADDR`: colonna `Source Address`.
- `DST_ADDR`: colonna `Destination Address`.
- `ZB_SRC_ADDR`: colonna `Source Address ZigBee`.
- `ZB_DST_ADDR`: colonna `Destination Address ZigBee`.
- `ZB_SRC_DEV_NAME`: colonna `Device Name ZigBee Source`.
- `CMD_STR`: colonna `Command String`.

Rate limit:

```text
10 messaggi al minuto
```

Chiarimento dal thread:

- Il nodo rate limiter va configurato con queue.
- Non deve droppare messaggi.
- In questo modo i messaggi vengono ritardati ma non persi.

### Parsing attributi e `filtered_elems.csv`

Dopo la publish ZBEE_ZCL, se `Command String` contiene almeno uno tra:

- `Active Power`
- `RMS Current`
- `RMS Voltage`

allora salvare gli elementi completi in `filtered_elems.csv`.

Formato:

```csv
No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value
```

Esempio:

```csv
1,152952012,99,Active Power,Success,16-Bit Signed Integer,0
2,152952012,99,RMS Current,Success,16-Bit Unsigned Integer,0
3,152952012,99,RMS Voltage,Success,16-Bit Unsigned Integer,223
```

Regola chiave:

- Gli elementi vanno associati per posizione.
- `Attribute[i]` corrisponde a `Status[i]`, `Data Type[i]` e al valore in posizione `i`.

Chiarimento dal thread:

- Considerare solo attributi per cui sono presenti tutti i campi corrispondenti:
  - status
  - data type
  - valore
- Se un pacchetto contiene gli attributi ma non contiene status/data type/valori, escluderlo da `filtered_elems.csv`.
- Non scrivere celle vuote.

Chart richiesti:

- Chart RMS Current.
- Chart RMS Voltage.

### Caso Link Status e `outgoing_cost.csv`

Se la riga ha:

```text
Packet Type = Link Status (0x08)
```

allora leggere i link in `Command String` e salvare gli outgoing cost.

Per ogni link:

- `Source`: `Source Address ZigBee` della riga CSV.
- `Destination`: `Links[i].Address`.
- `Cost`: `Links[i].Outgoing Cost`.

Se arriva un Link Status successivo dalla stessa source, aggiornare il costo per ogni destination.

Formato `outgoing_cost.csv`:

```csv
No.,Source,Destination,Cost
```

Esempio:

```csv
1,0x0000,0x0112,7
```

Chiarimento dal thread:

- `outgoing_cost.csv` deve preservare l'ordine in cui i Link Status vengono ricevuti/processati.
- Non deve essere ordinato per source/destination.
- L'ordinamento va fatto solo dopo, per inviare a ThingSpeak.

### ThingSpeak

Dopo la produzione/aggiornamento di `outgoing_cost.csv`:

1. Trovare la source piu' piccola interpretando gli indirizzi come numeri esadecimali.
2. Per quella source, ordinare le destination in ordine esadecimale crescente.
3. Inviare il relativo cost a ThingSpeak in `field1`.

Endpoint HTTP:

```text
https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE
```

Rate limit:

```text
1 messaggio ogni 20 secondi
```

Chiarimenti:

- Il canale ThingSpeak deve essere pubblico.
- Il link/channel ID va inserito nel report e nel form.
- Se ThingSpeak ha problemi temporanei di login, riprovare: il thread indica che puo' essere un problema del servizio.

### Casi da ignorare

Ignorare i pacchetti che:

- non contengono `ZBEE_ZCL`;
- non sono `Link Status (0x08)`.

Anche questi pacchetti contano nel limite dei 200 ID.

## Part 2 - Exercise LoRaWAN

Scenario:

- Carrier frequency: 868 MHz.
- Bandwidth: 125 kHz.
- Gateway: 1.
- Sensor nodes: 40.
- Payload size: 20 bytes.
- Processo di trasmissione: Poisson.
- Intensita' per nodo:

```text
lambda = 2 packets/minute = 1/30 packets/second
```

### EQ1

Determinare il piu' grande spreading factor che garantisce packet success rate almeno 75%.

Modello da usare:

```text
success rate = exp(-2 * N * lambda * airtime)
```

Con:

```text
N = 40
lambda = 1/30 packets/s
target = 0.75
```

Soglia airtime:

```text
exp(-2 * 40 * (1/30) * airtime) >= 0.75
```

Quindi:

```text
airtime <= -ln(0.75) / (2 * 40 * (1/30))
airtime <= circa 0.108 secondi
```

Usando il TTN airtime calculator per payload 20 byte, BW 125 kHz, il risultato atteso e' il piu' grande SF con airtime sotto circa 108 ms.
In pratica il candidato probabile e' `SF8`; `SF9` e superiori hanno airtime troppo alto.

### EQ2

Domanda:

La packet success rate misurata e' molto piu' bassa del previsto e non uniforme tra nodi: alcuni nodi vanno bene, altri molto male.

Opzioni:

1. Decrease the number of nodes.
2. Move the nodes closer to the gateway.
3. Increase the spreading factor.

Risposta consigliata:

```text
2. Move the nodes closer to the gateway.
```

Motivazione:

- Il problema non e' uniforme tra tutti i nodi.
- Questo suggerisce un problema di copertura/link budget per alcuni nodi.
- Aumentare SF puo' migliorare il range, ma aumenta anche l'airtime e quindi le collisioni.
- Ridurre il numero di nodi riduce la congestione, ma non risolve direttamente la non uniformita' legata alla posizione.

## Thread WeBeep - Chiarimenti del professore/assistenti

### Ordine di `outgoing_cost.csv`

Domanda:

- Se alla fine si salva `outgoing_cost.csv` ordinato per source/destination, e poi si riordina ancora per ThingSpeak, va bene?

Risposta:

- No.
- `outgoing_cost.csv` deve preservare l'ordine in cui i Link Status sono ricevuti/processati.
- Solo dopo aver salvato il CSV si puo' riordinare per inviare a ThingSpeak.

Implicazione:

- Il CSV consegnato non va ordinato.
- L'ordinamento esadecimale serve solo per il ramo ThingSpeak.

### Topic MQTT per publish ZBEE_ZCL

Domanda:

- Il topic deve essere `csv["Device Name ZigBee Source"]` oppure `ZigBee/${csv["Device Name ZigBee Source"]}`?

Risposta:

```text
ZigBee/${csv["Device Name ZigBee Source"]}
```

Implicazione:

- `msg.topic` deve essere ad esempio `ZigBee/Coordinator`, non solo `Coordinator`.
- Il campo `topic` dentro il payload deve essere uguale.

### Pacchetti con attributi ma campi incompleti

Domanda:

- Alcuni pacchetti `Read Attributes (0x00)` contengono gli attributi richiesti ma non hanno status, data type o valori. Vanno considerati con celle vuote?

Risposta:

- Considerare solo pacchetti/attributi per cui sono presenti tutti i campi corrispondenti.
- Se mancano status, data type o valore, escludere quell'attributo dal processing.
- Non considerarlo in `filtered_elems.csv`.

Implicazione:

- `filtered_elems.csv` deve contenere solo righe complete.

### Rate limiter e salvataggio `filtered_elems.csv`

Domanda:

- La creazione di `filtered_elems.csv` e' affetta dal rate limiter?

Risposta:

- Impostare il rate limiter in queue, cosi' i messaggi non vengono persi.
- Il rate limiter puo' influenzare il momento in cui i messaggi vengono salvati, ma alla fine tutti i messaggi validi devono essere salvati.

Implicazione:

- Non usare `drop` sul delay/rate limiter.

### Problemi ThingSpeak

Domanda:

- ThingSpeak dava errore di login tramite MathWorks.

Risposta:

- Probabile problema temporaneo del servizio.
- In seguito risultava funzionante.

Implicazione:

- Se ThingSpeak non risponde, riprovare.
- Per la consegna resta richiesto canale pubblico e link nel report/form.

## Deliverable

### Part 1

Consegnare:

- `Challenge.pdf`
  - Nomi e person code.
  - Screenshot del flow Node-RED.
  - Spiegazione dei nodi.
  - Screenshot dei chart Node-RED.
  - Link/channel ID ThingSpeak pubblico.

- `nodered.txt`
  - Export JSON del flow Node-RED.

- `id_log.csv`
  - Header:

```csv
No.,ID,TIMESTAMP
```

- `filtered_elems.csv`
  - Header:

```csv
No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value
```

- `outgoing_cost.csv`
  - Header:

```csv
No.,Source,Destination,Cost
```

- ThingSpeak channel ID/link.

### Part 2

Consegnare:

- `Exercise.pdf`
  - Nomi e person code.
  - Risposte a EQ1 ed EQ2.

### ZIP finale

Per team da due persone:

```text
<leader_personcode>_<other_personcode>.zip
```

Regole:

- Solo il team leader deve caricare su WeBeep.
- Non caricare duplicati.
- Max 2 persone.
- Compilare il form.
- Errori di nome file, form mancante o estensioni sbagliate causano penalita'.
