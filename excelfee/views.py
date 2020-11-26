from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import excelfee.serializers as serializers
from excelfee.excelhandler import ExcelHandler
import excelfee.models as models
import base64
import os
import openpyxl


def _err(e=None):
    if e is None:
        e = "description of the error"
    return {'error': str(e)}


def _get_examples(e):
    return {
        "application/json": e
    }


@swagger_auto_schema(
    methods=['POST'],
    operation_id='calculate_fee',
    operation_description='Calculate fee using MS Excel file\n'
                          'Update Excel cells with the values from JSON (array cells) '
                          'and get result as a calculated fee. Updated Excel file handled in-memory\n'
                          'To update/upload new Excel - use endpoint upload_excel',
    request_body=serializers.InputDataSerializer,
    # request_body=serializers.InputDataSerializer,
    responses={200: openapi.Response('OK', serializers.CalcResultSerializer),
               404: openapi.Response('Excel file not found', serializers.ErrorSerializer,
                                     examples=_get_examples(
                                         _err("[Errno 2] No such file or directory: FeeCalcDemo.xlsx"))),
               500: openapi.Response('Calculation failed', serializers.ErrorSerializer,
                                     examples=_get_examples(_err()))})
@api_view(['POST'])
def calculate_fee(request):
    try:
        filename = request.data.get('filename')
        excel_file = models.ExcelFile.objects.filter(filename__iexact=filename)
        if not excel_file:
            raise FileNotFoundError(f'Excel file {filename} not found')

        excel_file = excel_file[0]
        excel = ExcelHandler(excel_file.filepath)
        input_data = models.InputDataGeneric(**request.data)
        result = excel.calculate_fee_generic(input_data, excel_file)
        return Response(serializers.CalcResultSerializer(result).data,
                        status=status.HTTP_200_OK)
    except FileNotFoundError as e:
        return Response({'error': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    methods=['POST'],
    operation_id='calculate',
    operation_description='Calculate cells using MS Excel file\n'
                          'Update Excel cells with the values from JSON (array cells) '
                          'and get result as a calculated cells. Updated Excel file handled in-memory\n'
                          'To update/upload new Excel - use endpoint upload_excel\n\n'
                          'Input JSON object contains cells with values that should be populated\n'
                          'Output JSON object contains pointers to the cells that have to be returned as'
                          'calculation answer',
    request_body=serializers.InputSerializer,
    responses={200: openapi.Response('OK', serializers.InputDataSerializer),
               404: openapi.Response('Excel file not found', serializers.ErrorSerializer,
                                     examples=_get_examples(
                                         _err("[Errno 2] No such file or directory: FeeCalcDemo.xlsx"))),
               500: openapi.Response('Calculation failed', serializers.ErrorSerializer,
                                     examples=_get_examples(_err()))})
@api_view(['POST'])
def calculate(request):
    try:
        filename = request.data.get('filename')
        excel_file = models.ExcelFile.objects.filter(filename__iexact=filename)
        if not excel_file:
            raise FileNotFoundError(f'Excel file {filename} not found')

        excel_file = excel_file[0]
        excel = ExcelHandler(excel_file.filepath)

        input_ = request.data.pop('input')
        output_ = request.data.pop('output')

        input_data = models.Input(**request.data)
        input_data.input = [models.Cell(**x) for x in input_.get('cells')]
        input_data.output = [models.Cell(**x) for x in output_.get('cells')]

        # input_json = request.data.get('input')
        # output_json = request.data.get('output')
        result = excel.calculate(input_data, excel_file)

        return Response(serializers.InputDataSerializer(result).data,
                        status=status.HTTP_200_OK)
    except FileNotFoundError as e:
        return Response({'error': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    methods=['GET'],
    operation_id='show_files',
    operation_description='Display all currently loaded files',
    responses={200: openapi.Response('OK', serializers.ExcelSerializer),
               404: openapi.Response('Excel file not found', serializers.ErrorSerializer,
                                     examples=_get_examples(
                                         _err("[Errno 2] No such file or directory: FeeCalcDemo.xlsx"))),
               })
@api_view(['GET'])
def show_files(request):
    files = models.ExcelFile.objects.order_by('purpose', 'filename', '-version')
    if not files:
        return Response(_err('No loaded Excel files'),
                        status=status.HTTP_404_NOT_FOUND)

    return Response(serializers.ExcelSerializer(files, many=True).data,
                    status=status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_id='upload_excel',
    operation_description='Upload MS Excel file',
    request_body=serializers.LoadExcelSerializer,
    responses={200: openapi.Response('File Uploaded Successfully', serializers.ExcelSerializer),
               400: openapi.Response('Bad Request', serializers.ErrorSerializer,
                                     examples=_get_examples(_err('content missing'))),
               500: openapi.Response('Error uploading Excel', serializers.ErrorSerializer,
                                     examples=_get_examples(_err('description of the error')))})
@api_view(['POST'])
def upload_excel(request):
    try:
        purpose_data = request.data.pop('purpose')
        purpose = models.ExcelPurpose.objects.filter(
            purpose=purpose_data.get('purpose'),
            target=purpose_data.get('target')
        )
        if not purpose:
            models.ExcelPurpose.objects.create(**purpose_data)
            purpose = models.ExcelPurpose.objects.order_by('-id')[0]
        else:
            purpose = purpose[0]

        excel_file = models.ExcelFile.objects.filter(purpose=purpose).order_by('-version')
        if not excel_file:
            excel_file = models.ExcelFile(purpose=purpose, **request.data)
        else:
            excel_file = excel_file[0]
            content = request.data.get('content')
            if excel_file.content != content:
                excel_file.version += 1
                excel_file.content = content
                excel_file.id = None

    except Exception as e:
        return Response(_err(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if excel_file.content is None:
        return Response(_err('content missing'), status=status.HTTP_400_BAD_REQUEST)

    if excel_file.filename is None:
        return Response(_err('filename missing'), status=status.HTTP_400_BAD_REQUEST)

    try:
        file_content = base64.b64decode(excel_file.content)
        excel_file.filename = excel_file.get_filename()
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = os.path.join(folder, excel_file.filename)
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        excel_file.filepath = filename

        with open(excel_file.filepath, "wb") as f:
            f.write(file_content)


    except Exception as e:
        return Response(_err(e), status=status.HTTP_400_BAD_REQUEST)

    excel_file.purpose.save()
    excel_file.save()
    book = openpyxl.load_workbook(excel_file.filepath)
    resp = serializers.ExcelSerializer(excel_file).data
    resp['sheetnames'] = book.sheetnames

    return Response(resp, status=status.HTTP_200_OK)


SUPPORTED_PROPERTIES = {
    'content', 'sheetnames', 'cells'
}


@swagger_auto_schema(
    methods=['GET'],
    operation_id='get_file_property',
    operation_description='Returns given property of the given Excel filename. Supported properties:\n'
                          '{}'.format("\n".join(SUPPORTED_PROPERTIES)),
    responses={200: openapi.Response('OK', serializers.PropertySerializer,
                                     examples=_get_examples({'property_name': ['value']})),
               400: openapi.Response('Bad Request', serializers.ErrorSerializer, examples=_get_examples(_err())),
               404: openapi.Response('Excel file not found', serializers.ErrorSerializer,
                                     examples=_get_examples(
                                         _err("[Errno 2] No such file or directory: FeeCalcDemo.xlsx"))),
               })
@api_view(['GET'])
def get_property(request, **kwargs):
    filename = kwargs.get('filename')
    property = kwargs.get('property')
    property = property.lower()
    if not filename:
        return Response(_err("filename is empty"), status=status.HTTP_400_BAD_REQUEST)

    if not property:
        return Response(_err("property is empty"), status=status.HTTP_400_BAD_REQUEST)

    file = models.ExcelFile.objects.get(filename__iexact=filename)
    if not file:
        return Response(_err(f"file {filename} not found"), status=status.HTTP_404_NOT_FOUND)

    if property not in SUPPORTED_PROPERTIES:
        resp = _err(f"property {property} is not supported")
        resp['supported_properties'] = [x for x in SUPPORTED_PROPERTIES]

        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    if property == 'sheetnames':
        book = openpyxl.load_workbook(file.filepath)
        return Response({'sheetnames': book.sheetnames}, status=status.HTTP_200_OK)
    elif property == 'content':
        return Response({'content': file.content}, status=status.HTTP_200_OK)
    elif property == 'cells':
        excel = ExcelHandler(file.filepath)
        return Response(excel.get_cells, status=status.HTTP_200_OK)
