import os
import re
from typing import Callable, Optional

from app.models.merge_config import MergeConfig
from app.services.pdf_service import merge_pdf_pages


class BatchResult:

    def __init__(self):
        self.success = []
        self.failed = []
        self.skipped = []
        self.cancelled = False


def natural_sort_key(path: str):
    """
    Sort:

        1.pdf
        2.pdf
        10.pdf

    thay vì:

        1.pdf
        10.pdf
        2.pdf
    """

    filename = os.path.basename(path)

    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(
            r"(\d+)",
            filename
        )
    ]


def get_pdf_files(input_dir: str):

    files = []

    for filename in os.listdir(input_dir):

        if not filename.lower().endswith(".pdf"):
            continue

        path = os.path.join(
            input_dir,
            filename
        )

        if os.path.isfile(path):
            files.append(path)

    files.sort(
        key=natural_sort_key
    )

    return files


def build_output_name(
    pdf1: str,
    pdf2: str
):
    name1 = os.path.splitext(
        os.path.basename(pdf1)
    )[0]

    name2 = os.path.splitext(
        os.path.basename(pdf2)
    )[0]

    return f"{name1}_{name2}.pdf"


def process_batch(
    config: MergeConfig,
    progress_callback: Optional[
        Callable[[int, int, str], None]
    ] = None,
    should_cancel: Optional[
        Callable[[], bool]
    ] = None
):

    result = BatchResult()

    pdf_files = get_pdf_files(
        config.input_dir
    )

    total_files = len(pdf_files)

    if total_files < 2:
        raise ValueError(
            "Thư mục phải có ít nhất 2 file PDF."
        )

    os.makedirs(
        config.output_dir,
        exist_ok=True
    )

    pair_count = total_files // 2

    for pair_index in range(pair_count):

        # ----------------------------------------------
        # Cancel
        # ----------------------------------------------

        if should_cancel and should_cancel():

            result.cancelled = True

            break

        index1 = pair_index * 2
        index2 = index1 + 1

        pdf1 = pdf_files[index1]
        pdf2 = pdf_files[index2]

        filename1 = os.path.basename(
            pdf1
        )

        filename2 = os.path.basename(
            pdf2
        )

        message = (
            f"Đang xử lý "
            f"{pair_index + 1}/{pair_count}: "
            f"{filename1} + {filename2}"
        )

        if progress_callback:
            progress_callback(
                pair_index,
                pair_count,
                message
            )

        try:

            output_filename = build_output_name(
                pdf1,
                pdf2
            )

            output_path = os.path.join(
                config.output_dir,
                output_filename
            )

            merge_pdf_pages(
                pdf1_path=pdf1,
                pdf2_path=pdf2,
                output_path=output_path,
                separator_width=config.separator_width,
                require_single_page=config.require_single_page
            )

            result.success.append(
                output_path
            )

        except Exception as error:

            result.failed.append(
                (
                    pdf1,
                    pdf2,
                    str(error)
                )
            )

    # ----------------------------------------------
    # File lẻ
    # ----------------------------------------------

    if total_files % 2 != 0:

        last_file = pdf_files[-1]

        result.skipped.append(
            last_file
        )

    if progress_callback:

        if result.cancelled:

            progress_callback(
                min(pair_count, pair_count),
                pair_count,
                "Đã dừng."
            )

        else:

            progress_callback(
                pair_count,
                pair_count,
                "Hoàn thành."
            )

    return result