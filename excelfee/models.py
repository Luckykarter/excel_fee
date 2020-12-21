from rest_framework import serializers
from django.db import models
import os


class ExcelPurpose(models.Model):
    class Meta:
        managed = False

    PURPOSES = {
        'F': 'Fee calculation'
    }

    id = models.IntegerField(name='id', primary_key=True, serialize=False)
    purpose = models.CharField(name='purpose',
                               help_text='The purpose for Excel usage',
                               choices=[(key, value) for key, value in PURPOSES.items()],
                               default='F',
                               max_length=4)
    target = models.CharField(name='target',
                              help_text='Target object for Excel calculator\n(E.g. FEECODE for fee calculation)',
                              max_length=40)

    def __str__(self):
        return f'{self.PURPOSES[self.purpose]}: {self.target}'


class ExcelFile(models.Model):
    class Meta:
        managed = False

    id = models.CharField(name="id",
                          help_text='Excel filename to use for calculation',
                          max_length=255, primary_key=True)

    version = models.IntegerField(name="version", auto_created=True, default=1,
                                  help_text="Sequential number of the Excel file loaded for the same purpose")

    timestamp = models.DateTimeField(name='timestamp', auto_now=True,
                                     help_text='Auto-generated timestamp when file uploaded')

    filepath = models.FilePathField(name='filepath',
                                    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))

    purpose = models.ForeignKey(ExcelPurpose, on_delete=models.CASCADE)

    content = models.TextField(name='content',
                               help_text='Excel file Base64 encoded', auto_created=True)

    sheetnames = models.TextField(name='sheetnames', default='',
                                  help_text='List of sheet names from uploaded Excel')

    def get_filename(self):
        return "_".join((
            self.purpose.purpose,
            self.purpose.target,
            str(self.version))) + ".xlsx"

    def __str__(self):
        return self.get_filename()


class CellPointer(models.Model, models.Field):
    class Meta:
        managed = False

    sheet = models.TextField(name='sheet', help_text='Name of the Excel sheet to work with')
    cell = models.TextField(name='cell', help_text='Cell coordinates (e.g. A1, B2, etc)')


class Cell(models.Model, models.Field):
    class Meta:
        managed = False

    sheet = models.TextField(name='sheet', help_text='Name of the Excel sheet to work with')
    cell = models.TextField(name='cell', help_text='Cell coordinates (e.g. A1, B2, etc)')
    value_type = models.TextField(name='value_type', choices=[('T', 'Text'), ('N', 'Numeric')])
    value_text = models.TextField(name='value_text', help_text='Value of text cell', default='')
    value_numeric = models.FloatField(name='value_numeric', help_text='Value of numeric cell', default=0.0)
    text_description = models.TextField(name='text_description',
                                        help_text='Optional textual description of the Excel cell',
                                        default='')

    @property
    def value(self):
        return self.value_text if self.value_type == 'T' else self.value_numeric

    @value.setter
    def value(self, value):
        self.value_numeric = 0
        self.value_text = ''

        if self.value_type == 'T':
            self.value_text = value
        else:
            self.value_numeric = value


class Output(models.Model):
    class Meta:
        managed = False

    id = models.CharField(name="id",
                          help_text='Excel filename to use for calculation',
                          max_length=255, primary_key=True)
    cells = [Cell('cell')]
    # cells = [models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='cell')]


class OutputFile(models.Model):
    class Meta:
        managed = False

    id = models.CharField(name="id",
                          help_text='Excel filename to use for calculation',
                          max_length=255, primary_key=True)
    content = models.TextField(name="content", help_text="Base64 encoded Excel file")


class Input(models.Model):
    class Meta:
        managed = False

    id = models.CharField(name="id",
                          help_text='Excel filename to use for calculation',
                          max_length=255, primary_key=True)

    input = [models.ForeignKey(Cell, on_delete=models.DO_NOTHING, related_name='input')]
    output = [models.ForeignKey(CellPointer, on_delete=models.DO_NOTHING, related_name='output')]

class InputFile(models.Model):
    class Meta:
        managed = False

    id = models.CharField(name="id",
                          help_text='Excel filename to use for calculation',
                          max_length=255, primary_key=True)

    input = [models.ForeignKey(Cell, on_delete=models.DO_NOTHING, related_name='input')]

class CalcResult(models.Model):
    class Meta:
        managed = False

    amount = models.FloatField(name="amount",
                               help_text="Amount calculated from provided Excel file", primary_key=True)

    description = models.CharField(name='description',
                                   help_text="Describes details of fee calculation",
                                   max_length=1024)

    excel = models.ForeignKey(ExcelFile, on_delete=models.DO_NOTHING,
                              help_text='File used for calculation')
