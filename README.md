<h1 align="center" style="font-size: 3rem;">
MORTGAGE-API
</h1>
<p align="center">
 <em>REST API for calculating mortgage parametrs: payment schedule, bank percent, extra payments etc.</em></p>

---

## Run
1. Run mirations:
```shell
docker-compose run app python manage.py migrate
```
2. Run the app and the database:
```shell
docker-compose up
```
## Quiqstart
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
3. Create a mortgage:<br><b>POST</b> `127.0.0.1:8000/api/v1/mortgage/`<br>headers: {Authorization: Bearer <your_token_value>}
```json
{
    "percent": "8.20",
    "period": 25,
    "first_payment_amount": 2500000,
    "total_amount": 11000000,
    "issue_date": "2021-09-04"
}
```
4. Calculate mortgage schedule: <br><b>POST</b> `127.0.0.1:8000/api/v1/mortgage/<mortgage_id>/calc-payment-schedule/`<br>headers: {Authorization: Bearer <your_token_value>}
5. Check calculated payments: <br><b>GET</b> `127.0.0.1:8000/api/v1/mortgage/<mortgage_id>/payment/?page_size=100&page=1`<br>headers: {Authorization: Bearer <your_token_value>}