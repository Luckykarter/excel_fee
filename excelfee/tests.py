from django.test import TestCase
from excelfee.excelhandler import ExcelHandler
import os




def test_excel():
    handler = ExcelHandler('C:\\Users\\egorw\\PycharmProjects\\doka\\excelfee\\data\\F_GICX_1.xlsx')
    print(handler.get_cells)
    print(handler._get_value('Integration', 'B4'))
    handler._set_value('Integration', 'B4', 0.01)
    print(handler._get_value('Integration', 'F3'))
    print(handler._get_value('Integration', 'F4'))
    content = handler._get_file_content()

    with open("C:\\Users\\egorw\\PycharmProjects\\doka\\excelfee\\data\\tst.txt", 'w+') as b:
        b.write(content)

    assert True

