# Return A Cleaning

Performs the following transformations:
1. transforms wide output of fixed-width file to one row per agency per category per month
2. converts FBI's bizarre negative number notation to integers
3. replaces all totals that are <= 0 with null [^1]

[^1]: see "Analysis of Missingness in UCR Crime Data", page 3
