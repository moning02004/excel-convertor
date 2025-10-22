import os
from collections import deque, defaultdict
from datetime import datetime

import unicodedata
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name


def get_display_width(text):
    width = []
    for ch in str(text):
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            width.append(1.3)
        else:
            width.append(1)
    return sum(width)


class ExcelConvertor:
    __header_style = {
        "bold": False,
        "font_name": "Arial",
        "font_size": 11,
        "align": "center",
        "valign": "vcenter",
        'bg_color': '#C6EFCE'
    }

    def __init__(self, save_to, is_header_filter=True, options=None):
        self.__header = dict()
        self.__body = list()
        self.__cell_styles = dict()
        self.__cell_comments = dict()

        self.is_header_filter = is_header_filter

        if save_to is None:
            raise ValueError("save_to 는 필수입니다.")
        if isinstance(save_to, str):
            default_dirname = "./output"

            timestamp = int(datetime.now().timestamp())
            save_to = f"{save_to}_{timestamp}.xlsx"
            if not save_to.startswith("./"):
                save_to = f"{default_dirname}/{save_to}"
            os.makedirs(os.path.dirname(save_to), exist_ok=True)

        self.save_to = save_to
        self.workbook = None
        self.worksheet = None
        self._opened = False

        self.options = options or {
            "in_memory": True
        }

    @property
    def header_style(self):
        return self.__header_style

    @header_style.setter
    def header_style(self, value):
        self.__header_style = value

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, value):
        if not isinstance(value, dict):
            raise ValueError("header 는 dict 형태여야 합니다.")
        self.__header = value

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value):
        if not isinstance(value, list):
            raise ValueError("body 는 list 형태여야 합니다.")
        self.__body = list(self.get_excel_row(body=value))

    @property
    def cell_styles(self):
        return self.__cell_styles

    @cell_styles.setter
    def cell_styles(self, value):
        if not isinstance(value, dict):
            raise ValueError("cell_styles 는 dict 형태여야 합니다.")
        self.__cell_styles = self.get_cell_styles(value)

    @property
    def cell_comments(self):
        return self.__cell_comments

    @cell_comments.setter
    def cell_comments(self, value):
        if not isinstance(value, dict):
            raise ValueError("cell_comments 는 dict 형태여야 합니다.")
        self.__cell_comments = self.get_cell_comments(value)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def write_sheet(self, sheet_name=None):
        self.worksheet = self.workbook.add_worksheet(name=sheet_name)

        max_widths = {}
        for row_index, row in enumerate(self.body):
            for col_index, cell_value in enumerate(row.split(",")):
                cell_length = max(get_display_width(cell_value), 6)
                if col_index not in max_widths or cell_length > max_widths[col_index]:
                    max_widths[col_index] = cell_length
        for col_index, width in max_widths.items():
            self.worksheet.set_column(col_index, col_index, width)

        header_format = self.workbook.add_format(self.header_style)
        default_integer_cell_format = self.workbook.add_format({'font_size': 10,
                                                                'num_format': '_* #,##0_-;_-* -#,##0_-;_-* "-"_-;_-@_-'})
        default_cell_format = self.workbook.add_format({'font_size': 10})

        total_rows = 0
        total_cols = 0
        for row_index, row in enumerate(self.body):
            row = row.split(",")
            total_rows = row_index + 1
            total_cols = len(row)
            for col_index, cell_value in enumerate(row):
                if row_index == 0:
                    self.worksheet.write(row_index, col_index, cell_value, header_format)
                    if self.cell_comments.get(col_index):
                        self.worksheet.write_comment(row_index, col_index, self.cell_comments[col_index], {
                            "width": 200,
                            "height": max(20 * len(self.cell_comments[col_index].split("\n")), 100),
                        })
                else:
                    try:
                        cell_value = int(cell_value) if "." not in cell_value else float(cell_value)
                        cell_format = self.cell_styles.get(col_index) or default_integer_cell_format
                    except ValueError:
                        cell_format = self.cell_styles.get(col_index) or default_cell_format
                    self.worksheet.write(row_index, col_index, cell_value, cell_format)

        if self.is_header_filter:
            filter_range = f"A1:{xl_col_to_name(total_cols - 1)}{total_rows}"
            self.worksheet.autofilter(filter_range)

        for col_index, width in max_widths.items():
            adjusted_width = width * 1.3
            self.worksheet.set_column(col_index, col_index, adjusted_width)

        self.worksheet.freeze_panes(1, 0)

    def get_excel_row(self, body, blank="-"):
        body = deque(body)
        body.insert(0, self.header)

        for x in body:
            row = [str(x[value] if x.get(value) is not None else blank).replace(",", " ")
                   for value in self.header.keys()]
            yield ",".join(row)

    def get_cell_styles(self, styles):
        cell_styles = defaultdict(lambda: {"font_size": 10})
        [cell_styles[key].update(cell_style) for key, cell_style in styles.items()]

        header_keys = list(self.header.keys())
        cell_styles = {header_keys.index(key): self.workbook.add_format(style)
                       for key, style in cell_styles.items() if key in header_keys}
        return cell_styles

    def get_cell_comments(self, comments):
        header_keys = list(self.header.keys())
        cell_comments = {header_keys.index(key): comment for key, comment in comments.items() if key in header_keys}
        return cell_comments

    def open(self):
        if not self._opened:
            self.workbook = xlsxwriter.Workbook(self.save_to, options=self.options)
            self._opened = True
        return self

    def close(self):
        if self._opened:
            self.workbook.close()
            self._opened = False
