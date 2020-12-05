import openpyxl
from pycel import ExcelCompiler
from excelfee.models import Output, Input
from excelfee.serializers import CellSerializer
import os


class ExcelHandler:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, file):
        self.book = openpyxl.load_workbook(file)
        self.excel = ExcelCompiler(excel=self.book)

    def _set_value(self, sheet: str, cell: str, value: any):
        self.book.worksheets[self.book.sheetnames.index(sheet)][cell] = value

    def _get_value(self, sheet: str, cell: str):
        return self.excel.evaluate(f'{sheet}!{cell}')

    def calculate(self, data: Input,
                  excel_id: str) -> Output:
        try:
            for cell in data.input:
                # cell = Cell(**d)
                self._set_value(cell.sheet, cell.cell, cell.value)

            result = Output()
            cells = []
            self.excel = ExcelCompiler(excel=self.book)
            for cell in data.output:
                cell.value = self._get_value(cell.sheet, cell.cell)
                cells.append(cell)
            result.cells = cells
            result.filename = excel_id
        except Exception as e:
            raise e

        return result

    @property
    def get_cells(self):
        result = {}

        for i, sheet_name in enumerate(self.book.sheetnames):
            sheet = self.book.worksheets[i]
            names = True
            cells = []
            cols = [col for col in sheet.iter_cols()]
            for c, col in enumerate(cols):
                if not names:
                    names = True
                    continue

                for n, cell in enumerate(col):
                    if cell.value is None:
                        continue
                    names = False
                    if c < len(cols) - 1:
                        tar_cell = cols[c + 1][n]
                        cells.append({
                            'cell': cell.value,
                            'type': 'N' if tar_cell.data_type == 'n' else 'T',
                            'coordinate': tar_cell.coordinate,
                        })

            result[sheet_name] = cells

        return result
