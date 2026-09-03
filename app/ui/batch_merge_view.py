import os
import threading
import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from app.models.merge_config import MergeConfig

from app.services.batch_service import (
    get_pdf_files,
    process_batch
)


class BatchMergeView(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent
        )

        self.input_dir = None
        self.output_dir = None

        self.cancel_requested = False

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
        # Input
        # ------------------------------------------

        tk.Label(
            frame,
            text="Input:",
            width=10,
            anchor="w"
        ).grid(
            row=0,
            column=0,
            pady=8
        )

        self.input_label = tk.Label(
            frame,
            text="Chưa chọn thư mục",
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
            text="Chọn thư mục",
            width=15,
            command=self.select_input_dir
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
        # File count
        # ------------------------------------------

        self.file_count_label = tk.Label(
            self,
            text="Chưa chọn input folder",
            font=("Arial", 11)
        )

        self.file_count_label.pack(
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
            text="BẮT ĐẦU",
            font=("Arial", 12, "bold"),
            width=18,
            height=2,
            command=self.start_batch
        )

        self.start_button.pack(
            side="left",
            padx=10
        )

        self.cancel_button = tk.Button(
            button_frame,
            text="DỪNG",
            width=12,
            height=2,
            state="disabled",
            command=self.cancel_batch
        )

        self.cancel_button.pack(
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
    # Folder
    # ==================================================

    def select_input_dir(self):

        path = filedialog.askdirectory(
            title="Chọn thư mục chứa PDF scan"
        )

        if not path:
            return

        self.input_dir = path

        self.input_label.config(
            text=path
        )

        self.update_file_count()

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

    def update_file_count(self):

        if not self.input_dir:
            return

        files = get_pdf_files(
            self.input_dir
        )

        count = len(files)

        pairs = count // 2

        extra = (
            " Có 1 file lẻ."
            if count % 2 != 0
            else ""
        )

        self.file_count_label.config(
            text=(
                f"Tìm thấy {count} PDF | "
                f"{pairs} cặp sẽ được ghép."
                f"{extra}"
            )
        )

    # ==================================================
    # Start batch
    # ==================================================

    def start_batch(self):

        if not self.input_dir:

            messagebox.showwarning(
                "Thiếu input",
                "Vui lòng chọn thư mục input."
            )

            return

        if not self.output_dir:

            messagebox.showwarning(
                "Thiếu output",
                "Vui lòng chọn thư mục output."
            )

            return

        files = get_pdf_files(
            self.input_dir
        )

        if len(files) < 2:

            messagebox.showwarning(
                "Không đủ file",
                "Cần ít nhất 2 file PDF."
            )

            return

        self.cancel_requested = False

        self.progress["value"] = 0

        self.progress_label.config(
            text="Đang chuẩn bị..."
        )

        self.log_text.delete(
            "1.0",
            tk.END
        )

        self.start_button.config(
            state="disabled"
        )

        self.cancel_button.config(
            state="normal"
        )

        config = MergeConfig(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            separator_width=0,
            require_single_page=True
        )

        self.worker_thread = threading.Thread(
            target=self.run_batch,
            args=(config,),
            daemon=True
        )

        self.worker_thread.start()

    # ==================================================
    # Worker
    # ==================================================

    def run_batch(
        self,
        config
    ):

        try:

            result = process_batch(
                config=config,
                progress_callback=self.batch_progress,
                should_cancel=self.is_cancel_requested
            )

            self.after(
                0,
                lambda: self.batch_finished(
                    result
                )
            )

        except Exception as error:

            self.after(
                0,
                lambda: self.batch_error(
                    error
                )
            )

    # ==================================================
    # Progress
    # ==================================================

    def batch_progress(
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
    # Cancel
    # ==================================================

    def cancel_batch(self):

        self.cancel_requested = True

        self.progress_label.config(
            text="Đang dừng sau file hiện tại..."
        )

        self.cancel_button.config(
            state="disabled"
        )

    def is_cancel_requested(self):

        return self.cancel_requested

    # ==================================================
    # Finished
    # ==================================================

    def batch_finished(
        self,
        result
    ):

        self.start_button.config(
            state="normal"
        )

        self.cancel_button.config(
            state="disabled"
        )

        success_count = len(
            result.success
        )

        failed_count = len(
            result.failed
        )

        skipped_count = len(
            result.skipped
        )

        if result.cancelled:

            status = "Đã dừng."

        else:

            status = "Hoàn thành."

            self.progress["value"] = 100

        self.progress_label.config(
            text=status
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
            f"Thành công: {success_count}\n"
        )

        self.log_text.insert(
            tk.END,
            f"Lỗi: {failed_count}\n"
        )

        self.log_text.insert(
            tk.END,
            f"File lẻ: {skipped_count}\n"
        )

        # ------------------------------------------
        # Errors
        # ------------------------------------------

        for (
            pdf1,
            pdf2,
            error
        ) in result.failed:

            self.log_text.insert(
                tk.END,
                "\n[LỖI]\n"
            )

            self.log_text.insert(
                tk.END,
                f"{os.path.basename(pdf1)} + "
                f"{os.path.basename(pdf2)}\n"
            )

            self.log_text.insert(
                tk.END,
                f"{error}\n"
            )

        # ------------------------------------------
        # Skipped
        # ------------------------------------------

        for path in result.skipped:

            self.log_text.insert(
                tk.END,
                "\n[FILE LẺ]\n"
            )

            self.log_text.insert(
                tk.END,
                f"{os.path.basename(path)}\n"
            )

        self.log_text.see(
            tk.END
        )

        if result.cancelled:

            messagebox.showinfo(
                "Đã dừng",
                (
                    f"Đã dừng xử lý.\n\n"
                    f"Thành công: {success_count}\n"
                    f"Lỗi: {failed_count}"
                )
            )

        else:

            messagebox.showinfo(
                "Hoàn thành",
                (
                    f"Đã xử lý xong.\n\n"
                    f"Thành công: {success_count}\n"
                    f"Lỗi: {failed_count}\n"
                    f"File lẻ: {skipped_count}"
                )
            )

    # ==================================================
    # Error
    # ==================================================

    def batch_error(
        self,
        error
    ):

        self.start_button.config(
            state="normal"
        )

        self.cancel_button.config(
            state="disabled"
        )

        self.progress_label.config(
            text="Có lỗi."
        )

        messagebox.showerror(
            "Lỗi",
            str(error)
        )