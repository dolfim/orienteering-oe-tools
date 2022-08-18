#!/usr/bin/env python3

import csv
import itertools
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

import typer


CSV_INPUT_ENCODING = 'ISO-8859-1'
CSV_OUTPUT_ENCODING = 'ISO-8859-1'

XML_INPUT_ENCODING = 'UTF8'
XML_OUTPUT_ENCODING = 'UTF8'

IOFID_FIELD = "Num3"
SOLVNR_FIELD = "Datenbank Id"
SICARD_FIELD = "Chipnr"
INDEX_COLS = (SICARD_FIELD, SOLVNR_FIELD, IOFID_FIELD)


ns = {'iof': 'http://www.orienteering.org/datastandard/3.0'}
ET.register_namespace('', ns['iof'])


def _make_name_key(row):
    return (row["Nachname"], row["Vorname"], row["Jg"])

def _field_or_default(item, xml_path, default=""):
    field = item.find(xml_path, ns)
    if field is None:
        return default
    return field.text

def main(
    eventor_input_filename: Path=typer.Option(..., "--eventor-entries", help="File XML con iscrizioni Eventor"),
    oe_input_filename: Path=typer.Option(..., "--oe-entries", help="File CSV con iscrizioni OE"),
    output_filename: Path=typer.Option(..., "--output", help="File CSV di output")
    ):
    
    typer.echo(f"Reading entries from CSV file {oe_input_filename}")
    with open(oe_input_filename, encoding=CSV_INPUT_ENCODING) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';')
        
        data = []
        header_keys = None
        data_by_index = {ix: {} for ix in INDEX_COLS}
        data_by_name = {}
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


    typer.echo(f"Reading entries from XML Eventor file {eventor_input_filename}")
    with open(eventor_input_filename, encoding=XML_INPUT_ENCODING) as xmlfile:
        root = ET.fromstring(xmlfile.read())
    
    total_eventor = 0
    total_added = 0
    for item in root.findall('.//iof:PersonEntry', ns):
        total_eventor += 1

        idField = item.find('iof:Person/iof:Id', ns)
        familyNameField = item.find('iof:Person/iof:Name/iof:Family', ns)
        givenNameField = item.find('iof:Person/iof:Name/iof:Given', ns)
        birthdayField = item.find('iof:Person/iof:BirthDate', ns)
        
        ixIofId = idField.text
        ixSicard = _field_or_default(item, "iof:ControlCard")
        birthYear = birthdayField.text.split('-')[0]
        ixNameKey = (familyNameField.text, givenNameField.text, birthYear)

        if ixIofId in data_by_index[IOFID_FIELD]:
            typer.secho(f"Runner IOF {ixIofId} already found by IOF ID. Skipping.", fg=typer.colors.BLUE)
            continue

        if ixSicard in data_by_index[SICARD_FIELD]:
            typer.secho(f"Runner IOF {ixIofId} already found by SI-Card. Skipping.", fg=typer.colors.BLUE)
            continue

        if ixNameKey in data_by_name:
            typer.secho(f"Runner IOF {ixIofId} already found by Name. Skipping.", fg=typer.colors.BLUE)
            continue
        

        typer.secho(f"Adding competitor IOF {ixIofId}", fg=typer.colors.YELLOW)
        iofClassName = item.find("iof:Class/iof:Name", ns).text
        if iofClassName == "Men":
            className = "HE"
            gender = "M"
        elif iofClassName == "Women":
            className = "DE"
            gender = "F"
        else:
            raise RuntimeError(f"Unknowen class name {iofClassName}")

        row = {
            "Chipnr": _field_or_default(item, "iof:ControlCard"),
            "Datenbank Id": "",
            "Nachname": _field_or_default(item, "iof:Person/iof:Name/iof:Family"),
            "Vorname": _field_or_default(item, "iof:Person/iof:Name/iof:Given"),
            "Jg": birthYear,
            "Geschlecht": gender,
            "Block": "",
            "Club-Nr.": "",
            "Abk": "",
            "Ort": _field_or_default(item, "iof:Organisation/iof:Name"),
            "Nat": _field_or_default(item, "iof:Organisation/iof:Country"),
            # "Sitz": _field_or_default(item, "iof:Organisation/iof:Country"),
            "Region": "",
            "Katnr": "",
            "Kurz": className,
            "Lang": "",
            "Num3": ixIofId,
            "Adr. Nachname": _field_or_default(item, "iof:Person/iof:Name/iof:Family"),
            "Adr. Vorname": _field_or_default(item, "iof:Person/iof:Name/iof:Given"),
            "Straße": "",
            "PLZ": "",
            "Adr. Ort": "",
            "EMail": "",
            "Gemietet": "0",
            "Startgeld": _field_or_default(item, "iof:AssignedFee/iof:Fee/iof:Amount"),
            "Bezahlt": "0",
        }
        data.append(row)
        total_added += 1
        
    typer.echo(f"Writing output to {output_filename}")
    with open(output_filename, 'w', encoding=CSV_OUTPUT_ENCODING) as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', delimiter=';', fieldnames=header_keys)

        writer.writeheader()
        writer.writerows(data)

    typer.secho(f'Total Eventor entries: {total_eventor}', fg=typer.colors.GREEN)
    typer.secho(f'Added new entries: {total_added}', fg=typer.colors.GREEN)
    typer.secho(f'Total entries: {len(data)}', fg=typer.colors.GREEN)


if __name__ == '__main__':
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()

