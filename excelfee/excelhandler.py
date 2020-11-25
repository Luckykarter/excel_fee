import openpyxl
from pycel import ExcelCompiler
from excelfee.models import InputData, CalcResult, ExcelFile, InputDataGeneric, Cell
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


