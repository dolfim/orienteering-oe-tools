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
GO2OLID_FIELD = "ID"
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD, GO2OLID_FIELD)


def main(
    missing_iof_input_filename: Path=typer.Option(..., "--missing-iof", help="File Excel with manual matches for IOF ID"),
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

    typer.echo(f"Reading IOF mapping from file {missing_iof_input_filename}")
    late_data = pd.read_excel(missing_iof_input_filename, skiprows=2)
    for _, entry in late_data.iterrows():
        if not pd.isna(entry["IOF ID"]) and not entry["IOF ID"] == "NA":
            typer.secho(f"Matching IOF ID {entry['IOF ID']} for {entry['Nachname']} {entry['Vorname']}", fg=typer.colors.GREEN)
            exportId = str(entry["Export-ID"])
            # print("Export-ID",exportId)
            if not exportId in data_by_index[GO2OLID_FIELD]:
                typer.secho(f"Athlete {entry['Nachname']} {entry['Vorname']} NOT FOUND", fg=typer.colors.RED)
                continue
            # print("ix", data_by_index[GO2OLID_FIELD][exportId])
            # print(data[data_by_index[GO2OLID_FIELD][exportId]])
            data[data_by_index[GO2OLID_FIELD][exportId]][IOFID_FIELD] = "{0:d}".format(int(entry["IOF ID"]))
        else:
            typer.secho(f"Athlete {entry['Nachname']} {entry['Vorname']} NOT FOUND", fg=typer.colors.RED)

        
    typer.echo(f"Writing output to {output_filename}")
    with open(output_filename, 'w', encoding=CSV_OUTPUT_ENCODING) as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', delimiter=';', fieldnames=header_keys)

        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

