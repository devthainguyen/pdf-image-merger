import os
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox

from app.services.pdf_service import (
    merge_pdf_pages
)

from app.ui.preview import PDFPreview


class ManualMergeView(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent
        )

        self.pdf1_path = None
        self.pdf2_path = None

        self.create_ui()

    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):

        self.create_manual_file_row(
            1
        )

        self.create_manual_file_row(
            2
        )

        # ------------------------------------------
        # Preview title
        # ------------------------------------------

        tk.Label(
            self,
            text="Preview",
            font=("Arial", 14, "bold")
        ).pack(
            pady=(15, 5)
        )

        # ------------------------------------------
        # Preview
        # ------------------------------------------

        preview_frame = tk.Frame(
            self,
            bd=1,
            relief="solid"
        )

        preview_frame.pack(
            padx=20,
            pady=5,
            fill="both",
            expand=True
        )

        self.preview1 = PDFPreview(
            preview_frame,
            "PDF 1"
        )

        self.preview2 = PDFPreview(
            preview_frame,
            "PDF 2"
        )

        # ------------------------------------------
        # Buttons
        # ------------------------------------------

        button_frame = tk.Frame(
            self
        )

        button_frame.pack(
            pady=15
        )

        tk.Button(
            button_frame,
            text="GHÉP PDF",
            font=("Arial", 12, "bold"),
            width=18,
            height=2,
            command=self.merge_pdf
        ).pack(
            side="left",
            padx=10
        )

        tk.Button(
            button_frame,
            text="Xóa",
            width=10,
            height=2,
            command=self.clear
        ).pack(
            side="left",
            padx=10
        )

    # ==================================================
    # File row
    # ==================================================

    def create_manual_file_row(
        self,
        number
    ):

        frame = tk.Frame(
            self
        )

        frame.pack(
            fill="x",
            padx=25,
            pady=5
        )

        tk.Label(
            frame,
            text=f"PDF {number}:",
            width=8,
            anchor="w"
        ).pack(
            side="left"
        )

        label = tk.Label(
            frame,
            text="Chưa chọn file",
            anchor="w",
            relief="sunken"
        )

        label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        if number == 1:

            command = self.select_pdf1

        else:

            command = self.select_pdf2

        tk.Button(
            frame,
            text="Chọn file",
            width=12,
            command=command
        ).pack(
            side="right"
        )

        if number == 1:

            self.pdf1_label = label

        else:

            self.pdf2_label = label

    # ==================================================
    # Select PDF
    # ==================================================

    def select_pdf1(self):

        path = self.select_pdf()

        if not path:
            return

        try:

            self.validate_pdf(
                path
            )

            self.pdf1_path = path

            self.pdf1_label.config(
                text=os.path.basename(
                    path
                )
            )

            self.preview1.load_pdf(
                path
            )

        except Exception as error:

            messagebox.showerror(
                "Lỗi",
                str(error)
            )

    def select_pdf2(self):

        path = self.select_pdf()

        if not path:
            return

        try:

            self.validate_pdf(
                path
            )

            self.pdf2_path = path

            self.pdf2_label.config(
                text=os.path.basename(
                    path
                )
            )

            self.preview2.load_pdf(
                path
            )

        except Exception as error:

            messagebox.showerror(
                "Lỗi",
                str(error)
            )

    @staticmethod
    def select_pdf():

        return filedialog.askopenfilename(
            title="Chọn PDF scan",
            filetypes=[
                (
                    "PDF files",
                    "*.pdf"
                )
            ]
        )

    # ==================================================
    # Validate
    # ==================================================

    @staticmethod
    def validate_pdf(
        path: str
    ):

        import fitz

        document = fitz.open(
            path
        )

        try:

            if len(document) == 0:

                raise ValueError(
                    "PDF không có trang."
                )

            if len(document) != 1:

                raise ValueError(
                    "PDF phải chỉ có 1 trang."
                )

        finally:

            document.close()

    # ==================================================
    # Merge
    # ==================================================

    def merge_pdf(self):

        if not self.pdf1_path:

            messagebox.showwarning(
                "Thiếu file",
                "Vui lòng chọn PDF 1."
            )

            return

        if not self.pdf2_path:

            messagebox.showwarning(
                "Thiếu file",
                "Vui lòng chọn PDF 2."
            )

            return

        name1 = os.path.splitext(
            os.path.basename(
                self.pdf1_path
            )
        )[0]

        name2 = os.path.splitext(
            os.path.basename(
                self.pdf2_path
            )
        )[0]

        output_path = (
            filedialog.asksaveasfilename(
                title="Lưu PDF",
                defaultextension=".pdf",
                initialfile=(
                    f"{name1}_{name2}.pdf"
                ),
                filetypes=[
                    (
                        "PDF files",
                        "*.pdf"
                    )
                ]
            )
        )

        if not output_path:
            return

        try:

            merge_pdf_pages(
                pdf1_path=self.pdf1_path,
                pdf2_path=self.pdf2_path,
                output_path=output_path,
                separator_width=0,
                require_single_page=True
            )

            messagebox.showinfo(
                "Thành công",
                "Đã ghép PDF thành công!"
            )

        except Exception as error:

            messagebox.showerror(
                "Lỗi",
                str(error)
            )

    # ==================================================
    # Clear
    # ==================================================

    def clear(self):

        self.pdf1_path = None
        self.pdf2_path = None

        self.pdf1_label.config(
            text="Chưa chọn file"
        )

        self.pdf2_label.config(
            text="Chưa chọn file"
        )

        self.preview1.clear()
        self.preview2.clear()