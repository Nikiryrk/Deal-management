from django.urls import path
from start.views.start import start
from start.views import create_deal,Deals
from qr.views import product, autocomplete
from employee_table.views import employee_table
from map.views import map

urlpatterns = [
    path('', start, name='start'),
    path('create_deal/', create_deal.create_deal, name='create_deal'),
    path('deals_table/',Deals.deals_table, name='deals_table'),
    path('search/', product.product, name='product'),
    path('product/<str:token>/qr/', product.qr_code, name='qr_code'),
    path('product/<str:uid>/generate_qr/', product.generate_qr, name='generate_qr'),
    path('public/product/<str:token>/', product.public_product, name='public_product'),
    path('autocomplete/', autocomplete.autocomplete, name='autocomplete'),
    path('employee_table/', employee_table.employee_table, name='employee_table'),
    path('map/', map.map, name='map'),
]

