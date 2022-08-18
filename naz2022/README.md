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

TODO


### Define start blocks for reverse IOF ranking

This script is creating blocks of size `BLOCK_SIZE=10` for drawing the start lists
according to WRE regulations.

The best athletes will be in the block stating last.

```shell
python define_wre_start_blocks.py --oe-entries 8naz_entries_go2ol_eventor.csv --men-ranking data/iof_ranking_MEN_F_18-08-2022.csv --women-ranking data/iof_ranking_WOMEN_F_18-08-2022.csv --output 8naz_entries_go2ol_eventor_rank.csv
```

### Assign a unique startnr among multiple events

TODO


### Combine events for printing startnr

After the start lists are generated in OE.

TODO