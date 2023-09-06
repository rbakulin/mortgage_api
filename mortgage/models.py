from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .helpers import (MORTGAGE_PERIOD_LIMITS, days_in_year,
                      get_last_day_in_months, get_timedelta)


class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Mortgage(CreatedUpdatedModel):
    percent = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="bank percent",
                                  validators=[MinValueValidator(0), MaxValueValidator(100)])
    period = models.IntegerField(verbose_name="period", validators=[
        MinValueValidator(MORTGAGE_PERIOD_LIMITS['min']),
        MaxValueValidator(MORTGAGE_PERIOD_LIMITS['max']),
    ])
    first_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="first payment amount",
                                               validators=[MinValueValidator(1)])
    credit_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="total amount",
                                        validators=[MinValueValidator(1)])
    issue_date = models.DateField(verbose_name="issue date")
    user = models.ForeignKey('auth.User', related_name='mortgages', on_delete=models.CASCADE, null=True)

    @property
    def apartment_price(self) -> Decimal:
        return self.first_payment_amount + self.credit_amount

    @property
    def period_in_months(self) -> int:
        return self.period * 12

    @property
    def last_payment_date(self) -> date:
        return self.issue_date + get_timedelta(months=self.period_in_months)

    @property
    def first_payment_date(self) -> date:
        return self.issue_date + get_timedelta(months=1)

    @property
    def monthly_percent(self) -> Decimal:
        return Decimal(self.percent / (12 * 100))  # 1/12 of credit's percent in 0.xx format

    @staticmethod
    def get_mortgage(mortgage_id: int) -> Mortgage:
        return Mortgage.objects.filter(pk=mortgage_id).first()

    class Meta:
        db_table = 'mortgage'
        ordering = ['id']


class Payment(CreatedUpdatedModel):
    date = models.DateField(verbose_name="date")
    amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="amount",
                                 validators=[MinValueValidator(1)])
    mortgage = models.ForeignKey('Mortgage', on_delete=models.CASCADE, related_name="payments",
                                 verbose_name='mortgage')
    is_extra = models.BooleanField(verbose_name='is extra payment', default=False)
    bank_amount = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="bank amount", null=True)
    debt_decrease = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt decrease", null=True)
    debt_rest = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="debt rest", null=True)

    def get_prev_payment(self) -> Payment:
        return Payment.objects.filter(
            mortgage_id=self.mortgage_id,
            date__lte=self.date
        ).exclude(pk=self.pk).order_by('-date', '-created_at').first()

    def get_next_payment(self) -> Payment:
        return Payment.objects.filter(mortgage_id=self.mortgage_id, date__gt=self.date).order_by('date').first()

    def calc_bank_amount(self) -> Decimal:
        prev_payment = self.get_prev_payment()
        if prev_payment:
            prev_payment_date = prev_payment.date
            debt_rest = prev_payment.debt_rest
        else:
            prev_payment_date = self.mortgage.issue_date
            debt_rest = self.mortgage.credit_amount
        days_in_current_year = days_in_year(self.date.year)

        def _get_dividend(days_count: int) -> Decimal:
            return debt_rest * self.mortgage.percent * days_count

        def _get_divisor(days_count: int) -> int:
            return days_count * 100

        if self.date.year == prev_payment_date.year:
            date_delta = self.date - prev_payment_date
            bank_percent = _get_dividend(date_delta.days) / _get_divisor(days_in_current_year)
            return round(bank_percent, 2)

        days_in_prev_month = get_last_day_in_months(prev_payment_date) - prev_payment_date.day
        days_in_prev_year = days_in_year(prev_payment_date.year)
        days_in_current_month = self.date.day
        bank_percent = _get_dividend(days_in_prev_month) / _get_divisor(days_in_prev_year) + _get_dividend(
            days_in_current_month) / _get_divisor(days_in_current_year)
        return round(bank_percent, 2)

    def calc_debt_decrease(self) -> Decimal:
        return self.amount - self.bank_amount

    def calc_debt_rest(self) -> Decimal:
        prev_payment = self.get_prev_payment()
        if prev_payment:
            prev_amount = prev_payment.debt_rest
        else:
            prev_amount = self.mortgage.credit_amount
        return prev_amount - self.debt_decrease

    class Meta:
        db_table = 'payment'
