#!/usr/bin/env python3

import csv
from dataclasses import dataclass
import datetime
import pandas as pd
from pathlib import Path
from typing import Dict, List, Set, Tuple

import typer


CSV_INPUT_ENCODING = 'ISO-8859-1'
CSV_OUTPUT_ENCODING = 'ISO-8859-1'

CLASSES_FILE = "resources/solv-classes.csv"

from oe_columns.it import *
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD, STARTNR_FIELD)

OUTPUT_COLUMNS = (
    "Startnummer",
    "Vorname",
    "Nachname",
    "Start (Sabato)",
    "Kategorie (Sabato)",
    "Startzeit (Sabato)",
    "Start (Domenica)",
    "Kategorie (Domenica)",
    "Startzeit (Domenica)",
)

START_MAPPING = {
    0: {
        "HE": "START 1",
        "HAL": "START 1",
        "HAM": "START 1",
        "HAK": "START 2",
        "HB": "START 2",
        "H35": "START 1",
        "H40": "START 1",
        "H45": "START 1",
        "H50": "START 1",
        "H55": "START 1",
        "H60": "START 2",
        "H65": "START 2",
        "H70": "START 2",
        "H75": "START 2",
        "H80": "START 2",
        "H85": "START 2",
        "H20": "START 1",
        "H18": "START 1",
        "H16": "START 2",
        "H14": "START 2",
        "H12": "START 2",
        "H10": "START 2",

        "DE": "START 1",
        "DAL": "START 1",
        "DAM": "START 1",
        "DAK": "START 2",
        "DB": "START 2",
        "D35": "START 1",
        "D40": "START 1",
        "D45": "START 1",
        "D50": "START 1",
        "D55": "START 1",
        "D60": "START 2",
        "D65": "START 2",
        "D70": "START 2",
        "D75": "START 2",
        "D80": "START 2",
        "D20": "START 1",
        "D18": "START 1",
        "D16": "START 2",
        "D14": "START 2",
        "D12": "START 2",
        "D10": "START 2",

        "OL": "START 2",
        "OM": "START 2",
        "OK": "START 2",
    },
    1: {
        "HE": "START 1",
        "HAL": "START 1",
        "HAM": "START 1",
        "HAK": "START 2",
        "HB": "START 2",
        "H35": "START 1",
        "H40": "START 1",
        "H45": "START 1",
        "H50": "START 1",
        "H55": "START 1",
        "H60": "START 1",
        "H65": "START 1",
        "H70": "START 2",
        "H75": "START 2",
        "H80": "START 2",
        "H85": "START 2",
        "H20": "START 1",
        "H18": "START 1",
        "H16": "START 1",
        "H14": "START 2",
        "H12": "START 2",
        "H10": "START 2",

        "DE": "START 1",
        "DAL": "START 1",
        "DAM": "START 1",
        "DAK": "START 2",
        "DB": "START 2",
        "D35": "START 1",
        "D40": "START 1",
        "D45": "START 1",
        "D50": "START 1",
        "D55": "START 1",
        "D60": "START 2",
        "D65": "START 2",
        "D70": "START 2",
        "D75": "START 2",
        "D80": "START 2",
        "D20": "START 1",
        "D18": "START 1",
        "D16": "START 1",
        "D14": "START 2",
        "D12": "START 2",
        "D10": "START 2",

        "OL": "START 2",
        "OM": "START 2",
        "OK": "START 2",
    },
}

NameTuple = Tuple[str, str, str]

@dataclass
class Run:
    data: List[dict]
    header_keys: List[str]
    ix_by_name: Dict[NameTuple, int]
    ix_by_field: Dict[str, Dict[str, int]]
    filename: Path
    zero_time: str

def _make_name_key(row):
    return (row[FAMILY_NAME_FIELD], row[GIVEN_NAME_FIELD], row[BIRTH_FIELD], row[CLASS_FIELD])


def load_run(input_filename: Path, zero_time: str):
    splits = zero_time.split(':')
    time_offset = datetime.timedelta(hours=int(splits[0]), minutes=int(splits[1]))

    typer.echo(f"Reading entries from CSV file {input_filename}")

    with open(input_filename, encoding=CSV_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        data = []
        header_keys = None
        data_by_name: Dict[NameTuple, int] = {}
        data_by_index = {ix: {} for ix in INDEX_COLS}
        for i, row in enumerate(reader):
            if not header_keys: header_keys = list(row.keys())

            start_time = datetime.datetime.strptime(row[START_FIELD], '%H:%M:%S')
            row[START_FIELD] = (time_offset + start_time).strftime('%H:%M')
            data.append(row)
            
            for ix in INDEX_COLS:
                if row[ix] != "0" and row[ix] != "":
                    data_by_index[ix][row[ix]] = i

            if row[FAMILY_NAME_FIELD] != VACANCY_NAME:
                name_key = _make_name_key(row)
                if name_key in data_by_name:
                    print("Duplicate", name_key)
                    raise RuntimeError("Name key is not unique enough")
                data_by_name[name_key] = i

    return Run(data, header_keys, data_by_name, data_by_index, zero_time, input_filename)

def main(
    oe_input_filename_1: Path=typer.Option(..., "--oe-input-1", help="CSV file with OE start list for run 1"),
    zero_time_1: str=typer.Option(..., "--zero-1", help="Zero time for run 1"),

    oe_input_filename_2: Path=typer.Option(..., "--oe-input-2", help="CSV file with OE start list for run 2"),
    zero_time_2: str=typer.Option(..., "--zero-2", help="Zero time for run 2"),

    output_filename: Path=typer.Option(..., "--output", help="Excel output file")
    ):
    
    runs: List[Run] = []
    runs.append(load_run(oe_input_filename_1, zero_time_1))
    runs.append(load_run(oe_input_filename_2, zero_time_2))
    
    all_startnr: Set[str] = {
        *runs[0].ix_by_field[STARTNR_FIELD].keys(),
        *runs[1].ix_by_field[STARTNR_FIELD].keys(),
    }

    # "Startnummer",
    # "Vorname",
    # "Nachname",
    # "Start (Sabato)",
    # "Kategorie (Sabato)",
    # "Startzeit (Sabato)",
    # "Start (Domenica)",
    # "Kategorie (Domenica)",
    # "Startzeit (Domenica)",
    output_data = []
    for startnr in sorted(all_startnr, key=lambda x: int(x)):
        entry = None

        sa_data = ("", "", "")
        if startnr in runs[0].ix_by_field[STARTNR_FIELD]:
            entry = runs[0].data[runs[0].ix_by_field[STARTNR_FIELD][startnr]]
            sa_data = (
                START_MAPPING[0][entry[CLASS_FIELD]],
                entry[CLASS_FIELD],
                entry[START_FIELD],
            )

        do_data = ("", "", "")
        if startnr in runs[1].ix_by_field[STARTNR_FIELD]:
            entry = runs[1].data[runs[1].ix_by_field[STARTNR_FIELD][startnr]]
            do_data = (
                START_MAPPING[1][entry[CLASS_FIELD]],
                entry[CLASS_FIELD],
                entry[START_FIELD],
            )
        
        if entry[FAMILY_NAME_FIELD] == VACANCY_NAME:
            continue

        output_data.append([
            startnr,
            entry[GIVEN_NAME_FIELD],
            entry[FAMILY_NAME_FIELD],
            *sa_data,
            *do_data,
        ])
    df = pd.DataFrame(output_data, columns=OUTPUT_COLUMNS)



    typer.echo(f"Writing report to {output_filename}")
    df.to_excel(output_filename, index=False)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

