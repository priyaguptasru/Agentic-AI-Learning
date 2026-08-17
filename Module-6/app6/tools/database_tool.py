import os

from sqlalchemy import create_engine, inspect, text


class DatabaseTool:
    """
    Database access tool.

    Responsibilities:
    1. Connect to PostgreSQL.
    2. Provide database schema information.
    3. Execute read-only SELECT queries.
    """

    def __init__(self):

        database_url = os.getenv("DATABASE_URL")

        if not database_url:

            raise ValueError("DATABASE_URL is not configured.")

        self.engine = create_engine(database_url)

    # =====================================================
    # GET DATABASE SCHEMA
    # =====================================================

    def get_schema(self):

        inspector = inspect(self.engine)

        schema_lines = []

        # -------------------------------------------------
        # Get all tables
        # -------------------------------------------------

        tables = inspector.get_table_names()

        if not tables:

            return "No tables were found in the database."

        # -------------------------------------------------
        # Get columns for every table
        # -------------------------------------------------

        for table_name in tables:

            schema_lines.append(f"TABLE: {table_name}")

            columns = inspector.get_columns(table_name)

            for column in columns:

                column_name = column["name"]

                column_type = str(column["type"])

                schema_lines.append(f"  - {column_name}: " f"{column_type}")

            schema_lines.append("")

        return "\n".join(schema_lines)

    # =====================================================
    # EXECUTE READ-ONLY SQL
    # =====================================================

    def execute_read_only(
        self,
        sql: str,
    ):

        if not sql or not sql.strip():

            raise ValueError("SQL query cannot be empty.")

        normalized = sql.strip().lower()

        forbidden = [
            "insert ",
            "update ",
            "delete ",
            "drop ",
            "alter ",
            "truncate ",
            "create ",
            "grant ",
            "revoke ",
        ]

        # -------------------------------------------------
        # Block dangerous statements
        # -------------------------------------------------

        for keyword in forbidden:

            if normalized.startswith(keyword):

                raise ValueError("Only read-only SELECT " "queries are allowed.")

        # -------------------------------------------------
        # Allow only SELECT
        # -------------------------------------------------

        if not normalized.startswith("select"):

            raise ValueError("Only SELECT queries are allowed.")

        # -------------------------------------------------
        # Execute query
        # -------------------------------------------------

        with self.engine.connect() as connection:

            result = connection.execute(text(sql))

            rows = result.fetchall()

            columns = result.keys()

            return [
                dict(
                    zip(
                        columns,
                        row,
                    )
                )
                for row in rows
            ]
