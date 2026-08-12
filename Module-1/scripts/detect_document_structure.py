import os
import json
import re


# ----------------------------------
# HEADER DETECTION
# ----------------------------------

def is_header(text):
    """
    Detect whether a line looks like a section header.
    """

    text = text.strip()

    if not text:
        return False

    # Example: INTRODUCTION
    if text.isupper() and len(text.split()) <= 10:
        return True

    # Example: 1 Introduction
    if re.match(r"^\d+\s+[A-Z]", text):
        return True

    # Example: 2.1 Dataset
    if re.match(r"^\d+(\.\d+)+\s+[A-Z]", text):
        return True

    # Example: Conclusion
    if text.istitle() and len(text.split()) <= 6:
        return True

    return False


# ----------------------------------
# DOCUMENT STRUCTURE DETECTION
# ----------------------------------

def detect_document_structure():

    # Move from scripts/ -> Module-1/
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    # Input text files
    input_folder = os.path.join(
        base_dir,
        "output",
        "text"
    )

    # Output JSON files
    output_folder = os.path.join(
        base_dir,
        "output",
        "json"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    # Read every TXT file
    for file_name in os.listdir(input_folder):

        if not file_name.endswith(".txt"):
            continue

        input_path = os.path.join(
            input_folder,
            file_name
        )

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as f:

            lines = f.readlines()

        # Main document structure
        document = {

            "document_name": file_name.replace(
                ".txt",
                ".pdf"
            ),

            "pages": []

        }

        current_page = None

        current_section = None

        # Process line by line
        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            # Detect page marker
            if line.startswith("--- Page"):

                page_number = int(
                    re.findall(
                        r"\d+",
                        line
                    )[0]
                )

                current_page = {

                    "page_number": page_number,

                    "sections": [],

                    "unclassified_content": []

                }

                document["pages"].append(
                    current_page
                )

                current_section = None

                continue

            # Detect section header
            if is_header(line):

                current_section = {

                    "header": line,

                    "content": []

                }

                current_page["sections"].append(
                    current_section
                )

                continue

            # Add content under section
            if current_section:

                current_section["content"].append(
                    line
                )

            # Otherwise store separately
            else:

                current_page[
                    "unclassified_content"
                ].append(line)

        # Create output path
        output_path = os.path.join(

            output_folder,

            file_name.replace(
                ".txt",
                ".json"
            )

        )

        # Save JSON
        with open(

            output_path,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                document,

                f,

                indent=4,

                ensure_ascii=False

            )

        print(
            f"Processed: {file_name}"
        )

    print(
        "\nAll documents processed successfully!"
    )


# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    detect_document_structure()