import tkinter as tk
from tkinter import ttk

from app.ui.manual_merge_view import ManualMergeView
from app.ui.batch_merge_view import BatchMergeView
from app.ui.split_pdf_view import SplitPdfView


class MainWindow:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "PDF Scan Merger"
        )

        self.root.geometry(
            "950x760"
        )

        self.root.resizable(
            False,
            False
        )

        self.create_ui()

    # ==================================================
    # Main UI
    # ==================================================

    def create_ui(self):

        title = tk.Label(
            self.root,
            text="PDF Scan Merger",
            font=("Arial", 22, "bold")
        )

        title.pack(
            pady=15
        )

        notebook = ttk.Notebook(
            self.root
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        # ------------------------------------------
        # Manual merge
        # ------------------------------------------

        manual_view = ManualMergeView(
            notebook
        )

        notebook.add(
            manual_view,
            text="Ghép 2 PDF"
        )

        # ------------------------------------------
        # Batch merge
        # ------------------------------------------

        batch_view = BatchMergeView(
            notebook
        )

        notebook.add(
            batch_view,
            text="Ghép hàng loạt"
        )

        split_view = SplitPdfView(
            notebook
        )

        notebook.add(
            split_view,
            text="Tách PDF"
        )