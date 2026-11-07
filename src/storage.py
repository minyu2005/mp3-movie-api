
import logging
import sqlite3

import pandas as pd

from .database import get_connection, initialize_database

logger = logging.getLogger(__name__)

MOVIE_COLUMNS = ["title", "release_year", "rating", "genre"]


class MovieStorage:
    def __init__(self, db_path="data/movies.db"):
        self.db_path = db_path
        initialize_database(self.db_path)

    def save(self, df):
        """Replace all movie rows in one transaction."""
        connection = get_connection(self.db_path)

        try:
            clean_df = df[MOVIE_COLUMNS].astype(object)
            clean_df = clean_df.where(pd.notna(clean_df), None)

            rows = list(clean_df.itertuples(index=False, name=None))

            connection.execute("DELETE FROM movies")

            connection.executemany(
                """
                INSERT INTO movies
                (title, release_year, rating, genre)
                VALUES (?, ?, ?, ?)
                """,
                rows
            )

            connection.commit()
            logger.debug("Stored movies in SQLite: rows=%d", len(rows))

        except sqlite3.Error:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get(self):
        """Return all movie columns as a DataFrame."""
        connection = get_connection(self.db_path)

        try:
            cursor = connection.execute(
                """
                SELECT title, release_year, rating, genre
                FROM movies
                ORDER BY id
                """
            )

            rows = cursor.fetchall()

            return pd.DataFrame(
                [dict(row) for row in rows],
                columns=MOVIE_COLUMNS
            )

        finally:
            connection.close()

    def select_columns(self, columns, limit=5):
        """Return id and selected columns."""
        if not columns:
            raise ValueError("Select at least one column")

        for column in columns:
            if column not in MOVIE_COLUMNS:
                raise ValueError(f"Unsupported column: {column}")

        selected_columns = ", ".join(["id"] + columns)
        connection = get_connection(self.db_path)

        try:
            cursor = connection.execute(
                f"""
                SELECT {selected_columns}
                FROM movies
                ORDER BY id
                LIMIT ?
                """,
                (limit,)
            )

            results = [dict(row) for row in cursor.fetchall()]
            logger.debug("Selected movies: rows=%d", len(results))
            return results

        finally:
            connection.close()

    def count_movies(self):
        """Count stored movies using SQL."""
        connection = get_connection(self.db_path)

        try:
            cursor = connection.execute(
                "SELECT COUNT(*) FROM movies"
            )
            return cursor.fetchone()[0]

        finally:
            connection.close()

    def query_movies(self, columns, min_rating, limit):
        """Filter and sort movies using SQL."""
        if not columns:
            raise ValueError("Select at least one column")

        for column in columns:
            if column not in MOVIE_COLUMNS:
                raise ValueError(f"Unsupported column: {column}")

        selected_columns = ", ".join(["id"] + columns)
        connection = get_connection(self.db_path)

        try:
            cursor = connection.execute(
                f"""
                SELECT {selected_columns}
                FROM movies
                WHERE rating >= ?
                ORDER BY rating DESC, id ASC
                LIMIT ?
                """,
                (min_rating, limit)
            )

            results = [dict(row) for row in cursor.fetchall()]

            logger.debug(
                "Queried movies: columns=%s, returned_rows=%d",
                columns,
                len(results)
            )

            return results

        finally:
            connection.close()
