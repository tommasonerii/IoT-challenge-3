#!/usr/bin/env python3
"""Generate report plots from Challenge 3 output CSV files."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "report_assets"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, skipinitialspace=True)
        return [
            {str(key).strip(): value for key, value in row.items()}
            for row in reader
        ]


def hex_int(value: str) -> int:
    return int(value, 16)


def save_filtered_charts(filtered_rows: list[dict[str, str]]) -> None:
    by_attr: dict[str, list[tuple[int, float]]] = {
        "Active Power": [],
        "RMS Current": [],
        "RMS Voltage": [],
    }

    for row in filtered_rows:
        attr = row["Attribute"]
        if attr not in by_attr:
            continue
        by_attr[attr].append((int(row["No."]), float(row["Data Value"])))

    for attr, values in by_attr.items():
        if not values:
            continue

        xs = [x for x, _ in values]
        ys = [y for _, y in values]

        plt.figure(figsize=(8, 4.5))
        plt.plot(xs, ys, marker="o", linewidth=1.8)
        plt.title(attr)
        plt.xlabel("filtered_elems.csv row No.")
        plt.ylabel("Data Value")
        plt.grid(True, alpha=0.35)
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"{attr.lower().replace(' ', '_')}.png", dpi=180)
        plt.close()

    attrs = [row["Attribute"] for row in filtered_rows]
    counts = Counter(attrs)
    labels = ["Active Power", "RMS Current", "RMS Voltage"]
    values = [counts.get(label, 0) for label in labels]

    plt.figure(figsize=(7, 4.5))
    plt.bar(labels, values)
    plt.title("Filtered Elements Count")
    plt.xlabel("Attribute")
    plt.ylabel("Rows")
    plt.grid(axis="y", alpha=0.35)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "filtered_elements_count.png", dpi=180)
    plt.close()


def save_thingspeak_chart(outgoing_rows: list[dict[str, str]]) -> None:
    if not outgoing_rows:
        return

    min_source = min({row["Source"] for row in outgoing_rows}, key=hex_int)
    selected = [row for row in outgoing_rows if row["Source"] == min_source]
    selected.sort(key=lambda row: hex_int(row["Destination"]))

    destinations = [row["Destination"] for row in selected]
    costs = [float(row["Cost"]) for row in selected]

    plt.figure(figsize=(9, 4.8))
    plt.plot(destinations, costs, marker="o", linewidth=1.8)
    plt.title(f"ThingSpeak field1 update order - source {min_source}")
    plt.xlabel("Destination address")
    plt.ylabel("Outgoing Cost")
    plt.grid(True, alpha=0.35)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "thingspeak_field1_updates.png", dpi=180)
    plt.close()


def save_outgoing_cost_heatmap(outgoing_rows: list[dict[str, str]]) -> None:
    if not outgoing_rows:
        return

    sources = sorted({row["Source"] for row in outgoing_rows}, key=hex_int)
    destinations = sorted({row["Destination"] for row in outgoing_rows}, key=hex_int)
    matrix = [[None for _ in destinations] for _ in sources]
    source_index = {source: idx for idx, source in enumerate(sources)}
    destination_index = {destination: idx for idx, destination in enumerate(destinations)}

    for row in outgoing_rows:
        matrix[source_index[row["Source"]]][destination_index[row["Destination"]]] = float(row["Cost"])

    numeric = [[value if value is not None else float("nan") for value in line] for line in matrix]

    plt.figure(figsize=(9, 5.5))
    image = plt.imshow(numeric, aspect="auto", interpolation="nearest")
    plt.colorbar(image, label="Outgoing Cost")
    plt.title("Outgoing Cost by Source/Destination")
    plt.xlabel("Destination")
    plt.ylabel("Source")
    plt.xticks(range(len(destinations)), destinations, rotation=45, ha="right")
    plt.yticks(range(len(sources)), sources)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "outgoing_cost_heatmap.png", dpi=180)
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    filtered_rows = read_csv(ROOT / "filtered_elems.csv")
    outgoing_rows = read_csv(ROOT / "outgoing_cost.csv")

    save_filtered_charts(filtered_rows)
    save_thingspeak_chart(outgoing_rows)
    save_outgoing_cost_heatmap(outgoing_rows)

    print(f"Generated plots in {OUT_DIR}")
    for path in sorted(OUT_DIR.glob("*.png")):
        print(f"- {path}")


if __name__ == "__main__":
    main()
