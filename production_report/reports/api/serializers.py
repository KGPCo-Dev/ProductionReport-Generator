from rest_framework import serializers

class ReportInputSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La fecha debe ser anterior a la final.")
        return data