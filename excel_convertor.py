import os
from collections import deque
from datetime import datetime

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name


class ExcelConverter:
    column_widths = {}
    header_style = {
        "bold": False,
        "font_name": "Arial",
        "font_size": 11,
        "align": "center",
        "valign": "vcenter",
        'bg_color': '#C6EFCE'
    }

    def __init__(self, excel_rows, buffer=None, cell_styles=None, cell_comments=None, is_filter=None):
        self.excel_rows = excel_rows
        self.cell_styles = cell_styles
        self.cell_comments = cell_comments
        self.is_filter = is_filter

        if buffer is None:
            raise ValueError("Buffer (filename or file-like object) must be provided.")
        if isinstance(buffer, str):
            default_dirname = "./output"

            timestamp = int(datetime.now().timestamp())
            buffer = f"{buffer}_{timestamp}.xlsx"
            if not buffer.startswith("./"):
                buffer = f"{default_dirname}/{buffer}"
            os.makedirs(os.path.dirname(buffer), exist_ok=True)
        self.buffer = buffer

    def save(self):
        workbook = xlsxwriter.Workbook(self.buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        header_texts = self.excel_rows[0].split(",")
        cell_styles = {header_texts.index(x): y for x, y in (self.cell_styles or {}).items()}

        max_widths = {}
        for row_index, row in enumerate(self.excel_rows):
            for col_index, cell_value in enumerate(row.split(",")):
                cell_length = len(str(cell_value))
                if col_index not in max_widths or cell_length > max_widths[col_index]:
                    max_widths[col_index] = cell_length

        for col_index, width in max_widths.items():
            worksheet.set_column(col_index, col_index, self.column_widths.get(col_index, width + 2))

        header_format = workbook.add_format(self.header_style)
        cell_formats = {col_index: workbook.add_format(style) for col_index, style in cell_styles.items()}
        default_integer_cell_format = workbook.add_format({'font_size': 10,
                                                           'num_format': '_* #,##0_-;_-* -#,##0_-;_-* "-"_-;_-@_-'})
        default_cell_format = workbook.add_format({'font_size': 10})

        total_rows = 0
        total_cols = 0
        for row_index, row in enumerate(self.excel_rows):
            row = row.split(",")
            total_rows = row_index + 1
            total_cols = len(row)
            for col_index, cell_value in enumerate(row):
                if row_index == 0:
                    worksheet.write(row_index, col_index, cell_value, header_format)
                    if self.cell_comments and self.cell_comments.get(cell_value):
                        worksheet.write_comment(row_index, col_index, self.cell_comments[cell_value], {
                            "width": 200,
                            "height": max(20 * len(self.cell_comments[cell_value].split("\n")), 100),
                        })
                else:
                    try:
                        cell_value = int(cell_value) if "." not in cell_value else float(cell_value)
                        cell_format = cell_formats.get(col_index) or default_integer_cell_format
                    except ValueError:
                        cell_format = cell_formats.get(col_index) or default_cell_format
                    worksheet.write(row_index, col_index, cell_value, cell_format)
        if self.is_filter:
            filter_range = f"A1:{xl_col_to_name(total_cols - 1)}{total_rows}"
            worksheet.autofilter(filter_range)

        for col_index, width in max_widths.items():
            adjusted_width = self.column_widths.get(col_index, width + 2) + (width * 0.5)
            worksheet.set_column(col_index, col_index, adjusted_width)

        worksheet.freeze_panes(1, 0)
        workbook.close()


def get_excel_row(header, body, blank="-"):
    body = deque(body)
    body.insert(0, header)

    for x in body:
        row = [str(x[value] if x.get(value) is not None else blank).replace(",", " ")
               for value in header.keys()]
        yield ",".join(row)
