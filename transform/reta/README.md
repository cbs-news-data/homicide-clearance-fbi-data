# Return A Cleaning

Performs the following transformations:
1. transforms wide output of fixed-width file to one row per agency per category per month
2. selects only murder-related records
3. drops all rows that are missing data in the fields defined in the INDEX_COLS variable at the top of [src/transform_reta.py](src/transform_reta.py)
4. converts FBI's bizarre negative number notation to integers [^1]
5. drops other number notation values that aren't documented in ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)

Disclaimers: 
- Some values appear to be negative entries, but aren't documented in the FBI's documentation. They are dropped. 

[^1]: see ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)
