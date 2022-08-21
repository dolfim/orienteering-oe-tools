# Tools for Naz 2022 in Campra (TI)

This is a collection of tools used to organize the Orienteering competitions
in Campra (TI) on 27th and 28th August 2022.

Event website: https://naz2022.o-92.ch/

### Competition details

| 8. National Orienteering Middle | 9. National Orienteering Long |
| --------------------------------|-------------------------------|
| Saturday, 27 August 2022        |Sunday, 28 August 2022         |
| Campra                          |Dötra and Pian Segno           |
| [IOF World Ranking Event](https://eventor.orienteering.org/Events/Show/7433) (forest)|[IOF World Ranking Event](https://eventor.orienteering.org/Events/Show/7434) (forest)|
| JEC Trial event                 | JEC Trial event               |
| Swiss PISTE H/D16-20            | Swiss PISTE H/D12-20          |

- The competitions are managed using OEv11
- Registrations done with the portal go2ol.ch
- Both competitions were registered as WRE
- We printed start number for the runners, such that the jury could easily disqualify who enters the forbidden zones. The start number was the same between the two competitions.

## Tools

### Import IOF Eventor entries

Append the IOF Eventor registrations to the CVS file exported from GO2OL.

```shell
python3 add_eventor_entries.py --eventor-entries entries_8._National_Orienteering_Middle.xml --oe-entries 8__Nationaler_OL__registrations_oe2010.csv --output 8naz_entries_go2ol_eventor.csv
```

### Import late registrations

Add late registrations from a table containing SOLV-nr, Class and (optional) SI-Card.
The rest of the athlete's details is imported from the SOLV Läufer-DB.

```shell
python add_late_entries.py --oe-entries 8__Nationaler_OL__registrations_oe2010.csv --solv-db data/solv-competitors.csv --late-entries Iscrizioni_tardive.xlsx  --sheet-name Sabato --output 8naz_entries_go2ol_eventor_late.csv
```

### Add missing IOF ID

Assign the missing IOF ID from a manually curated list.

```shell
python fix_missing_iof.py --oe-entries 8__Nationaler_OL__registrations_oe2010.csv --missing-iof missing_iof_id_36.xlsx  --output 8naz_entries_go2ol_eventor_late_ioffix.csv
```

### Define start blocks for reverse IOF ranking

This script is creating blocks of size `BLOCK_SIZE=10` for drawing the start lists
according to WRE regulations.

The best athletes will be in the block stating last.

```shell
python define_wre_start_blocks.py --oe-entries 8naz_entries_go2ol_eventor.csv --men-ranking data/iof_ranking_MEN_F_18-08-2022.csv --women-ranking data/iof_ranking_WOMEN_F_18-08-2022.csv --output 8naz_entries_go2ol_eventor_rank.csv
```

### Assign a common startnr among multiple events

Assign a common start number among multiple events, using the following rules:

- Elite classes `ELITE_CLASSES = ("HE", "H20", "DE", "D20")` will get the lowest numbers
- All other classes will start at the next hundred. If there are 123 elite athletes, the next
  classes will start with 201
- Drawing within a class is random
- Bedise Elite, all other classes are sorted according to the SOLV class number
- Athletes are identified among events by the tuple {Lastname, Givenname, Birth year, Class}

```shell
python define_common_startnr.py data/8__Nationaler_OL__registrations_oe2010.csv data/9__Nationaler_OL__registrations_oe2010.csv
```

---

All the steps above are concatenated via the script `prepare_entries.sh`.
This script will produce the following final files:

```shell
$ ./prepare_entries.sh
...
Writing output to 8naz_entries_final_startnr.csv
Writing output to 9naz_entries_final_startnr.csv
```

---

### Update start block with new WRE list

If we have to update the WRE start block, we proceed as
1. Export from OE the latest version of the competition. Select only the Elite classes.
2. Run again the `define_wre_start_blocks.py` script with the new list
3. Import as new registration
4. Manually or automatically regerate the start list for these categories.

If the OE export is in another language, modify this import line

```diff
22c22
< from oe_columns.de import *
---
> from oe_columns.it import *
```

Run as:

```shell
python define_wre_start_blocks.py --oe-entries 8naz_liste_partenza_elite.csv --men-ranking data/iof_ranking_MEN_F_18-08-2022.csv --women-ranking data/iof_ranking_WOMEN_F_18-08-2022.csv --output 8naz_elite_blocks.csv
```

### Combine events for printing startnr

After the start lists are generated in OE, we combine the two OE export files into a single table
which is used to print the start numbers.

python export_startnr_for_print.py --oe-input-1="8Naz_Liste_di_partenza.csv" --oe-input-2="9Naz_Liste_di_partenza.csv" --zero-1="12:00:00" --zero-2="09:00:00" --output NazCampra2022_Startnr.xlsx
