import logging
from decimal import Decimal
from math import pow
from typing import Callable, Optional, Tuple

from django.db import transaction

from mortgage.helpers import get_months_difference, get_timedelta
from mortgage.messages import events
from mortgage.models import Mortgage, Payment

logger = logging.getLogger('django')


class PaymentScheduler:
    def __init__(self, mortgage: Mortgage) -> None:
        self.mortgage = mortgage

    @transaction.atomic()
    def calc_and_save_payments_schedule(self, start_payment_number: int = 1, amount: Optional[Decimal] = None) -> None:
        # 1 - hardcode in math formula
        power = Decimal(pow(self.mortgage.monthly_percent + 1, self.mortgage.period_in_months))
        coef = Decimal(power * self.mortgage.monthly_percent / (power - 1))
        amount = round(coef * self.mortgage.credit_amount, 2) if not amount else amount
        number_of_payments = range(start_payment_number, self.mortgage.period_in_months)

        for i in number_of_payments:
            payment = Payment(
                mortgage=self.mortgage,
                amount=amount,
                date=self.mortgage.issue_date + get_timedelta(months=i),
            )
            payment.bank_amount = payment.calc_bank_amount()
            payment.debt_decrease = payment.calc_debt_decrease()
            payment.debt_rest = payment.calc_debt_rest()
            payment.save()
            # to avoid adding unneeded payments when bank percent is high
            if payment.debt_rest < amount:
                break

        logger.info(events.PAYMENTS_ADDED.format(payments_num=self.mortgage.period_in_months - start_payment_number,
                                                 mortgage_id=self.mortgage.pk, amount=amount))

        # add last payment manually
        last_payment = Payment(
            mortgage=self.mortgage,
            date=self.mortgage.last_payment_date,
        )
        last_payment.amount = last_payment.get_prev_payment().debt_rest
        last_payment.bank_amount = last_payment.calc_bank_amount()
        last_payment.debt_decrease = last_payment.calc_debt_decrease()
        last_payment.debt_rest = 0
        last_payment.save()

        logger.info(events.LAST_PAYMENT_ADDED.format(mortgage_id=self.mortgage.pk, amount=last_payment.amount))


class ExtraPaymentCalculator:
    def __init__(self, mortgage: Mortgage, extra_payment: Payment) -> None:
        self.mortgage = mortgage
        self.extra_payment = extra_payment

    def save_extra_payment(self) -> None:
        saving_method = self.get_saving_method()
        return saving_method()

    def get_saving_method(self) -> Callable:
        date = self.extra_payment.date
        amount = self.extra_payment.amount
        mortgage_id = self.mortgage.pk
        for payment in Payment.objects.filter(mortgage_id=self.mortgage.pk):
            if payment.date == self.extra_payment.date:
                logger.info(events.SAVING_METHOD_CHOSEN.format(date=date, amount=amount, mortgage_id=mortgage_id,
                                                               method_name=self.same_date_saving.__name__))
                return self.same_date_saving

        extra_payment = self.extra_payment
        extra_payment.bank_amount = extra_payment.calc_bank_amount()
        if extra_payment.amount <= extra_payment.bank_amount:
            logger.info(events.SAVING_METHOD_CHOSEN.format(date=date, amount=amount, mortgage_id=mortgage_id,
                                                           method_name=self.less_than_bank_percent_saving.__name__))
            return self.less_than_bank_percent_saving
        else:
            logger.info(events.SAVING_METHOD_CHOSEN.format(date=date, amount=amount, mortgage_id=mortgage_id,
                                                           method_name=self.more_than_bank_percent_saving.__name__))
            return self.more_than_bank_percent_saving

    @transaction.atomic(durable=True)
    def same_date_saving(self) -> None:
        extra_payment = self.extra_payment
        extra_payment.bank_amount = 0  # whole extra payment goes for debt decrease
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()
        logger.info(events.EXTRA_PAYMENT_ADDED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                      date=extra_payment.date))

        next_payment = self.extra_payment.get_next_payment()
        next_payment.amount = next_payment.calc_bank_amount()
        next_payment.bank_amount = next_payment.amount
        next_payment.debt_decrease = 0
        next_payment.debt_rest = next_payment.calc_debt_rest() - next_payment.debt_decrease
        next_payment.save()
        logger.info(events.NEXT_PAYMENT_UPDATED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                       date=extra_payment.date))

        # delete old payment schedule if it exists
        Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment.date).delete()
        logger.info(events.SCHEDULE_DELETED.format(mortgage_id=self.mortgage.pk))

        start_payment_number, amount = self.get_new_schedule_parameters(next_payment)
        payment_scheduler = PaymentScheduler(mortgage=self.mortgage)
        payment_scheduler.calc_and_save_payments_schedule(start_payment_number, amount)

    @transaction.atomic(durable=True)
    def less_than_bank_percent_saving(self) -> None:
        extra_payment = self.extra_payment
        extra_payment.bank_amount = self.extra_payment.amount
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()
        logger.info(events.EXTRA_PAYMENT_ADDED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                      date=extra_payment.date))

        next_payment = extra_payment.get_next_payment()
        next_payment.amount = next_payment.amount - self.extra_payment.amount
        next_payment.bank_amount = next_payment.calc_bank_amount()
        next_payment.debt_decrease = next_payment.calc_debt_decrease()
        next_payment.debt_rest = next_payment.calc_debt_rest()
        next_payment.save()
        logger.info(events.NEXT_PAYMENT_UPDATED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                       date=extra_payment.date))

    @transaction.atomic(durable=True)
    def more_than_bank_percent_saving(self) -> None:
        extra_payment = self.extra_payment
        extra_payment.bank_amount = extra_payment.calc_bank_amount()
        extra_payment.debt_decrease = extra_payment.calc_debt_decrease()
        extra_payment.debt_rest = extra_payment.calc_debt_rest()
        extra_payment.save()
        logger.info(events.EXTRA_PAYMENT_ADDED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                      date=extra_payment.date))

        next_payment = extra_payment.get_next_payment()
        next_payment.bank_amount = next_payment.calc_bank_amount()
        next_payment.amount = next_payment.bank_amount
        next_payment.debt_decrease = next_payment.calc_debt_decrease()
        next_payment.debt_rest = next_payment.calc_debt_rest()
        next_payment.save()
        logger.info(events.NEXT_PAYMENT_UPDATED.format(mortgage_id=self.mortgage.pk, amount=extra_payment.amount,
                                                       date=extra_payment.date))

        # delete old payment schedule if it exists
        Payment.objects.filter(mortgage_id=self.mortgage.pk, date__gt=next_payment.date).delete()
        logger.info(events.SCHEDULE_DELETED.format(mortgage_id=self.mortgage.pk))

        start_payment_number, amount = self.get_new_schedule_parameters(next_payment)
        payment_scheduler = PaymentScheduler(mortgage=self.mortgage)
        payment_scheduler.calc_and_save_payments_schedule(start_payment_number, amount)

    def get_new_schedule_parameters(self, next_payment: Payment) -> Tuple[int, Decimal]:
        months_left = get_months_difference(self.mortgage.last_payment_date, next_payment.date)
        power = Decimal(pow(self.mortgage.monthly_percent + 1, months_left))
        coef = Decimal(power * self.mortgage.monthly_percent / (power - 1))

        start_payment_number = get_months_difference(next_payment.date, self.mortgage.issue_date) + 1
        amount = round(coef * self.extra_payment.debt_rest, 2)
        logger.info(events.NEW_SCHEDULE_PARAMS.format(mortgage_id=self.mortgage.pk, months_left=months_left, pow=power,
                                                      coef=coef, start_payment_num=start_payment_number, amount=amount))
        return start_payment_number, amount
