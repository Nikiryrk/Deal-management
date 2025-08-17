from django.urls import path

from dealmanagement.integration_utils.bitrix24.views.start import start

urlpatterns = [
    path('', start),
]
