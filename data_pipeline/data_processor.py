"""
DS 3500 - MP1
Data processing module.
"""

import logging
import pandas as pd


logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows from the DataFrame."""

    before = len(df)
    result = df.drop_duplicates().copy()

    logger.debug(
        "Removed %d duplicate rows",
        before - len(result)
    )

    return result


def handle_missing(df, axis="rows"):
    """Remove rows or columns containing missing values."""

    if axis == "rows":
        before = len(df)

        result = df.dropna(axis=0).copy()

        logger.debug(
            "Removed %d rows with missing values",
            before - len(result)
        )

        return result

    if axis == "columns":
        before = len(df.columns)

        result = df.dropna(axis=1).copy()

        logger.debug(
            "Removed %d columns with missing values",
            before - len(result.columns)
        )

        return result

    logger.error(
        "Invalid missing value axis: %s",
        axis
    )

    raise ValueError(
        f"Invalid missing value axis: {axis}"
    )


def remove_outliers(df, columns, method, threshold):
    """Remove outliers using IQR or Z-score."""

    if method not in ["iqr", "zscore"]:
        logger.error(
            "Invalid outlier method: %s",
            method
        )

        raise ValueError(
            f"Invalid outlier method: {method}"
        )

    result = df.copy()

    for column in columns:

        if column not in result.columns:
            logger.warning(
                "Column not found: %s",
                column
            )
            continue

        if not pd.api.types.is_numeric_dtype(result[column]):
            logger.warning(
                "Column is not numeric: %s",
                column
            )
            continue

        if method == "iqr":

            q1 = result[column].quantile(0.25)
            q3 = result[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            before = len(result)

            result = result[
                (result[column] >= lower)
                & (result[column] <= upper)
            ].copy()

            logger.debug(
                "%s: method=%s, threshold=%s, removed=%d",
                column,
                method,
                threshold,
                before - len(result)
            )

        elif method == "zscore":

            mean = result[column].mean()
            std = result[column].std(ddof=0)

            if pd.isna(std) or std == 0:
                logger.debug(
                    "%s: skipping Z-score because standard deviation is zero",
                    column
                )
                continue

            z_scores = abs(
                (result[column] - mean) / std
            )

            before = len(result)

            result = result[
                z_scores <= threshold
            ].copy()

            logger.debug(
                "%s: method=%s, threshold=%s, removed=%d",
                column,
                method,
                threshold,
                before - len(result)
            )

    return result


def process_data(df, config):
    """Apply data-cleaning steps based on configuration settings."""

    processing = config["processing"]

    result = df.copy()

    if processing["remove_duplicates"]:
        result = remove_duplicates(result)

    missing_config = processing["missing"]

    if missing_config["enabled"]:
        result = handle_missing(
            result,
            axis=missing_config["axis"]
        )

    outlier_config = processing["outliers"]

    if outlier_config["enabled"]:
        result = remove_outliers(
            result,
            columns=outlier_config["columns"],
            method=outlier_config["method"],
            threshold=outlier_config["threshold"]
        )

    return result


def create_cleaning_report(df_before, df_after):
    """Create a report comparing data before and after cleaning."""

    report = {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": (
            len(df_before.columns)
            - len(df_after.columns)
        )
    }

    return report