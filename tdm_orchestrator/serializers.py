from rest_framework import serializers
from .models import SqlScript, Runner, RunnerStep, ExecutionLog


class SqlScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SqlScript
        fields = '__all__'

class RunnerStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunnerStep
        fields = '__all__'

class RunnerSerializer(serializers.ModelSerializer):
    runnerstep_set = RunnerStepSerializer(many=True, read_only=True)
    scripts = SqlScriptSerializer(many=True, read_only=True)
    class Meta:
        model = Runner
        fields = '__all__'

class ExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionLog
        fields = '__all__'
