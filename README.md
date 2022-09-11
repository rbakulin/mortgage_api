<h1 align="center" style="font-size: 3rem;">
MORTGAGE-API
</h1>
<p align="center">
 <em>REST API for calculating mortgage parametrs: payment schedule, bank percent, extra payments etc.</em></p>

---
## Run
1. Run migrations:
```shell
docker-compose run app python manage.py migrate
```
2. Run the app and the database:
```shell
docker-compose up
```
## Quickstart
1. Create a user:<br><b>POST</b> `127.0.0.1:8000/auth/register/`
```json
{
    "username": "admin",
    "password": "adminadmin",
    "password2": "adminadmin",
    "email": "admin@example.com"
}
```
2. Get a token:<br><b>POST</b> `127.0.0.1:8000/auth/token/`
```json
{
    "username": "admin",
    "password": "adminadmin"
}
```
3. Create a mortgage:<br><b>POST</b> `127.0.0.1:8000/api/v1/mortgage/`<br><em>headers: {Authorization: Bearer <your_token_value>}</em>
```json
{
    "percent": "8.20",
    "period": 25,
    "first_payment_amount": 2500000,
    "total_amount": 11000000,
    "issue_date": "2021-09-04"
}
```
4. Calculate mortgage schedule: <br><b>POST</b> `127.0.0.1:8000/api/v1/mortgage/<mortgage_id>/calc-payment-schedule/`<br><em>headers: {Authorization: Bearer <your_token_value>}</em>
5. Add extra payment: <br><b>POST</b> `127.0.0.1:8000/api/v1/mortgage/<mortgage_id>/add-extra-payment/`<br><em>headers: {Authorization: Bearer <your_token_value>}</em>
```json
{
    "amount": 70000,
    "date": "2021-10-04"
}
```
6. Check calculated payments: <br><b>GET</b> `127.0.0.1:8000/api/v1/mortgage/<mortgage_id>/payment/?page_size=100&page=1`<br><em>headers: {Authorization: Bearer <your_token_value>}</em>
## API structure
All endpoints description: `127.0.0.1:8000/swagger/`
## ⚠️ Usage
1. All `mortgage/` endpoints are available only for registered users.
2. User can only see mortgages that were created by himself.
3. After updating a mortgage (PUT, PATCH), payment schedule will be recalculated automatically. Also, all extra payments for this mortgage will be removed.
4. You can't CRUD payments directly via API -- use `calc-payment-schedule/` endpoint instead.
5. There are a few rules for adding extra payments `add-extra-payment/`: 
   - Extra payment's date should be bigger than first payment's date and lower than last payment's date.
   - Extra payment's amount should be less than previous payment's debt rest.
6. Access token expires in 1 hour, refresh token -- in 24 hours. Use `token/refresh/` to refresh the token. 
