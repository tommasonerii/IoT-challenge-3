# IoT Challenge 3

Node-RED, MQTT, ZigBee CSV processing, ThingSpeak updates, and LoRaWAN ALOHA analysis for the IoT Challenge 3 assignment.

## Project Status

| Area | Status | Notes |
| --- | --- | --- |
| Node-RED flow | Done | Exported in `code/flows.json` and `delivery/nodered.txt`. |
| Part 1 CSV outputs | Done | `id_log.csv`, `filtered_elems.csv`, and `outgoing_cost.csv` are present in root and `delivery/`. |
| Part 1 report | Done | `delivery/Challenge.pdf` is present. |
| Part 2 report | Done, review pending | `delivery/Exercise.pdf` is present. EQ1 should be rechecked: the report concludes `SF7`, while local notes previously expected `SF8`. |
| Final ZIP / upload | Pending | See `TODO.md`. |

Deadline from the challenge material:

```text
12 maggio 2026, 23:59
```

## Quick Start

Use the `iot-challenge` conda environment for Python scripts.

```powershell
conda run -n iot-challenge python scripts\start_challenge_env.py --flow code\flows.json
```

This starts:

- Mosquitto on `localhost:1884`;
- Node-RED on `http://localhost:1880`;
- logs under `logs/`;
- the repository flow when `--flow code\flows.json` is provided.

Generate report plots from the final CSV files:

```powershell
conda run -n iot-challenge python scripts\plot_challenge_outputs.py
```

## Repository Layout

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Working rules for agents operating on this repository. |
| `README.md` | Primary interpreted project context and operating guide. |
| `TODO.md` | Operational checklist and remaining risks. |
| `code/flows.json` | Node-RED flow export. |
| `docs/Challenge3.pdf` | Official challenge statement. Consult only when README/TODO are not enough. |
| `docs/challenge3.csv` | Input dataset, 5218 rows, `Packet Number` from `0` to `5217`. |
| `scripts/start_challenge_env.py` | Starts Mosquitto and Node-RED. |
| `scripts/plot_challenge_outputs.py` | Builds plots from generated CSV outputs. |
| `part1/report/Challenge.tex` | LaTeX source for Part 1 report. |
| `part2/report/Exercise.tex` | LaTeX source for Part 2 report. |
| `delivery/` | Files prepared for final submission. |

## Local Context Policy

`README.md` and `TODO.md` are the local context files that must stay aligned after each response that modifies or verifies the work:

- update `README.md` when requirements, architecture, commands, outputs, or known risks change;
- update `TODO.md` when the operational state changes.

## Prerequisites

- Mosquitto available on the command line.
- Node-RED available on the command line.
- Node-RED dashboard nodes installed when chart screenshots are needed.
- Conda environment named `iot-challenge` for repository scripts.
- ThingSpeak public channel and Write API Key.

Useful manual commands:

```powershell
mosquitto -p 1884 -v
node-red
mosquitto_sub -h localhost -p 1884 -t challenge3/id_generator -v
mosquitto_pub -h localhost -p 1884 -t challenge3/id_generator -m "{`"id`":7123,`"timestamp`":1710930219}"
```

Do not open `localhost:1884` in the browser: that port speaks MQTT, not HTTP.

## Configuration

ThingSpeak credentials must stay out of `code/flows.json`.

The flow reads the Write API Key from:

```text
THINGSPEAK_WRITE_API_KEY
```

Store it locally in `.env`:

```text
THINGSPEAK_WRITE_API_KEY=...
```

`.env` is local-only and must not be committed.

## Part 1 Architecture

The Node-RED flow implements six blocks:

1. Initialization and CSV header reset.
2. ID generation and MQTT publish.
3. MQTT subscription, 200-ID limit, and CSV row selection.
4. ZBEE_ZCL publish, filtered attributes, and dashboard charts.
5. Link Status processing and `outgoing_cost.csv` update.
6. ThingSpeak update after the 200 received IDs are processed.

### ID Generation

- MQTT broker: `localhost:1884`.
- Publish topic: `challenge3/id_generator`.
- Publish interval: 1 second.
- Payload:

```json
{"id": 7123, "timestamp": 1710930219}
```

- `id`: random integer from `0` to `30000`.
- `timestamp`: UNIX timestamp.
- Every generated ID is appended to `id_log.csv`.
- Header:

```csv
No.,ID,TIMESTAMP
```

The generator also stops after the subscriber completes 200 received IDs, to avoid an oversized `id_log.csv`. The mandatory limit is still enforced on the subscriber side.

### Subscription and Packet Selection

The subscriber listens on:

```text
challenge3/id_generator
```

For each received ID:

1. parse the JSON payload;
2. compute `N = id % 5218`;
3. select the row in `docs/challenge3.csv` whose `Packet Number = N`;
4. count the ID even if the selected packet is ignored;
5. process no more than 200 received IDs.

Packets are ignored unless they either:

- contain `ZBEE_ZCL` in `Command String`; or
- have `Packet Type = Link Status (0x08)`.

### ZBEE_ZCL Publish

For ZBEE_ZCL packets, the MQTT publish topic is:

```text
ZigBee/<Device Name ZigBee Source>
```

`msg.topic` must match the `topic` field inside the payload.

Payload shape:

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

Rate limit:

- 10 messages per minute;
- queue enabled;
- no message dropping.

### Filtered Attributes

The flow writes `filtered_elems.csv` after the ZBEE_ZCL rate limiter.

Header:

```csv
No.,Timestamp,Sequence Number, Attribute,Status,Data Type,Data Value
```

Only these attributes are saved:

- `Active Power`;
- `RMS Current`;
- `RMS Voltage`.

Rules:

- preserve positional matching: `Attribute[i]`, `Status[i]`, `Data Type[i]`, `Data Value[i]`;
- save only complete attributes;
- skip attributes with missing status, data type, or value;
- never write empty CSV cells.

Dashboard charts:

- RMS Current;
- RMS Voltage.

The chart x-axis can use the dashboard arrival time; no custom timestamp is required.

### Link Status and Outgoing Cost

Link Status packets are identified by:

```text
Packet Type = Link Status (0x08)
```

`outgoing_cost.csv` header:

```csv
No.,Source,Destination,Cost
```

Mapping:

- `Source`: row value of `Source Address ZigBee`;
- `Destination`: `Links[i].Address`;
- `Cost`: `Links[i].Outgoing Cost`.

If a later Link Status packet updates an existing source/destination pair, the final cost is updated. The CSV preserves the first processing order of source/destination pairs and is not sorted by source or destination.

### ThingSpeak

After the 200 received IDs are processed:

1. read the final Link Status state;
2. select the smallest source address by hexadecimal numeric value;
3. sort that source's destinations by hexadecimal numeric value;
4. send each cost to ThingSpeak in `field1`.

Endpoint:

```text
https://api.thingspeak.com/update?api_key=WRITE_API_KEY&field1=VALUE
```

Rate limit:

- 1 update every 20 seconds;
- queue enabled;
- no message dropping.

The ThingSpeak channel must be public, and the channel link/ID must appear in the report and submission form.

## Part 2 LoRaWAN

Use the simplified ALOHA model:

```text
success rate = exp(-2 * N * lambda * airtime)
```

Parameters:

```text
N = 40
lambda = 2 packets/minute = 1/30 packets/second
target = 75%
```

The airtime threshold is:

```text
airtime <= -ln(0.75) / (2 * 40 * (1/30))
airtime <= approximately 0.108 s
```

Current report state:

- `part2/report/Exercise.tex` uses the TTN LoRaWAN airtime calculator with 20 input bytes and LoRaWAN overhead included.
- Under that interpretation, `SF7` is the largest SF satisfying the 75% target.
- `TODO.md` keeps an open check because earlier local notes expected `SF8`.

Recommended EQ2 answer:

```text
Move the nodes closer to the gateway
```

Reason: non-uniform node performance points to coverage or link-budget issues, not only global congestion.

## Deliverables

Part 1:

- `Challenge.pdf`;
- `nodered.txt`;
- `id_log.csv`;
- `filtered_elems.csv`;
- `outgoing_cost.csv`;
- public ThingSpeak channel link/ID.

Part 2:

- `Exercise.pdf`.

Current delivery folder:

```text
delivery/
  Challenge.pdf
  Exercise.pdf
  filtered_elems.csv
  id_log.csv
  nodered.txt
  outgoing_cost.csv
```

Final ZIP naming for a two-person team:

```text
<leader_personcode>_<other_personcode>.zip
```

Only the team leader uploads the ZIP to WeBeep. The form must also be completed.

## Validation Checklist

Before submission, verify:

- `delivery/` contains all required files;
- `nodered.txt` matches `code/flows.json`;
- `id_log.csv` has exactly 200 generated IDs for the final run;
- `filtered_elems.csv` contains no empty cells;
- `outgoing_cost.csv` preserves processing order and is not sorted;
- ThingSpeak updates are visible on the public channel;
- queued Node-RED delay nodes have drained before collecting final CSV outputs;
- EQ1 interpretation in `Exercise.pdf` is the intended one.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `localhost:1884` does not open in the browser | Expected behavior. Use MQTT clients; port 1884 is not HTTP. |
| MQTT messages are not received | Confirm Mosquitto is running on `localhost:1884` and both nodes use the same broker config. |
| Chart nodes are missing | Install `node-red-dashboard` from Node-RED palette manager. |
| ThingSpeak updates fail | Confirm `THINGSPEAK_WRITE_API_KEY` is set in `.env` and the channel accepts public updates. |
| Output CSVs miss delayed messages | Wait for all queued delay nodes to drain before copying final deliverables. |

## Maintainer Notes

- Keep changes small and challenge-focused.
- Do not regenerate or delete existing CSV outputs unless explicitly needed.
- Do not commit secrets.
- Keep `README.md` and `TODO.md` aligned after any verification or file change.
