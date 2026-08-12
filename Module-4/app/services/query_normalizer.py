"""
Query Normalizer Service

This service cleans the user query before
performing semantic or keyword search.

Important:
Document filenames and their extensions are preserved.
Example:

Adobe_Sample_PDF.pdf
        ↓
adobe_sample_pdf.pdf
"""

import re


class QueryNormalizer:

    def __init__(self):

        print("\nQuery Normalizer Ready!")

    # =========================================================
    # NORMALIZE QUERY
    # =========================================================

    def normalize(
        self,
        query: str,
    ):

        if not query:

            return ""

        # -----------------------------------------------------
        # Convert to lowercase
        # -----------------------------------------------------

        query = query.lower()

        # -----------------------------------------------------
        # Remove leading/trailing spaces
        # -----------------------------------------------------

        query = query.strip()

        # -----------------------------------------------------
        # Preserve common document extensions
        #
        # Example:
        #
        # adobe_sample_pdf.pdf
        #
        # The dot must NOT be removed.
        # -----------------------------------------------------

        document_extensions = (
            ".pdf",
            ".csv",
            ".json",
            ".txt",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        )

        extension_placeholders = {}

        for index, extension in enumerate(document_extensions):

            placeholder = f"__FILE_EXTENSION_{index}__"

            if extension in query:

                query = query.replace(
                    extension,
                    placeholder,
                )

                extension_placeholders[placeholder] = extension

        # -----------------------------------------------------
        # Replace hyphen with space
        # -----------------------------------------------------

        query = query.replace(
            "-",
            " ",
        )

        # -----------------------------------------------------
        # Remove remaining punctuation
        #
        # Underscores are preserved because \w includes "_".
        # -----------------------------------------------------

        query = re.sub(
            r"[^\w\s]",
            "",
            query,
        )

        # -----------------------------------------------------
        # Restore document extensions
        # -----------------------------------------------------

        for (
            placeholder,
            extension,
        ) in extension_placeholders.items():

            query = query.replace(
                placeholder,
                extension,
            )

        # -----------------------------------------------------
        # Replace multiple spaces with one
        # -----------------------------------------------------

        query = re.sub(
            r"\s+",
            " ",
            query,
        )

        # -----------------------------------------------------
        # Final trim
        # -----------------------------------------------------

        query = query.strip()

        return query


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    normalizer = QueryNormalizer()

    print("\n" + "=" * 80)
    print("QUERY NORMALIZER")
    print("=" * 80)
    print("Type your query below.")
    print("Type 'exit' to quit.")
    print("=" * 80)

    while True:

        query = input("\nEnter your query : ").strip()

        if query.lower() in [
            "exit",
            "quit",
            "q",
        ]:

            print("\nExiting Query Normalizer...")

            break

        if not query:

            print("Please enter a valid query.")

            continue

        normalized_query = normalizer.normalize(query)

        print("\nOriginal Query :")
        print(query)

        print("\nNormalized Query :")
        print(normalized_query)

        print("\n" + "=" * 80)
