import fitz


def get_pdf_page_info(pdf_path: str):
    """
    Đọc thông tin trang đầu tiên của PDF.

    Returns:
        {
            "width": float,
            "height": float,
            "page_count": int
        }
    """

    document = fitz.open(pdf_path)

    try:
        if len(document) == 0:
            raise ValueError(
                "PDF không có trang nào."
            )

        page = document[0]

        rect = page.rect

        return {
            "width": rect.width,
            "height": rect.height,
            "page_count": len(document)
        }

    finally:
        document.close()


def merge_pdf_pages(
    pdf1_path: str,
    pdf2_path: str,
    output_path: str,
    separator_width: float = 0.0,
    require_single_page: bool = True
):
    """
    Ghép trang đầu tiên của 2 PDF thành một trang PDF mới.

    PDF 1 nằm bên trái.
    PDF 2 nằm bên phải.

    Quan trọng:
    Không render PDF thành ảnh rồi encode lại.
    PyMuPDF sẽ import trực tiếp nội dung trang PDF.
    """

    source1 = fitz.open(pdf1_path)
    source2 = fitz.open(pdf2_path)

    output = fitz.open()

    try:
        if len(source1) == 0:
            raise ValueError(
                f"{pdf1_path} không có trang."
            )

        if len(source2) == 0:
            raise ValueError(
                f"{pdf2_path} không có trang."
            )

        if require_single_page:

            if len(source1) != 1:
                raise ValueError(
                    f"{pdf1_path} có {len(source1)} trang. "
                    f"Tool yêu cầu PDF chỉ có 1 trang."
                )

            if len(source2) != 1:
                raise ValueError(
                    f"{pdf2_path} có {len(source2)} trang. "
                    f"Tool yêu cầu PDF chỉ có 1 trang."
                )

        page1 = source1[0]
        page2 = source2[0]

        rect1 = page1.rect
        rect2 = page2.rect

        # --------------------------------------------------
        # Tính kích thước sau khi đưa 2 trang về cùng chiều cao
        # --------------------------------------------------

        target_height = max(
            rect1.height,
            rect2.height
        )

        scale1 = (
            target_height
            / rect1.height
        )

        scale2 = (
            target_height
            / rect2.height
        )

        width1 = rect1.width * scale1
        width2 = rect2.width * scale2

        output_width = (
            width1
            + separator_width
            + width2
        )

        output_height = target_height

        # --------------------------------------------------
        # Tạo trang output
        # --------------------------------------------------

        output_page = output.new_page(
            width=output_width,
            height=output_height
        )

        # --------------------------------------------------
        # PDF 1 - bên trái
        # --------------------------------------------------

        output_rect1 = fitz.Rect(
            0,
            0,
            width1,
            output_height
        )

        output_page.show_pdf_page(
            output_rect1,
            source1,
            0,
            keep_proportion=True
        )

        # --------------------------------------------------
        # PDF 2 - bên phải
        # --------------------------------------------------

        x2 = width1 + separator_width

        output_rect2 = fitz.Rect(
            x2,
            0,
            x2 + width2,
            output_height
        )

        output_page.show_pdf_page(
            output_rect2,
            source2,
            0,
            keep_proportion=True
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        output.save(
            output_path,
            garbage=4,
            deflate=True
        )

    finally:
        source1.close()
        source2.close()
        output.close()