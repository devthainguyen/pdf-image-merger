import os
import threading
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import fitz

from app.services.pdf_splitter import (
    split_pdf,
)


class SplitPdfView(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent
        )

        self.input_pdf_path = None
        self.output_dir = None

        self.worker_thread = None

        self.create_ui()

    # ==================================================
    # UI
    # ==================================================

    def create_ui(self):

        frame = tk.Frame(
            self
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=25
        )

        # ------------------------------------------
        # Input PDF
        # ------------------------------------------

        tk.Label(
            frame,
            text="PDF:",
            width=10,
            anchor="w"
        ).grid(
            row=0,
            column=0,
            pady=8
        )

        self.input_label = tk.Label(
            frame,
            text="Chưa chọn file",
            relief="sunken",
            anchor="w"
        )

        self.input_label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5
        )

        tk.Button(
            frame,
            text="Chọn PDF",
            width=15,
            command=self.select_input_pdf
        ).grid(
            row=0,
            column=2
        )

        # ------------------------------------------
        # Output
        # ------------------------------------------

        tk.Label(
            frame,
            text="Output:",
            width=10,
            anchor="w"
        ).grid(
            row=1,
            column=0,
            pady=8
        )

        self.output_label = tk.Label(
            frame,
            text="Chưa chọn thư mục",
            relief="sunken",
            anchor="w"
        )

        self.output_label.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5
        )

        tk.Button(
            frame,
            text="Chọn thư mục",
            width=15,
            command=self.select_output_dir
        ).grid(
            row=1,
            column=2
        )

        frame.columnconfigure(
            1,
            weight=1
        )

        # ------------------------------------------
        # Page count
        # ------------------------------------------

        self.page_count_label = tk.Label(
            self,
            text="Chưa chọn PDF",
            font=("Arial", 11)
        )

        self.page_count_label.pack(
            pady=10
        )

        # ------------------------------------------
        # Progress
        # ------------------------------------------

        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            length=700,
            mode="determinate"
        )

        self.progress.pack(
            pady=15
        )

        self.progress_label = tk.Label(
            self,
            text="Chưa bắt đầu"
        )

        self.progress_label.pack()

        # ------------------------------------------
        # Buttons
        # ------------------------------------------

        button_frame = tk.Frame(
            self
        )

        button_frame.pack(
            pady=20
        )

        self.start_button = tk.Button(
            button_frame,
            text="TÁCH PDF",
            font=("Arial", 12, "bold"),
            width=18,
            height=2,
            command=self.start_split
        )

        self.start_button.pack(
            side="left",
            padx=10
        )

        self.clear_button = tk.Button(
            button_frame,
            text="Xóa",
            width=10,
            height=2,
            command=self.clear
        )

        self.clear_button.pack(
            side="left",
            padx=10
        )

        # ------------------------------------------
        # Log
        # ------------------------------------------

        tk.Label(
            self,
            text="Log",
            font=("Arial", 11, "bold")
        ).pack()

        self.log_text = tk.Text(
            self,
            height=12,
            width=100
        )

        self.log_text.pack(
            padx=25,
            pady=5
        )

    # ==================================================
    # Select input PDF
    # ==================================================

    def select_input_pdf(self):

        path = filedialog.askopenfilename(
            title="Chọn PDF cần tách",
            filetypes=[
                (
                    "PDF files",
                    "*.pdf"
                )
            ]
        )

        if not path:
            return

        try:

            document = fitz.open(
                path
            )

            try:

                page_count = len(
                    document
                )

            finally:

                document.close()

            if page_count == 0:

                raise ValueError(
                    "PDF không có trang."
                )

            self.input_pdf_path = path

            self.input_label.config(
                text=os.path.basename(
                    path
                )
            )

            self.page_count_label.config(
                text=(
                    f"PDF có "
                    f"{page_count} trang."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Lỗi",
                str(error)
            )

    # ==================================================
    # Select output directory
    # ==================================================

    def select_output_dir(self):

        path = filedialog.askdirectory(
            title="Chọn thư mục output"
        )

        if not path:
            return

        self.output_dir = path

        self.output_label.config(
            text=path
        )

    # ==================================================
    # Start
    # ==================================================

    def start_split(self):

        if not self.input_pdf_path:

            messagebox.showwarning(
                "Thiếu file",
                "Vui lòng chọn PDF cần tách."
            )

            return

        if not self.output_dir:

            messagebox.showwarning(
                "Thiếu output",
                "Vui lòng chọn thư mục output."
            )

            return

        self.start_button.config(
            state="disabled"
        )

        self.clear_button.config(
            state="disabled"
        )

        self.progress["value"] = 0

        self.progress_label.config(
            text="Đang chuẩn bị..."
        )

        self.log_text.delete(
            "1.0",
            tk.END
        )

        self.worker_thread = threading.Thread(
            target=self.run_split,
            daemon=True
        )

        self.worker_thread.start()

    # ==================================================
    # Worker
    # ==================================================

    def run_split(self):

        try:

            output_files = split_pdf(
                input_pdf_path=self.input_pdf_path,
                output_dir=self.output_dir,
                progress_callback=(
                    self.split_progress
                ),
            )

            self.after(
                0,
                lambda: self.split_finished(
                    len(output_files)
                )
            )

        except Exception as error:

            self.after(
                0,
                lambda: self.split_error(
                    error
                )
            )

    # ==================================================
    # Progress callback
    # ==================================================

    def split_progress(
        self,
        current,
        total,
        message
    ):

        self.after(
            0,
            lambda: self.update_progress(
                current,
                total,
                message
            )
        )

    def update_progress(
        self,
        current,
        total,
        message
    ):

        if total > 0:

            value = (
                current
                / total
                * 100
            )

            self.progress["value"] = value

        self.progress_label.config(
            text=message
        )

        self.log_text.insert(
            tk.END,
            message + "\n"
        )

        self.log_text.see(
            tk.END
        )

    # ==================================================
    # Finished
    # ==================================================

    def split_finished(
        self,
        count
    ):

        self.start_button.config(
            state="normal"
        )

        self.clear_button.config(
            state="normal"
        )

        self.progress["value"] = 100

        self.progress_label.config(
            text="Hoàn thành."
        )

        self.log_text.insert(
            tk.END,
            "\n"
            "================================\n"
        )

        self.log_text.insert(
            tk.END,
            "KẾT QUẢ\n"
        )

        self.log_text.insert(
            tk.END,
            "================================\n"
        )

        self.log_text.insert(
            tk.END,
            f"Đã tạo {count} file PDF.\n"
        )

        self.log_text.insert(
            tk.END,
            f"Output: {self.output_dir}\n"
        )

        self.log_text.see(
            tk.END
        )

        messagebox.showinfo(
            "Hoàn thành",
            (
                f"Đã tách PDF thành công!\n\n"
                f"Số file: {count}\n\n"
                f"Output:\n"
                f"{self.output_dir}"
            )
        )

    # ==================================================
    # Error
    # ==================================================

    def split_error(
        self,
        error
    ):

        self.start_button.config(
            state="normal"
        )

        self.clear_button.config(
            state="normal"
        )

        self.progress_label.config(
            text="Có lỗi."
        )

        messagebox.showerror(
            "Lỗi",
            str(error)
        )

    # ==================================================
    # Clear
    # ==================================================

    def clear(self):

        self.input_pdf_path = None
        self.output_dir = None

        self.input_label.config(
            text="Chưa chọn file"
        )

        self.output_label.config(
            text="Chưa chọn thư mục"
        )

        self.page_count_label.config(
            text="Chưa chọn PDF"
        )

        self.progress["value"] = 0

        self.progress_label.config(
            text="Chưa bắt đầu"
        )

        self.log_text.delete(
            "1.0",
            tk.END
        )