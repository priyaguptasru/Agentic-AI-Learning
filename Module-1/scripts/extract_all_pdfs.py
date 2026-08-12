import fitz
import os

from scripts.logger import log_error


# ----------------------------------
# PDF EXTRACTION
# ----------------------------------

def extract_all_pdfs():

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    pdf_folder = os.path.join(
        base_dir,
        "data",
        "pdfs"
    )

    output_folder = os.path.join(
        base_dir,
        "output",
        "text"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    for file_name in os.listdir(pdf_folder):

        if not file_name.endswith(".pdf"):
            continue

        pdf_path = os.path.join(
            pdf_folder,
            file_name
        )

        try:

            pdf = fitz.open(pdf_path)

            full_text = ""

            for page_no in range(len(pdf)):

                page = pdf[page_no]

                full_text += (
                    f"\n\n--- Page {page_no + 1} ---\n"
                )

                full_text += page.get_text()

            output_file = os.path.join(
                output_folder,
                file_name.replace(
                    ".pdf",
                    ".txt"
                )
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(full_text)

            print(
                f"Saved: {output_file}"
            )

            pdf.close()

        except Exception as e:

            log_error(
                f"PDF Extraction Failed | "
                f"{file_name} | {e}"
            )

            print(
                f"Skipped: {file_name}"
            )

            continue


# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    extract_all_pdfs()