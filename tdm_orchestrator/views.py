from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import SqlScript, Runner, RunnerStep, ExecutionLog
from .serializers import (
    SqlScriptSerializer, RunnerStepSerializer, RunnerSerializer, ExecutionLogSerializer
)

class SqlScriptViewSet(viewsets.ModelViewSet):
    queryset = SqlScript.objects.all()
    serializer_class = SqlScriptSerializer

class RunnerStepViewSet(viewsets.ModelViewSet):
    queryset = RunnerStep.objects.all()
    serializer_class = RunnerStepSerializer

class RunnerViewSet(viewsets.ModelViewSet):
    queryset = Runner.objects.all()
    serializer_class = RunnerSerializer

class ExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = ExecutionLog.objects.all()
    serializer_class = ExecutionLogSerializer
