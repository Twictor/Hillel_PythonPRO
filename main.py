from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import requests
import time
from typing import Dict, Tuple

app = FastAPI()
security = HTTPBasic()

# Конфигурация
API_KEY = 'RTQKBDMBWUCMIDFZ'
CACHE_TTL = 300  # 5 минут в секундах

# База данных пользователей
USERS = {
    "admin": "admin123",
    "user": "user123",
    "jack": "qwe123"
}

# Кеш курсов валют
exchange_cache: Dict[Tuple[str, str], Tuple[float, float]] = {}


class PriceRequest(BaseModel):
    amount1: float
    currency1: str
    amount2: float
    currency2: str


class PriceResponse(BaseModel):
    addition: str
    subtraction: str


def get_exchange_rate(from_curr: str, to_curr: str) -> float:
    if from_curr == to_curr:
        return 1.0

    cache_key = (from_curr, to_curr)
    now = time.time()

    # Проверка кеша
    if cache_key in exchange_cache:
        rate, timestamp = exchange_cache[cache_key]
        if now - timestamp < CACHE_TTL:
            return rate

    # Запрос к API
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_curr}&to_currency={to_curr}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        exchange_cache[cache_key] = (rate, now)
        return rate
    except Exception as e:
        raise ValueError(f"Ошибка получения курса: {e}")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in USERS or USERS[credentials.username] != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/calculate")
def calculate(request: PriceRequest, username: str = Depends(authenticate)):
    try:
        # Конвертация в CHF
        amount1_chf = request.amount1 * get_exchange_rate(request.currency1.upper(), "CHF")
        amount2_chf = request.amount2 * get_exchange_rate(request.currency2.upper(), "CHF")

        # Вычисления
        add_chf = amount1_chf + amount2_chf
        sub_chf = amount1_chf - amount2_chf

        # Конвертация обратно
        add_result = add_chf * get_exchange_rate("CHF", request.currency1.upper())
        sub_result = sub_chf * get_exchange_rate("CHF", request.currency1.upper())

        return PriceResponse(
            addition=f"{round(add_result, 2)} {request.currency1}",
            subtraction=f"{round(sub_result, 2)} {request.currency1}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/balance")
def balance(username: str = Depends(authenticate)):
    return {"balance": "1000 USD"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)