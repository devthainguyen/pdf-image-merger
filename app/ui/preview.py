import io
import tkinter as tk

import pymupdf

from PIL import Image, ImageTk


class PDFPreview:

    def __init__(
        self,
        parent,
        title: str
    ):

        self.photo = None

        self.frame = tk.Frame(
            parent
        )

        self.frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        tk.Label(
            self.frame,
            text=title,
            font=("Arial", 11, "bold")
        ).pack()

        self.label = tk.Label(
            self.frame,
            text="Chưa có ảnh",
            bg="#eeeeee"
        )

        self.label.pack(
            fill="both",
            expand=True,
            pady=5
        )

    def load_pdf(
        self,
        pdf_path: str,
        max_width: int = 400,
        max_height: int = 430
    ):

        document = pymupdf.open(
            pdf_path
        )

        try:

            if len(document) == 0:
                return

            page = document[0]

            # Preview chỉ cần resolution thấp.
            matrix = pymupdf.Matrix(
                1.0,
                1.0
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

        finally:

            document.close()

        image.thumbnail(
            (
                max_width,
                max_height
            ),
            Image.Resampling.LANCZOS
        )

        self.photo = ImageTk.PhotoImage(
            image
        )

        self.label.config(
            image=self.photo,
            text=""
        )

    def clear(self):

        self.photo = None

        self.label.config(
            image="",
            text="Chưa có ảnh"
        )