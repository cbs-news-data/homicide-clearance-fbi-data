# Return A Cleaning

Performs the following transformations:
1. transforms wide output of fixed-width file to one row per agency per category per month
2. drops all rows that are missing data in the fields defined in the INDEX_COLS variable at the top of [src/transform_reta.py](src/transform_reta.py)
3. converts FBI's bizarre negative number notation to integers [^1]
4. drops other number notation values that aren't documented in ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)
5. replaces all totals that are <= 0 with null [^2]

Disclaimers: 
- Some values appear to be negative entries, but aren't documented in the FBI's documentation. They are dropped. 


[^1]: see ["Ret A negative entries"](../../documents/Ret%20A%20negative%20entries.pdf)
[^2]: see ["Analysis of Missingness in UCR Crime Data"](../../documents/Analysis%20of%20Missingness%20in%20UCR%20Crime%20Data.pdf), page 3
