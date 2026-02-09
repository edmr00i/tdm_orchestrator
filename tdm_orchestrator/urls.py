
from rest_framework import routers
from .views import (
	SqlScriptViewSet, RunnerStepViewSet, RunnerViewSet, ExecutionLogViewSet
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'scripts', SqlScriptViewSet)
router.register(r'runners', RunnerViewSet)
router.register(r'runnersteps', RunnerStepViewSet)
router.register(r'executionlogs', ExecutionLogViewSet)

urlpatterns = [
	path('api/', include(router.urls)),
]
