from django.contrib import admin
from .models import Mortgage, RealEstateObject, Payment

admin.site.register([Mortgage, RealEstateObject, Payment])
