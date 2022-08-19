#!/usr/bin/env python3

import csv
from pathlib import Path

import pandas as pd
import typer


CSV_INPUT_ENCODING = 'ISO-8859-1'
CSV_OUTPUT_ENCODING = 'ISO-8859-1'

IOFID_FIELD = "Num3"
SOLVNR_FIELD = "Datenbank Id"
SICARD_FIELD = "Chipnr"
START_REGION_FIELD = "Num1"
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD)


ENTRY_DB_FIELDS = (
    "Chipnr",
    "Datenbank Id",
    "Nachname",
    "Vorname",
    "Jg",
    "Geschlecht",
    # "Block": "",
    "Club-Nr.",
    "Abk",
    "Ort",
    "Nat",
    "Sitz",
    "Region",
    # "Katnr",
    # "Kurz",
    # "Lang",
    "Num3",
    "Adr. Nachname",
    "Adr. Vorname",
    "Straße",
    "PLZ",
    "Adr. Ort",
    "EMail",
    # "Gemietet",
    # "Startgeld",
    # "Bezahlt",
)

BLOCK_DEFAULT = 5
BLOCKS_MAPPING = {
    "Sabato": { # From https://o-tools.swiss-orienteering.ch/plan/unique_id/11004
        "101": 7,
        "102": 5,
        "103": 5,
        "104": 3,
        "105": 3,
        "106": 7,
        "107": 3,
    },
    "Domenica": { # From https://o-tools.swiss-orienteering.ch/plan/unique_id/11006
        "101": 5,
        "102": 3,
        "103": 7,
        "104": 5,
        "105": 7,
        "106": 3,
        "107": 7,
    },
}

def main(
    late_input_filename: Path=typer.Option(..., "--late-entries", help="File Excel late entries"),
    sheet_name: str=typer.Option(..., help="Name of the worksheet to use"),
    solv_input_filename: Path=typer.Option(..., "--solv-db", help="File CSV con DB SOLV"),
    oe_input_filename: Path=typer.Option(..., "--oe-entries", help="File CSV con iscrizioni OE"),
    output_filename: Path=typer.Option(..., "--output", help="File CSV di output")
    ):
    
    typer.echo(f"Reading entries from CSV file {oe_input_filename}")
    with open(oe_input_filename, encoding=CSV_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        data = []
        header_keys = None
        data_by_index = {ix: {} for ix in INDEX_COLS}
        for i, row in enumerate(reader):
            if not header_keys: header_keys = list(row.keys())
            data.append(row)
            
            for ix in INDEX_COLS:
                if row[ix] != "0" and row[ix] != "":
                    data_by_index[ix][row[ix]] = i

    typer.echo(f"Reading SOLV DB from CSV file {solv_input_filename}")
    with open(solv_input_filename, encoding=CSV_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        solv_db = {}
        for i, row in enumerate(reader):
            row["Chipnr"] = row["Chipnr SI"]
            row["Geschlecht"] = row["G"]
            solv_db[row[SOLVNR_FIELD]] = row

    typer.echo(f"Reading Late entries from file {late_input_filename}")
    late_data = pd.read_excel(late_input_filename, sheet_name=sheet_name, skiprows=1)
    for _, entry in late_data.iterrows():
        if not pd.isna(entry["Eseguito"]):
            typer.secho(f"Athlete {entry['Cognome']} {entry['Nome']} already done", fg=typer.colors.YELLOW)
            continue

        if entry["SOLV-nr"] and entry["SOLV-nr"] in solv_db:
            typer.secho(f"Athlete {entry['SOLV-nr']} {entry['Cognome']} {entry['Nome']} found in SOLV DB", fg=typer.colors.GREEN)
            db_entry = solv_db[entry["SOLV-nr"]]
            startRegion = db_entry["Num1"]
            startBlock = BLOCKS_MAPPING[sheet_name].get(startRegion, BLOCK_DEFAULT)
            row = {
                k: db_entry[k]
                for k in ENTRY_DB_FIELDS
            }
            late_entry = {
                "Startgeld": entry["Importo"],
                "Kurz": entry["Cat"],
                "Startgeld": entry["Importo"],
                "Block": str(startBlock),
            }
            if not pd.isna(entry["SI-Card"]):
                late_entry[SICARD_FIELD] = entry["SI-Card"]
            row = {
                **row,
                **late_entry
            }
            data.append(row)
        else:
            typer.secho(f"Athlete {entry['Cognome']} {entry['Nome']} NOT FOUND", fg=typer.colors.RED)



        
    typer.echo(f"Writing output to {output_filename}")
    with open(output_filename, 'w', encoding=CSV_OUTPUT_ENCODING) as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', delimiter=';', fieldnames=header_keys)

        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

