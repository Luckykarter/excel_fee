from django.test import TestCase
from excelfee.excelhandler import ExcelHandler
import os

def test_excel():
    handler = ExcelHandler()
    print(handler._get_value('Integration', 'B4'))
    handler._set_value('Integration', 'B4', 0.01)
    print(handler._get_value('Integration', 'F3'))
    print(handler._get_value('Integration', 'F4'))
    assert True

