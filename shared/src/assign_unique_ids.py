"""contains functions for assigning unique IDs to data without ids"""

import hashlib


def assign_unique_ids(df, *fieldnames):
    """assigns unique identifiers to each row in dataframe based on fields in fieldnames

    Args:
        df (pandas.DataFrame): dataframe to assign ids to
        *fieldnames: one or more column names to use to determine uniqueness

    Returns:
        pandas.DataFrame: dataframe with unique ids set
    """
    assert len(fieldnames) > 1, "You must provide at least one field"

    df["unique_id"] = df.apply(
        lambda row: hashlib.sha1(
            str.encode("-".join([str(row[fieldname]) for fieldname in fieldnames]))
        ).hexdigest(),
        axis=1,
    )

    # put unique id first
    df = df[
        ["unique_id"] + list(filter(lambda c: c != "unique_id", df.columns.tolist()))
    ]

    # check output
    found_rows = df.unique_id.nunique()
    expected_rows = len(df)
    if not found_rows == expected_rows:
        non_unique_ids = df[
            df.unique_id.duplicated() == True  # pylint: disable=singleton-comparison
        ].unique_id.unique()
        df[df.unique_id.isin(non_unique_ids)].to_csv(
            "output/dupe_rows.csv", index=False
        )

        raise ValueError(
            "assigning unique IDs did not result in fully unique IDs. "
            f"Found {found_rows} unique records, expected {expected_rows}.\n\n"
            "dumped the duplicated rows to output/dupe_rows.csv for inspection"
        )

    return df
