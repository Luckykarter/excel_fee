import openpyxl
from pycel import ExcelCompiler
from excelfee.models import InputData, CalcResult, ExcelFile, InputDataGeneric, Cell, Input
from excelfee.serializers import CellSerializer
import os


class ExcelHandler:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    # FILE = os.path.join(BASE_PATH, "data\\FeeCalcDemo.xlsx")

    def __init__(self, file):
        self.book = openpyxl.load_workbook(file)
        self.worksheet = 'Integration'
        self.map_in = {
            'startdate': 'B3',
            'rate': 'B4',
            'amount': 'B5',
        }
        self.map_out = {
            'amount': 'F3',
            'description': 'F4',
        }

        self.excel = ExcelCompiler(excel=self.book)

    def _set_value(self, sheet: str, cell: str, value: any):
        self.book.worksheets[self.book.sheetnames.index(sheet)][cell] = value

    def _get_value(self, sheet: str, cell: str):
        excel = ExcelCompiler(excel=self.book)
        return excel.evaluate(f'{sheet}!{cell}')

    def calculate(self, data: Input,
                  excel: ExcelFile) -> InputDataGeneric:
        try:
            for cell in data.input:
                # cell = Cell(**d)
                self._set_value(cell.sheet, cell.cell, cell.value)

            result = InputDataGeneric()
            cells = []
            for cell in data.output:
                # cell = Cell(**d)
                cell.value = self._get_value(cell.sheet, cell.cell)
                cells.append(cell)
            result.cells = cells
            result.filename = excel.filename
        except Exception as e:
            raise e

        return result

    def calculate_fee(self, input_data: InputData, excel: ExcelFile) -> CalcResult:
        try:

            rate = input_data.rate
            self._set_value(self.worksheet, self.map_in['startdate'], input_data.startdate)
            if rate:
                self._set_value(self.worksheet, self.map_in['rate'], input_data.rate)
            self._set_value(self.worksheet, self.map_in['amount'], input_data.amount)

            result = CalcResult()
            result.amount = self._get_value(self.worksheet, self.map_out['amount'])
            result.description = self._get_value(self.worksheet, self.map_out['description'])
            result.excel = excel
        except Exception as e:
            raise e

        return result

    def calculate_fee_generic(self, input_data: InputDataGeneric, excel: ExcelFile) -> CalcResult:
        try:
            for d in input_data.cells:
                cell = Cell(**d)
                self._set_value(cell.sheet, cell.cell, cell.value)

            result = CalcResult()
            result.amount = self._get_value(self.worksheet, self.map_out['amount'])
            result.description = self._get_value(self.worksheet, self.map_out['description'])
            result.excel = excel

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
