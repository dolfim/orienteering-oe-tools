#!/usr/bin/env python3

import csv
from dataclasses import dataclass
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

import typer


CSV_INPUT_ENCODING = 'ISO-8859-1'
CSV_OUTPUT_ENCODING = 'ISO-8859-1'

CLASSES_FILE = "resources/solv-classes.csv"

IOFID_FIELD = "Num3"
SOLVNR_FIELD = "Datenbank Id"
SICARD_FIELD = "Chipnr"
CLASS_FIELD = "Kurz"
CLASSNR_FIELD = "Katnr"
BLOCK_FIELD = "Block"
GIVEN_NAME_FIELD = "Vorname"
FAMILY_NAME_FIELD = "Nachname"
BIRTH_FIELD = "Jg"
STARTNR_FIELD = "Stnr"
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD)

ELITE_CLASSES = ("HE", "H20", "DE", "D20")

NameTuple = Tuple[str, str, str]

@dataclass
class Run:
    data: List[dict]
    header_keys: List[str]
    ix_by_name: Dict[NameTuple, int]
    ix_by_field: Dict[str, Dict[str, int]]
    filename: Path

def _make_name_key(row):
    return (row[FAMILY_NAME_FIELD], row[GIVEN_NAME_FIELD], row[BIRTH_FIELD], row[CLASS_FIELD])

def round_up_to_nearest_100(num):
    return math.ceil(num / 100) * 100

def main(
    oe_input_filenames: List[Path]=typer.Argument(..., help="File CSV con iscrizioni OE"),
    ):
    
    typer.echo(f"Reading classes metadata from CSV file {CLASSES_FILE}")
    with open(CLASSES_FILE, encoding=CSV_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        classesRefs = []
        for row in reader:
            classesRefs.append(row)
        classesRefs.sort(key=lambda x: int(x[CLASSNR_FIELD]))


    all_entries: Dict[NameTuple, Dict[int, int]] = {}
    all_entries_per_class: Dict[str, Dict[NameTuple, Dict[int, int]]] = {}
    runs: List[Run] = []
    for irun, input_filename in enumerate(oe_input_filenames):
        typer.echo(f"Reading entries from CSV file {input_filename}")
        with open(input_filename, encoding=CSV_INPUT_ENCODING) as csvfile:
            reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
            
            data = []
            header_keys = None
            data_by_name: Dict[NameTuple, int] = {}
            data_by_index = {ix: {} for ix in INDEX_COLS}
            for i, row in enumerate(reader):
                if not header_keys: header_keys = list(row.keys())
                data.append(row)
                
                for ix in INDEX_COLS:
                    if row[ix] != "0" and row[ix] != "":
                        data_by_index[ix][row[ix]] = i

                name_key = _make_name_key(row)
                if name_key in data_by_name:
                    print("Duplicate", name_key)
                    raise RuntimeError("Name key is not unique enough")
                data_by_name[name_key] = i

                all_entries.setdefault(name_key, {})[irun] = i

                all_entries_per_class.setdefault(row[CLASS_FIELD], {})
                all_entries_per_class[row[CLASS_FIELD]].setdefault(name_key, {})[irun] = i

        typer.secho(f"Number of enties {len(data)}", fg=typer.colors.BLUE)
        runs.append(Run(data, header_keys, data_by_name, data_by_index, input_filename))

    typer.secho(f"Total number of enties {len(all_entries)}", fg=typer.colors.BLUE)

    total_elite = 0
    for className, entries in sorted(all_entries_per_class.items()):
        if className in ELITE_CLASSES:
            total_elite += len(entries)
        typer.echo(f"{className}    {len(entries)}")

    starting_nr = round_up_to_nearest_100(total_elite)
    typer.echo(f"Number of elite {total_elite}, stating other classes with {starting_nr}")
    
    # Elite start nr
    startnr = 1
    for className in ELITE_CLASSES:
        flat_entries = list(all_entries_per_class[className].items())
        random.shuffle(flat_entries)
        entries = dict(flat_entries)
        for i, (name_key, entry_ix) in enumerate(entries.items()):
            for irun, ix in entry_ix.items():
                runs[irun].data[ix][STARTNR_FIELD] = str(startnr)
            startnr += 1

    # Others start nr
    startnr = starting_nr + 1
    for classRef in classesRefs:
        className = classRef[CLASS_FIELD]
        if className in ELITE_CLASSES or className not in all_entries_per_class:
            continue

        flat_entries = list(all_entries_per_class[className].items())
        random.shuffle(flat_entries)
        entries = dict(flat_entries)
        for i, (name_key, entry_ix) in enumerate(entries.items()):
            for irun, ix in entry_ix.items():
                runs[irun].data[ix][STARTNR_FIELD] = str(startnr)
            startnr += 1


    for run in runs:
        output_filename = run.filename.with_stem(f"{run.filename.stem}_startnr")
        typer.echo(f"Writing output to {output_filename}")
        with open(output_filename, 'w', encoding=CSV_OUTPUT_ENCODING) as csvfile:
            writer = csv.DictWriter(csvfile, dialect='excel', delimiter=';', fieldnames=run.header_keys)

            writer.writeheader()
            writer.writerows(run.data)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

