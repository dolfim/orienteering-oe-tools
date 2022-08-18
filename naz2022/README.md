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
