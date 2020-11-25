from rest_framework.response import Response

from test_autogen.models import LID

# Create your views here.
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from test_autogen import serializers


@swagger_auto_schema(
    methods=['GET'],
    operation_id='INFLID',
    operation_description='Info Import L/C',
    responses={200: openapi.Response('Import L/C', serializers.LIDSerializer()),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
def get_contract(request, **kwargs):
    ref = kwargs.get('ownref')
    if ref is None:
        contract = LID.objects.all()
    else:
        contract = LID.objects.filter(OWNREF__in=ref)
    serializer = serializers.LIDSerializer(contract, many=True)
    return Response(serializer.data)
