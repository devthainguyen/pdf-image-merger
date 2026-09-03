from pathlib import Path

import pymupdf


def split_pdf(
    input_pdf_path: str,
    output_dir: str,
    progress_callback=None
) -> list[Path]:

    input_path = Path(
        input_pdf_path
    )

    output_path = Path(
        output_dir
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file PDF: {input_path}"
        )

    if input_path.suffix.lower() != ".pdf":
        raise ValueError(
            "File đầu vào phải là PDF."
        )

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    source = pymupdf.open(
        input_path
    )

    try:

        total_pages = len(source)

        if total_pages == 0:
            raise ValueError(
                "PDF không có trang."
            )

        digits = max(
            4,
            len(str(total_pages))
        )

        output_files = []

        for page_index in range(total_pages):

            page_number = page_index + 1

            filename = (
                f"{page_number:0{digits}d}.pdf"
            )

            output_file = (
                output_path / filename
            )

            new_pdf = pymupdf.open()

            try:

                new_pdf.insert_pdf(
                    source,
                    from_page=page_index,
                    to_page=page_index
                )

                new_pdf.save(
                    output_file
                )

            finally:

                new_pdf.close()

            output_files.append(
                output_file
            )

            if progress_callback:

                progress_callback(
                    page_number,
                    total_pages,
                    f"Đang tách trang {page_number}/{total_pages}"
                )

        return output_files

    finally:

        source.close()