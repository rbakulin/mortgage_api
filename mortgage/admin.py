from django.contrib import admin
from .models import Mortgage, RealEstateObject, Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'date', 'amount', 'mortgage', 'bank_share', 'debt_decrease', 'debt_rest']
    readonly_fields = ('bank_share', 'debt_decrease', 'debt_rest')
    ordering = ['date']


class MortgageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'percent', 'period', 'first_payment_amount', 'total_amount', 'issue_date',
                    'real_estate_object', 'user']


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Mortgage, MortgageAdmin)
admin.site.register(RealEstateObject)
