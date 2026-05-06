# AGENTS.md

Linee guida per agenti che lavorano su questo repository della Challenge 3 IoT.

## Stile di lavoro

- Rispondi in italiano, in modo breve e operativo.
- Non riscrivere la traccia completa della challenge: cita solo i vincoli rilevanti al task corrente.
- Prima di modificare file, controlla il contesto locale: `README.md`, `TODO.md`, `code/flows.json`, `scripts/`.
- Mantieni le modifiche piccole e mirate. Non fare refactor non richiesti.
- Non cancellare o rigenerare CSV/output esistenti senza un motivo esplicito.
- Non committare segreti. La key ThingSpeak deve restare fuori da `code/flows.json` e stare in `.env` come `THINGSPEAK_WRITE_API_KEY`.

## File principali

- `README.md`: fonte principale dei requisiti gia' interpretati.
- `TODO.md`: stato operativo e punti ancora da verificare.
- `docs/Challenge3.pdf`: traccia ufficiale, da consultare solo se README/TODO non bastano.
- `docs/challenge3.csv`: dataset di input, 5218 righe con `Packet Number` da 0 a 5217.
- `code/flows.json`: export Node-RED del flow.
- `scripts/start_challenge_env.py`: avvia Mosquitto su `localhost:1884` e Node-RED su `localhost:1880`.
- `scripts/plot_challenge_outputs.py`: genera grafici da CSV in `report_assets/`.

## Comandi utili

```powershell
conda run -n iot-challenge python scripts\start_challenge_env.py
conda run -n iot-challenge python scripts\start_challenge_env.py --flow code\flows.json
conda run -n iot-challenge python scripts\plot_challenge_outputs.py
mosquitto -p 1884 -v
node-red
```

## Regole Part 1 da non rompere

- MQTT broker: `localhost`, porta `1884`.
- Generatore ID: pubblica ogni secondo su `challenge3/id_generator`.
- Payload ID: JSON con `id` casuale `0..30000` e `timestamp` UNIX.
- Ogni ID generato va scritto in `id_log.csv` con header `No.,ID,TIMESTAMP`.
- Subscription: per ogni ID ricevuto calcola `N = id % 5218` e processa la riga con `Packet Number = N`.
- Il limite di 200 vale sugli ID ricevuti dalla subscription; anche i pacchetti ignorati contano.
- Ignora pacchetti che non contengono `ZBEE_ZCL` e non sono `Link Status (0x08)`.

### ZBEE_ZCL

- Topic MQTT corretto: `ZigBee/<Device Name ZigBee Source>`.
- `msg.topic` deve coincidere con `msg.payload.topic`.
- Rate limit: 10 messaggi/minuto, con queue attiva. Non droppare messaggi.
- Payload richiesto:

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

### `filtered_elems.csv`

- Header esatto: `No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value`.
- Salvare solo attributi tra `Active Power`, `RMS Current`, `RMS Voltage`.
- Associare i campi per posizione: `Attribute[i]`, `Status[i]`, `Data Type[i]`, `Data Value[i]`.
- Inserire solo righe complete. Se mancano status, data type o valore, escludere l'attributo.
- Non scrivere celle vuote.
- Chart richiesti: RMS Current e RMS Voltage.

### `outgoing_cost.csv`

- Header esatto: `No.,Source,Destination,Cost`.
- Si aggiorna dai pacchetti con `Packet Type = Link Status (0x08)`.
- `Source` = `Source Address ZigBee` della riga.
- `Destination` = address del link.
- `Cost` = outgoing cost del link.
- Se arriva un nuovo Link Status dalla stessa source, aggiorna i costi per destination.
- Il CSV deve preservare l'ordine di ricezione/processing. Non ordinarlo per source/destination.
- L'ordinamento esadecimale serve solo dopo, per ThingSpeak.

### ThingSpeak

- Dopo aggiornamento di `outgoing_cost.csv`, scegli la source piu' piccola come numero esadecimale.
- Per quella source, ordina le destination in esadecimale crescente.
- Invia il cost in `field1`.
- Endpoint: `https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE`.
- Rate limit: 1 messaggio ogni 20 secondi, con queue.
- Il canale deve essere pubblico e il link/channel ID va nel report/form.

## Regole Part 2 LoRaWAN

- Usa modello ALOHA:

```text
success rate = exp(-2 * N * lambda * airtime)
```

- Parametri: `N = 40`, `lambda = 2 packets/minute = 1/30 packets/s`, target `75%`.
- Soglia airtime: circa `0.108 s`.
- EQ1: scegliere il piu' grande spreading factor con airtime sotto circa 108 ms; candidato atteso `SF8`.
- EQ2: risposta consigliata `Move the nodes closer to the gateway`, perche' il problema e' non uniforme tra nodi.

## Deliverable

- Part 1: `Challenge.pdf`, `nodered.txt`, `id_log.csv`, `filtered_elems.csv`, `outgoing_cost.csv`, ThingSpeak channel/link.
- Part 2: `Exercise.pdf`.
- ZIP finale per team da due: `<leader_personcode>_<other_personcode>.zip`.
- Solo il team leader carica su WeBeep.
- Evita duplicati, nomi file errati, form mancante o estensioni sbagliate.
