# TODO - IoT Challenge 3

Checklist operativa per completare la challenge.

## 1. Ambiente

- [x] Verificare che Mosquitto sia installato.
- [x] Avviare Mosquitto su porta `1884`.

```powershell
mosquitto -p 1884 -v
```

- [x] Testare subscriber MQTT.

```powershell
mosquitto_sub -h localhost -p 1884 -t challenge3/id_generator -v
```

- [x] Testare publisher MQTT.

```powershell
mosquitto_pub -h localhost -p 1884 -t challenge3/id_generator -m "{`"id`":7123,`"timestamp`":1710930219}"
```

- [x] Avviare Node-RED.

```powershell
node-red
```

- [x] Aprire Node-RED.

```text
http://localhost:1880
```

- [x] Installare `node-red-dashboard` se mancano i nodi chart.
- [x] Creare canale ThingSpeak pubblico.
- [x] Recuperare `WRITE_API_KEY` e channel link/ID.

## 2. Preparazione file

- [x] Decidere dove Node-RED leggera' `challenge3.csv`.
- [x] Verificare che `challenge3.csv` abbia 5218 righe con `Packet Number` 0..5217.
- [x] Preparare header `id_log.csv`.

```csv
No.,ID,TIMESTAMP
```

- [x] Preparare header `filtered_elems.csv`.

```csv
No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value
```

- [x] Preparare header `outgoing_cost.csv`.

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
- [x] Fare screenshot dei chart per `Challenge.pdf`.

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

- [x] Alla fine dei 200 ID, leggere i dati finali di `outgoing_cost.csv`.
- [x] Trovare la source minima interpretando gli indirizzi come esadecimali.
- [x] Per quella source, ordinare le destination in ordine esadecimale crescente.
- [x] Inviare ogni cost a ThingSpeak in `field1`.
- [x] Usare endpoint:

```text
https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE
```

- [x] Applicare rate limit: 1 messaggio ogni 20 secondi.
- [x] Verificare che il canale sia pubblico.
- [x] Salvare link/channel ID per report e form.

## 9. Exercise LoRaWAN

- [x] Calcolare `lambda`:

```text
2 packets/min = 1/30 packets/s
```

- [x] Usare modello ALOHA:

```text
success rate = exp(-2 * N * lambda * airtime)
```

- [x] Usare:

```text
N = 40
target = 0.75
```

- [x] Calcolare soglia airtime:

```text
airtime <= -ln(0.75) / (2 * 40 * (1/30))
```

- [x] Usare TTN airtime calculator per payload 20 byte, BW 125 kHz.
- [x] Trovare il piu' grande SF con success rate >= 75%.
- [x] Motivare EQ1.
- [x] Rispondere EQ2 scegliendo:

```text
Move the nodes closer to the gateway
```

- [x] Motivare EQ2 con non uniformita' delle performance e link budget/copertura.

## 10. Report

- [x] Esportare flow Node-RED come JSON.
- [ ] Salvare export in:

```text
nodered.txt
```

- [x] Creare sorgente LaTeX `part1/report/Challenge.tex` con:
  - [x] nomi e person code
  - [x] screenshot flow Node-RED
  - [x] spiegazione di ogni nodo
  - [x] screenshot chart RMS Current
  - [x] screenshot chart RMS Voltage
  - [x] ThingSpeak channel ID/link

- [ ] Compilare `Challenge.pdf`.

- [x] Creare sorgente LaTeX `part2/report/Exercise.tex` con:
  - [x] nomi e person code
  - [x] risposta EQ1
  - [x] risposta EQ2

- [ ] Compilare `Exercise.pdf`.

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
