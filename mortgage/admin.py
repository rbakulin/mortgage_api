from django.contrib import admin
from .models import Mortgage, Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'date', 'amount', 'mortgage', 'bank_share', 'debt_decrease', 'debt_rest']
    readonly_fields = ('bank_share', 'debt_decrease', 'debt_rest')
    ordering = ['date']


class MortgageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'percent', 'period', 'first_payment_amount', 'apartment_price', 'total_amount', 'issue_date',
                    'user']


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Mortgage, MortgageAdmin)
