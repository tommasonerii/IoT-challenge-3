# TODO - IoT Challenge 3

Checklist operativa per completare la challenge.

## 1. Ambiente

- [ ] Verificare che Mosquitto sia installato.
- [ ] Avviare Mosquitto su porta `1884`.

```powershell
mosquitto -p 1884 -v
```

- [ ] Testare subscriber MQTT.

```powershell
mosquitto_sub -h localhost -p 1884 -t challenge3/id_generator -v
```

- [ ] Testare publisher MQTT.

```powershell
mosquitto_pub -h localhost -p 1884 -t challenge3/id_generator -m "{`"id`":7123,`"timestamp`":1710930219}"
```

- [ ] Avviare Node-RED.

```powershell
node-red
```

- [ ] Aprire Node-RED.

```text
http://localhost:1880
```

- [ ] Installare `node-red-dashboard` se mancano i nodi chart.
- [ ] Creare canale ThingSpeak pubblico.
- [ ] Recuperare `WRITE_API_KEY` e channel link/ID.

## 2. Preparazione file

- [ ] Decidere dove Node-RED leggera' `challenge3.csv`.
- [ ] Verificare che `challenge3.csv` abbia 5218 righe con `Packet Number` 0..5217.
- [ ] Preparare header `id_log.csv`.

```csv
No.,ID,TIMESTAMP
```

- [ ] Preparare header `filtered_elems.csv`.

```csv
No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value
```

- [ ] Preparare header `outgoing_cost.csv`.

```csv
No.,Source,Destination,Cost
```

## 3. Flow Node-RED - Generatore ID

- [x] Creare ramo `inject -> function -> mqtt out`.
- [x] Configurare tick ogni 1 secondo, controllato da `Start generator` / `Stop generator`.
- [x] In `function`, generare `id` random tra 0 e 30000.
- [x] In `function`, generare UNIX timestamp.
- [x] Pubblicare su topic:

```text
challenge3/id_generator
```

- [x] Configurare broker MQTT:

```text
localhost:1884
```

- [x] Salvare ogni ID generato in `id_log.csv`.
- [x] Controllare che il CSV abbia `No.` incrementale.

## 4. Flow Node-RED - Subscription ID

- [x] Creare ramo `mqtt in` sul topic:

```text
challenge3/id_generator
```

- [x] Parsare il payload JSON ricevuto.
- [x] Contare gli ID ricevuti.
- [x] Fermare il processing dopo esattamente 200 ID.
- [x] Calcolare:

```text
N = id % 5218
```

- [x] Leggere/cercare nel CSV la riga con `Packet Number = N`.
- [x] Ignorare righe non `ZBEE_ZCL` e non `Link Status`, contando comunque l'ID.

## 5. Caso ZBEE_ZCL

- [x] Rilevare se `Command String` contiene `ZBEE_ZCL`.
- [x] Creare topic MQTT:

```text
ZigBee/<Device Name ZigBee Source>
```

- [x] Creare payload con:
  - [x] `timestamp`
  - [x] `id`
  - [x] `wpan.src`
  - [x] `wpan.dst`
  - [x] `zbee.src`
  - [x] `zbee.dst`
  - [x] `topic`
  - [x] `payload`

- [x] Verificare che `msg.topic` sia uguale a `msg.payload.topic`.
- [x] Configurare `mqtt out`.
- [x] Aggiungere rate limiter a 10 messaggi/minuto.
- [x] Configurare il rate limiter in queue, non drop.

## 6. Parsing attributi filtrati

- [x] Dopo la publish ZBEE_ZCL, controllare attributi:
  - [x] `Active Power`
  - [x] `RMS Current`
  - [x] `RMS Voltage`

- [x] Considerare solo attributi con campi completi:
  - [x] `Status`
  - [x] `Data Type`
  - [x] valore numerico

- [x] Escludere attributi incompleti.
- [x] Non scrivere celle vuote.
- [x] Mantenere matching posizionale:

```text
Attribute[i] -> Status[i] -> Data Type[i] -> Value[i]
```

- [x] Scrivere righe complete in `filtered_elems.csv`.
- [x] Inviare valori `RMS Current` a chart dedicato.
- [x] Inviare valori `RMS Voltage` a chart dedicato.
- [ ] Fare screenshot dei chart per `Challenge.pdf`.

## 7. Caso Link Status

- [x] Rilevare:

```text
Packet Type = Link Status (0x08)
```

- [x] Parsare `Command String`.
- [x] Estrarre `Links`.
- [x] Per ogni link, ricavare:
  - [x] source = `Source Address ZigBee`
  - [x] destination = `Links[i].Address`
  - [x] cost = `Links[i].Outgoing Cost`

- [x] Aggiornare il costo se arriva una nuova coppia source/destination.
- [x] Preservare l'ordine di ricezione/processing.
- [x] Scrivere `outgoing_cost.csv` senza ordinare per source/destination.

## 8. ThingSpeak

- [ ] Alla fine dei 200 ID, leggere i dati finali di `outgoing_cost.csv`.
- [ ] Trovare la source minima interpretando gli indirizzi come esadecimali.
- [ ] Per quella source, ordinare le destination in ordine esadecimale crescente.
- [ ] Inviare ogni cost a ThingSpeak in `field1`.
- [ ] Usare endpoint:

```text
https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE
```

- [ ] Applicare rate limit: 1 messaggio ogni 20 secondi.
- [ ] Verificare che il canale sia pubblico.
- [ ] Salvare link/channel ID per report e form.

## 9. Exercise LoRaWAN

- [ ] Calcolare `lambda`:

```text
2 packets/min = 1/30 packets/s
```

- [ ] Usare modello ALOHA:

```text
success rate = exp(-2 * N * lambda * airtime)
```

- [ ] Usare:

```text
N = 40
target = 0.75
```

- [ ] Calcolare soglia airtime:

```text
airtime <= -ln(0.75) / (2 * 40 * (1/30))
```

- [ ] Usare TTN airtime calculator per payload 20 byte, BW 125 kHz.
- [ ] Trovare il piu' grande SF con success rate >= 75%.
- [ ] Motivare EQ1.
- [ ] Rispondere EQ2 scegliendo:

```text
Move the nodes closer to the gateway
```

- [ ] Motivare EQ2 con non uniformita' delle performance e link budget/copertura.

## 10. Report

- [ ] Esportare flow Node-RED come JSON.
- [ ] Salvare export in:

```text
nodered.txt
```

- [ ] Creare `Challenge.pdf` con:
  - [ ] nomi e person code
  - [ ] screenshot flow Node-RED
  - [ ] spiegazione di ogni nodo
  - [ ] screenshot chart RMS Current
  - [ ] screenshot chart RMS Voltage
  - [ ] ThingSpeak channel ID/link

- [ ] Creare `Exercise.pdf` con:
  - [ ] nomi e person code
  - [ ] risposta EQ1
  - [ ] risposta EQ2

## 11. Consegna

- [ ] Verificare presenza file:
  - [ ] `Challenge.pdf`
  - [ ] `Exercise.pdf`
  - [ ] `nodered.txt`
  - [ ] `id_log.csv`
  - [ ] `filtered_elems.csv`
  - [ ] `outgoing_cost.csv`

- [ ] Creare ZIP con nome corretto.

Per team da due:

```text
<leader_personcode>_<other_personcode>.zip
```

- [ ] Caricare ZIP su WeBeep.
- [ ] Compilare form.
- [ ] Verificare che il canale ThingSpeak sia pubblico.
- [ ] Consegnare entro:

```text
12 maggio 2026, 23:59
```
