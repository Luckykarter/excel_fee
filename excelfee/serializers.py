from rest_framework.serializers import ModelSerializer
import rest_framework.serializers as serializers
import excelfee.models as models


class ExcelPurposeSerializer(ModelSerializer):
    class Meta:
        model = models.ExcelPurpose
        exclude = ['id']


class CellPointerSerializer(ModelSerializer):
    # purpose = ExcelPurposeSerializer()

    class Meta:
        model = models.CellPointer
        fields = '__all__'


class CellSerializer(ModelSerializer):
    class Meta:
        model = models.Cell
        fields = '__all__'


class LoadExcelSerializer(ModelSerializer):
    class Meta:
        model = models.ExcelFile
        fields = ['id', 'content']


class ExcelSerializer(ModelSerializer):
    purpose = ExcelPurposeSerializer()

    class Meta:
        model = models.ExcelFile
        fields = ['purpose', 'id', 'version', 'timestamp', 'sheetnames']


class OutputSerializer(ModelSerializer):
    cells = CellSerializer(many=True)

    class Meta:
        # model = models.InputData
        model = models.Output
        fields = '__all__'


class InputSerializer(ModelSerializer):
    input = CellSerializer(many=True)
    output = CellPointerSerializer(many=True)

    class Meta:
        model = models.Input
        fields = '__all__'


class CalcResultSerializer(ModelSerializer):
    excel = ExcelSerializer()

    class Meta:
        model = models.CalcResult
        fields = '__all__'


class ArraySerializer(serializers.Serializer):
    class Meta:
        field = serializers.StringRelatedField()


class SheetSerializer(serializers.Serializer):
    sheetnames = ArraySerializer(many=True)

    class Meta:
        fields = ['sheetnames']


class ErrorSerializer(serializers.Serializer):
    error = serializers.StringRelatedField()


class PropertySerializer(serializers.Serializer):
    property_name = serializers.StringRelatedField(many=True)
