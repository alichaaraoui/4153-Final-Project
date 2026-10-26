"""Joining per-applicant feature tables onto the application table.

The application table has exactly one row per applicant, and so must the result. A join that
silently adds rows (because a child table was not aggregated) or drops rows (because of an
inner join) still runs without an error, and the model then trains on the wrong data. The
functions here make that mistake fail loudly instead.
"""

from __future__ import annotations

import pandas as pd

# PROVIDED: a feature whose name ends with this is a count, so "no records" means 0.
COUNT_SUFFIX = "_COUNT"


def assert_one_row_per_applicant(
    df: pd.DataFrame, expected_ids: pd.Series, id_col: str = "SK_ID_CURR"
) -> None:
    """Raise a ValueError unless ``df`` has exactly one row for each id in ``expected_ids``.

    Args:
        df: The table to check (for example the joined feature table).
        expected_ids: The applicant ids that must each appear exactly once.
        id_col: The applicant id column.

    Raises:
        ValueError: if the row count differs, any id appears twice, or the set of ids is not
            exactly ``expected_ids``. The message must say which problem it found and give
            the numbers (for example "24,395 rows for 5,000 applicants").

    Hints:
        - Equal row counts are not enough on their own: one duplicated id plus one missing id
          keeps the count the same.
    """
    if id_col not in df.columns:
        raise ValueError(f"{id_col} column missing from table with columns {list(df.columns)}")

    actual_ids = df[id_col]
    expected_ids = pd.Series(expected_ids).reset_index(drop=True)

    n_expected = len(expected_ids)
    n_actual = len(df)
    if n_actual != n_expected:
        raise ValueError(f"{n_actual} rows for {n_expected} applicants")

    duplicates = actual_ids[actual_ids.duplicated()].unique()
    if len(duplicates):
        dup_list = ", ".join(str(x) for x in duplicates[:10])
        raise ValueError(f"duplicate applicant ids found: {dup_list}")

    actual_set = set(actual_ids.tolist())
    expected_set = set(expected_ids.tolist())
    if actual_set != expected_set:
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)
        if missing and extra:
            raise ValueError(
                f"{len(missing)} missing and {len(extra)} extra applicant ids; "
                f"missing={missing[:10]}, extra={extra[:10]}"
            )
        if missing:
            raise ValueError(f"{len(missing)} missing applicant ids: {missing[:10]}")
        raise ValueError(f"{len(extra)} extra applicant ids: {extra[:10]}")


def join_features(
    app: pd.DataFrame, feature_tables: dict[str, pd.DataFrame], id_col: str = "SK_ID_CURR"
) -> pd.DataFrame:
    """Left-join each per-applicant feature table onto the application table.

    Args:
        app: The application table, one row per applicant.
        feature_tables: Table name -> aggregated table (the output of an ``aggregate_*``
            function), for example ``{"bureau": aggregate_bureau(bureau)}``.
        id_col: The applicant id column.

    Returns:
        A new DataFrame with the same rows in the same order as ``app``, every column of
        ``app`` unchanged, plus every feature column. For applicants missing from a feature
        table, columns ending in ``_COUNT`` are 0 and every other new column is NaN.

    Raises:
        ValueError: before joining, if a feature table has the same id twice (name the table:
            it was probably not aggregated), or if a feature column name is already taken.
            After joining, through ``assert_one_row_per_applicant``.

    Hints:
        - Which ``how=`` keeps every applicant, including the ones with no history at all?
        - ``pd.merge`` has a ``validate=`` argument that can raise on duplicate keys for you.
        - Why 0 for counts but NaN for averages? Be ready to explain it at the checkpoint.
    """
    out = app.copy()
    if not feature_tables:
        assert_one_row_per_applicant(out, app[id_col], id_col=id_col)
        return out

    for table_name, table in feature_tables.items():
        if id_col not in table.columns:
            raise ValueError(f"{table_name} is missing {id_col}")
        if table[id_col].duplicated().any():
            raise ValueError(f"{table_name} has duplicate {id_col} values; it was not aggregated")

        for col in table.columns:
            if col == id_col:
                continue
            if col in out.columns:
                raise ValueError(f"Feature column '{col}' already exists in the application table")

        out = out.merge(table, on=id_col, how="left", validate="one_to_one")

        for col in table.columns:
            if col == id_col:
                continue
            if col.endswith(COUNT_SUFFIX):
                out[col] = out[col].fillna(0)

    assert_one_row_per_applicant(out, app[id_col], id_col=id_col)

    return out
