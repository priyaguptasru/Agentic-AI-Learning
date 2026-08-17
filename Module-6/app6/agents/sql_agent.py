from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app6.agents.base_agent import BaseAgent
from app6.llm.llm import LLMService
from app6.prompts.sql_prompt import SQL_PROMPT
from app6.tools.database_tool import DatabaseTool


class SQLAgent(BaseAgent):
    """
    Specialized agent responsible for:

    1. Reading the current database schema.
    2. Understanding the user's natural-language request.
    3. Generating a PostgreSQL SELECT query.
    4. Validating the generated SQL.
    5. Executing only safe read-only SQL.
    6. Returning the result to the workflow state.

    The agent is schema-driven and does not contain
    hard-coded knowledge about specific file types,
    tables, or business entities.
    """

    def __init__(self):

        super().__init__(
            name="SQL Agent",
            description=(
                "Generates and executes "
                "read-only SQL queries "
                "against the application "
                "database using the "
                "available database schema."
            ),
            version="1.0",
        )

        self.llm = LLMService()

        self.database = DatabaseTool()

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        state,
    ):
        """
        Generate and execute a safe SQL query.

        The database schema is retrieved dynamically
        instead of being hard-coded in the agent.
        """

        query = state.get(
            "query",
            "",
        )

        if not query or not query.strip():

            raise ValueError("SQL query request cannot be empty.")

        print("\n" + "=" * 80)
        print("SQL AGENT")
        print("=" * 80)

        print(f"User Query : {query}")

        # =================================================
        # STEP 1
        # READ DATABASE SCHEMA
        # =================================================

        try:

            schema = self.database.get_schema()

        except Exception as e:

            print(f"\nSchema retrieval failed: {e}")

            return {
                "sql_error": ("Failed to read database " f"schema: {e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        if not schema:

            return {
                "sql_error": (
                    "Database schema is empty. " "SQL generation cannot continue."
                ),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        print("\nDatabase Schema:")
        print(schema)

        # =================================================
        # STEP 2
        # CREATE SQL PROMPT
        # =================================================

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SQL_PROMPT,
                ),
            ]
        )

        chain = prompt | self.llm.llm | JsonOutputParser()

        # =================================================
        # STEP 3
        # GENERATE SQL
        # =================================================

        try:

            response = chain.invoke(
                {
                    "schema": schema,
                    "query": query.strip(),
                }
            )

        except Exception as e:

            print(f"\nSQL generation failed: {e}")

            return {
                "sql_error": ("SQL generation failed: " f"{e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        print("\nRaw SQL Agent Response:")
        print(response)

        # =================================================
        # STEP 4
        # EXTRACT SQL
        # =================================================

        if not isinstance(
            response,
            dict,
        ):

            return {
                "sql_error": ("SQL agent returned " "an invalid response format."),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        sql = str(
            response.get(
                "sql",
                "",
            )
        ).strip()

        # -------------------------------------------------
        # Empty SQL
        # -------------------------------------------------

        if not sql:

            return {
                "sql_error": (
                    "The SQL agent could not "
                    "generate a valid SQL query "
                    "from the available schema."
                ),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        print("\nGenerated SQL:")
        print(sql)

        # =================================================
        # STEP 5
        # SQL SAFETY VALIDATION
        # =================================================

        validation_error = self._validate_sql(sql)

        if validation_error:

            print(f"\nSQL validation failed: " f"{validation_error}")

            return {
                "sql_query": sql,
                "sql_error": validation_error,
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        # =================================================
        # STEP 6
        # EXECUTE READ-ONLY SQL
        # =================================================

        try:

            result = self.database.execute_read_only(sql)

        except Exception as e:

            print(f"\nSQL execution failed: {e}")

            return {
                "sql_query": sql,
                "sql_error": ("SQL execution failed: " f"{e}"),
                "steps_executed": (
                    state.get(
                        "steps_executed",
                        [],
                    )
                    + ["execute_sql_failed"]
                ),
            }

        # =================================================
        # STEP 7
        # RETURN RESULT
        # =================================================

        print("\nSQL Result:")
        print(result)

        return {
            "sql_query": sql,
            "sql_result": result,
            "steps_executed": (
                state.get(
                    "steps_executed",
                    [],
                )
                + ["execute_sql"]
            ),
        }

    # =====================================================
    # SQL VALIDATION
    # =====================================================

    def _validate_sql(
        self,
        sql: str,
    ):
        """
        Deterministic SQL safety validation.

        This validation is intentionally performed
        in Python rather than relying only on the LLM.
        """

        normalized = sql.strip().lower()

        # -------------------------------------------------
        # Empty SQL
        # -------------------------------------------------

        if not normalized:

            return "Generated SQL is empty."

        # -------------------------------------------------
        # Only SELECT is allowed
        # -------------------------------------------------

        if not normalized.startswith("select"):

            return "Only SELECT queries " "are allowed."

        # -------------------------------------------------
        # Prevent multiple statements
        # -------------------------------------------------

        sql_without_trailing_semicolon = normalized.rstrip(";").strip()

        if ";" in sql_without_trailing_semicolon:

            return "Multiple SQL statements " "are not allowed."

        # -------------------------------------------------
        # Forbidden operations
        # -------------------------------------------------

        forbidden_keywords = [
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "truncate",
            "create",
            "grant",
            "revoke",
            "merge",
        ]

        for keyword in forbidden_keywords:

            if self._contains_sql_keyword(
                normalized,
                keyword,
            ):

                return "Generated SQL contains " f"forbidden operation: " f"{keyword}"

        return None

    # =====================================================
    # SQL KEYWORD CHECK
    # =====================================================

    @staticmethod
    def _contains_sql_keyword(
        sql: str,
        keyword: str,
    ) -> bool:
        """
        Check whether a SQL keyword appears
        as a separate SQL token.

        This avoids incorrectly rejecting
        column/table names such as:

            updated_at
            created_at
            deleted_flag
        """

        import re

        pattern = rf"\b{re.escape(keyword)}\b"

        return bool(
            re.search(
                pattern,
                sql,
            )
        )
