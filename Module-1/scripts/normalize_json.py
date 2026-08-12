import os
import json

from scripts.logger import log_error


# --------------------------------------------------
# NORMALIZE JSON
# --------------------------------------------------

def normalize_json():

    # --------------------------------------------------
    # FIND PROJECT ROOT
    # --------------------------------------------------

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    # --------------------------------------------------
    # INPUT JSON FOLDER
    # --------------------------------------------------

    input_folder = os.path.join(
        base_dir,
        "output",
        "json"
    )

    # --------------------------------------------------
    # OUTPUT NORMALIZED JSON FOLDER
    # --------------------------------------------------

    output_folder = os.path.join(
        base_dir,
        "output",
        "normalized_json"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    # --------------------------------------------------
    # PROCESS EACH JSON FILE
    # --------------------------------------------------

    for file_name in os.listdir(input_folder):

        if not file_name.endswith(".json"):
            continue

        print(
            f"\nProcessing: {file_name}"
        )

        file_path = os.path.join(
            input_folder,
            file_name
        )

        # --------------------------------------------------
        # READ JSON
        # --------------------------------------------------

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except Exception as e:

            log_error(
                f"JSON Read Failed | "
                f"{file_name} | {e}"
            )

            print(
                f"Skipped: {file_name}"
            )

            continue

        # --------------------------------------------------
        # NORMALIZATION
        # --------------------------------------------------

        try:

            normalized_data = {
                "document_id": 1,
                "document_name": data.get(
                    "document_name",
                    ""
                ),
                "pages": []
            }

            page_counter = 1
            section_counter = 1
            paragraph_counter = 1

            # --------------------------------------------------
            # PAGE LOOP
            # --------------------------------------------------

            for page in data.get(
                "pages",
                []
            ):

                normalized_page = {
                    "page_id": page_counter,
                    "page_number": page.get(
                        "page_number",
                        0
                    ),
                    "sections": [],
                    "unclassified_content": []
                }

                # --------------------------------------------------
                # SECTION LOOP
                # --------------------------------------------------

                for section in page.get(
                    "sections",
                    []
                ):

                    normalized_section = {
                        "section_id": section_counter,
                        "header": section.get(
                            "header",
                            ""
                        ),
                        "paragraphs": []
                    }

                    # --------------------------------------------------
                    # CONTENT -> PARAGRAPHS
                    # --------------------------------------------------

                    for line in section.get(
                        "content",
                        []
                    ):

                        normalized_section[
                            "paragraphs"
                        ].append(
                            {
                                "paragraph_id": paragraph_counter,
                                "text": line
                            }
                        )

                        paragraph_counter += 1

                    normalized_page[
                        "sections"
                    ].append(
                        normalized_section
                    )

                    section_counter += 1

                # --------------------------------------------------
                # UNCLASSIFIED CONTENT
                # --------------------------------------------------

                for line in page.get(
                    "unclassified_content",
                    []
                ):

                    normalized_page[
                        "unclassified_content"
                    ].append(
                        {
                            "paragraph_id": paragraph_counter,
                            "text": line
                        }
                    )

                    paragraph_counter += 1

                normalized_data[
                    "pages"
                ].append(
                    normalized_page
                )

                page_counter += 1

        except Exception as e:

            log_error(
                f"JSON Normalization Failed | "
                f"{file_name} | {e}"
            )

            print(
                f"Skipped: {file_name}"
            )

            continue

        # --------------------------------------------------
        # SAVE NORMALIZED FILE
        # --------------------------------------------------

        output_file = os.path.join(
            output_folder,
            file_name
        )

        try:

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    normalized_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            log_error(
                f"JSON Save Failed | "
                f"{file_name} | {e}"
            )

            print(
                f"Skipped Saving: {file_name}"
            )

            continue

        print(
            f"Saved: {output_file}"
        )

    print(
        "\nNormalization Completed Successfully!"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    normalize_json()