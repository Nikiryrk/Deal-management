from django.urls import path
from start.views.start import start
from start.views import create_deal,Deals

urlpatterns = [
    path('', start, name='start'),
    path('create_deal/', create_deal.create_deal, name='create_deal'),
    path('deals_table/',Deals.deals_table, name='deals_table')
]

