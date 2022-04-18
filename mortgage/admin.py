from django.contrib import admin
from .models import Mortgage, RealEstateObject, Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'mortgage', 'bank_percent', 'debt_decrease', 'debt_rest']
    readonly_fields = ('bank_percent', 'debt_decrease', 'debt_rest')
    ordering = ['date']


admin.site.register(Payment, PaymentAdmin)
admin.site.register([Mortgage, RealEstateObject])
