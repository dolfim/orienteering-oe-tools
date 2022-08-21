#!/usr/bin/env python3

import csv
import math
from pathlib import Path

import typer

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


CSV_INPUT_ENCODING = 'ISO-8859-1'
CSV_OUTPUT_ENCODING = 'ISO-8859-1'

WRE_INPUT_ENCODING = 'UTF8'
WRE_OUTPUT_ENCODING = 'UTF8'

from oe_columns.it import *
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD)

BLOCK_SIZE = 10
MEN_CATEGORIES = ["H20", "HE"]
WOMEN_CATEGORIES = ["D20", "DE"]


def main(
    oe_input_filename: Path=typer.Option(..., "--oe-entries", help="File CSV con iscrizioni OE"),
    men_ranking: Path=typer.Option(..., help="CSV con ranking maschile"),
    women_ranking: Path=typer.Option(..., help="CSV con ranking femminile"),
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

    typer.echo(f"Reading men ranking from CSV file {men_ranking}")
    with open(men_ranking, encoding=WRE_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        men_ranking_by_iof = {}
        for i, row in enumerate(reader):
            men_ranking_by_iof[row["IOF ID"]] = int(row["WRS Position"])

    typer.echo(f"Reading women ranking from CSV file {women_ranking}")
    with open(women_ranking, encoding=WRE_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        women_ranking_by_iof = {}
        for i, row in enumerate(reader):
            women_ranking_by_iof[row["IOF ID"]] = int(row["WRS Position"])


    reportData = []
    for classesList, ranking_by_iof in ((MEN_CATEGORIES, men_ranking_by_iof), (WOMEN_CATEGORIES, women_ranking_by_iof)):
        for className in classesList:
            typer.secho(f"Processing class {className}...", fg=typer.colors.BLUE)
            classEntries = []
            for i, row in enumerate(data):
                if row[CLASS_FIELD] == className:
                    worldRank = ranking_by_iof.get(row[IOFID_FIELD], 999999)
                    classEntries.append({
                        "ix": i,
                        "iofId": row[IOFID_FIELD],
                        "worldRank": worldRank,
                        "block": 1,
                    })
            

            maxBlock = math.ceil((len(classEntries) / BLOCK_SIZE)) * 2 + 1
            currentBlock = maxBlock
            classEntries.sort(key=lambda x: x["worldRank"])
            for i, entry in enumerate(classEntries):
                if i % BLOCK_SIZE == 0:
                    currentBlock -= 2
                entry["block"] = currentBlock
                data[entry["ix"]][BLOCK_FIELD] = str(currentBlock)
                data[entry["ix"]][IOFRANK_FIELD] = str(entry["worldRank"])
                data[entry["ix"]][DBRANK_FIELD] = str(entry["worldRank"])
                reportData.append({
                    "Class": className,
                    "IOF ID": str(entry["iofId"]),
                    "Name": f"{data[entry['ix']][FAMILY_NAME_FIELD]} {data[entry['ix']][GIVEN_NAME_FIELD]}",
                    "Rank": str(entry["worldRank"]),
                    "StartBlock": str(currentBlock),
                })

            typer.secho(f"Class {className} finished with block {currentBlock} from max block {maxBlock} and {len(classEntries)} entries.", fg=typer.colors.GREEN)

    df = pd.DataFrame(reportData)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)
    report_filename = output_filename.with_stem(f"{output_filename.stem}_report").with_suffix(".xlsx")
    typer.echo(f"Writing report to {report_filename}")
    df.to_excel(report_filename, index=False)

    typer.echo(f"Writing output to {output_filename}")
    with open(output_filename, 'w', encoding=CSV_OUTPUT_ENCODING) as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', delimiter=';', fieldnames=header_keys)

        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

