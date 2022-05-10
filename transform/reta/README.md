# Return A Cleaning

Performs the following transformations:
1. transforms wide output of fixed-width file to one row per agency per category per month
2. drops all rows that are missing data in the fields defined in the INDEX_COLS variable at the top of [src/transform_reta.py](src/transform_reta.py)
3. transforms values based on yaml files in [hand/](hand/)
4. converts FBI's bizarre negative number notation to integers [^1]
5. drops other number notation values that aren't documented in ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)
6. standardizes ORI fields to match the format of other datasets
7. drops duplicate rows
    - This is because at least one agency "MD INVESTIGATIVE SERV" (ORI MD0021000) appears to have submitted twice in 1996. The values are the same, so dropping duplicates
8. assigns unique IDs based on row values

Disclaimers: 
- Some values appear to be negative entries, but aren't documented in the FBI's documentation. They are dropped. 

[^1]: see ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)
