"""
About the code:
users = [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"},
            {"username": "jack", "password": "qwe123"}
        ]
"""


import functools
import requests
import time
from typing import Dict, Tuple


class Price:
    _exchange_rate_cache: Dict[Tuple[str, str], Tuple[float, float]] = {}  # (from, to) -> (rate, timestamp)
    _CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, amount: float, currency: str):
        self.amount = round(float(amount), 2)
        self.currency = currency.upper()

    def __add__(self, other: 'Price') -> 'Price':
        return self._perform_operation(other, operation='add')

    def __sub__(self, other: 'Price') -> 'Price':
        return self._perform_operation(other, operation='sub')

    def _perform_operation(self, other: 'Price', operation: str) -> 'Price':
        if not isinstance(other, Price):
            raise TypeError("Operands must be instances of Price")

        if self.currency == other.currency:
            new_amount = (
                self.amount + other.amount
                if operation == 'add'
                else self.amount - other.amount
            )
            if operation == 'sub' and new_amount < 0:
                raise ValueError("Resulting amount cannot be negative.")
            return Price(round(new_amount, 2), self.currency)

        # Conversion via CHF
        self_in_chf = self._convert_to_chf()
        other_in_chf = other._convert_to_chf()

        result_in_chf = (
            self_in_chf + other_in_chf
            if operation == 'add'
            else self_in_chf - other_in_chf
        )

        if operation == 'sub' and result_in_chf < 0:
            raise ValueError("Resulting amount cannot be negative.")

        return self._convert_from_chf(result_in_chf)

    def _convert_to_chf(self) -> float:
        if self.currency == 'CHF':
            return self.amount
        rate = self._get_exchange_rate(self.currency, 'CHF')
        return round(self.amount * rate, 4)

    def _convert_from_chf(self, amount_in_chf: float) -> 'Price':
        if self.currency == 'CHF':
            return Price(round(amount_in_chf, 2), self.currency)
        rate = self._get_exchange_rate('CHF', self.currency)
        return Price(round(amount_in_chf * rate, 2), self.currency)

    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0

        cache_key = (from_currency, to_currency)
        current_time = time.time()

        # Check cache
        if cache_key in self._exchange_rate_cache:
            rate, timestamp = self._exchange_rate_cache[cache_key]
            if current_time - timestamp < self._CACHE_TTL_SECONDS:
                return rate

        # API request
        api_key = 'RTQKBDMBWUCMIDFZ'
        url = (
            f'https://www.alphavantage.co/query?'
            f'function=CURRENCY_EXCHANGE_RATE&'
            f'from_currency={from_currency}&to_currency={to_currency}&apikey={api_key}'
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Check HTTP errors
            data = response.json()

            if "Realtime Currency Exchange Rate" not in data:
                raise ValueError(f"API didn't return exchange rate. Response: {data}")

            rate_str = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
            rate = float(rate_str)

            # Update cache
            self._exchange_rate_cache[cache_key] = (rate, current_time)
            return rate

        except (requests.RequestException, KeyError, ValueError) as e:
            raise ValueError(
                f"Failed to get exchange rate {from_currency} → {to_currency}: {str(e)}"
            )

    def __repr__(self):
        return f"Price({self.amount}, '{self.currency}')"


class AuthDecorator:
    """Decorator for user authentication"""

    def __init__(self):
        self.users = [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"},
            {"username": "jack", "password": "qwe123"}
        ]
        self.authenticated_user = None

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.authenticated_user:
                print(f"\n[Authenticated as: {self.authenticated_user['username']}]")
                return func(*args, **kwargs)

            while True:
                print("\n Authentication required:")
                username = input("Username: ")
                password = input("Password: ")

                user = next(
                    (u for u in self.users
                     if u["username"] == username and u["password"] == password),
                    None
                )

                if user:
                    self.authenticated_user = user
                    print(f"Welcome, {username}!")
                    return func(*args, **kwargs)

                print("Invalid credentials")

        return wrapper


# Create decorator instance
auth = AuthDecorator()


@auth
def calculate_prices():
    """Function for price calculations (with authentication)"""
    print("\n Available currencies: USD, EUR, CHF, UAH, etc.")
    try:
        a = Price(float(input("Enter amount 1: ")), input("Enter currency 1 (e.g. USD): "))
        b = Price(float(input("Enter amount 2: ")), input("Enter currency 2 (e.g. EUR): "))

        print(f"\n {a} + {b} = {a + b}")
        print(f" {a} - {b} = {a - b}")
    except Exception as e:
        print(f"Error: {e}")


@auth
def show_balance():
    """Example of another protected function"""
    print(f"\n Balance: {Price(1000, 'USD')}")


def main():
    while True:
        print("\n====== MENU ======")
        print("1: Price Calculator")
        print("2: Show Balance")
        print("3: Exit")
        choice = input("Select action: ")

        if choice == "1":
            calculate_prices()
        elif choice == "2":
            show_balance()
        elif choice == "3":
            print("Exiting program")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
