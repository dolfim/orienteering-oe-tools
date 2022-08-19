#!/bin/bash

DATA_ROOT="$HOME/Library/CloudStorage/OneDrive-Personal/CO/NazCampra2022/NazCampra2022 - IT/Iscrizioni"
GO2OL_8NAZ_ENTRIES="${DATA_ROOT}/8__Nationaler_OL__registrations_oe2010.csv"
EVENTOR_8NAZ_ENTRIES="${DATA_ROOT}/entries_8._National_Orienteering_Middle.xml"
GO2OL_8NAZ_NOIOF="${DATA_ROOT}/missing_iof_id_36.xlsx"

GO2OL_9NAZ_ENTRIES="${DATA_ROOT}/9__Nationaler_OL__registrations_oe2010.csv"
EVENTOR_9NAZ_ENTRIES="${DATA_ROOT}/entries_9._National_Orienteering_Long.xml"
GO2OL_9NAZ_NOIOF="${DATA_ROOT}/missing_iof_id_35.xlsx"

RANKING_MEN="${DATA_ROOT}/iof_ranking_MEN_F_19-08-2022.csv"
RANKING_WOMEN="${DATA_ROOT}/iof_ranking_WOMEN_F_19-08-2022.csv"

LATE_ENTRIES="${DATA_ROOT}/Iscrizioni tardive.xlsx"

SOLV_DB="${DATA_ROOT}/solv-competitors.csv"


# 8. Naz

python add_eventor_entries.py \
    --oe-entries "${GO2OL_8NAZ_ENTRIES}" \
    --eventor-entries "${EVENTOR_8NAZ_ENTRIES}" \
    --output 8naz_entries_go2ol_eventor.csv

python add_late_entries.py \
    --oe-entries 8naz_entries_go2ol_eventor.csv \
    --solv-db "${SOLV_DB}" \
    --late-entries "${LATE_ENTRIES}" --sheet-name Sabato \
    --output 8naz_entries_go2ol_eventor_late.csv

python fix_missing_iof.py \
    --oe-entries 8naz_entries_go2ol_eventor_late.csv \
    --missing-iof "${GO2OL_8NAZ_NOIOF}" \
    --output 8naz_entries_go2ol_eventor_late_ioffix.csv

python define_wre_start_blocks.py \
    --oe-entries 8naz_entries_go2ol_eventor_late_ioffix.csv \
    --men-ranking "${RANKING_MEN}" \
    --women-ranking "${RANKING_WOMEN}" \
    --output 8naz_entries_final.csv


# 9. Naz
python add_eventor_entries.py \
    --oe-entries "${GO2OL_9NAZ_ENTRIES}" \
    --eventor-entries "${EVENTOR_9NAZ_ENTRIES}" \
    --output 9naz_entries_go2ol_eventor.csv

python add_late_entries.py \
    --oe-entries 9naz_entries_go2ol_eventor.csv \
    --solv-db "${SOLV_DB}" \
    --late-entries "${LATE_ENTRIES}" --sheet-name Domenica \
    --output 9naz_entries_go2ol_eventor_late.csv

python fix_missing_iof.py \
    --oe-entries 9naz_entries_go2ol_eventor_late.csv \
    --missing-iof "${GO2OL_9NAZ_NOIOF}" \
    --output 9naz_entries_go2ol_eventor_late_ioffix.csv

python define_wre_start_blocks.py \
    --oe-entries 9naz_entries_go2ol_eventor_late_ioffix.csv \
    --men-ranking "${RANKING_MEN}" \
    --women-ranking "${RANKING_WOMEN}" \
    --output 9naz_entries_final.csv



# Common parts

python define_common_startnr.py \
    8naz_entries_final.csv 9naz_entries_final.csv

