from django.contrib import admin

from .models import Mortgage, Payment


class PaymentAdmin(admin.ModelAdmin):
    list_filter = ['mortgage__id']
    list_display = ['date', 'amount', 'mortgage_id', 'bank_amount', 'debt_decrease', 'debt_rest', 'is_extra']
    readonly_fields = ('bank_amount', 'debt_decrease', 'debt_rest')
    ordering = ['mortgage', 'date', 'created_at']


class MortgageAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['pk', 'percent', 'period', 'first_payment_amount', 'apartment_price', 'credit_amount', 'issue_date',
                    'user']


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Mortgage, MortgageAdmin)
