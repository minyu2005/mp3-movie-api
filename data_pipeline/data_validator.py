import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data."""

    result = df.copy()
    rows_before = len(result)

    # Check required columns
    for col in required_columns:
        if col not in result.columns:
            logger.error("Required column missing: %s", col)
            raise ValueError(f"Required column missing: {col}")

    # Check numeric columns
    for col in numeric_columns:
        invalid_rows = []

        for i, value in result[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid numeric value in %s at row %s: %s",
                        col,
                        i,
                        value
                    )
                    invalid_rows.append(i)

        if invalid_rows:
            logger.warning(
                "Removed %d rows with invalid numeric values in %s",
                len(invalid_rows),
                col
            )

            result = result.drop(index=invalid_rows)

        result[col] = pd.to_numeric(result[col])

    logger.debug(
        "Validation: %d -> %d rows",
        rows_before,
        len(result)
    )

    return result