"""
About the code:
- `users` - list of users (define them yourself)
- `command()` - simple function mimicking business logic
- `auth()` - decorator that requires user authorization to execute tasks

users = [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"},
            {"username": "jack", "password": "qwe123"}
        ]
"""
import functools


class Price:
    """Class for working with monetary amounts and currencies"""
    EXCHANGE_RATES = {
        "USD": {"CHF": 0.9},
        "EUR": {"CHF": 1.1},
        "CHF": {"USD": 1.1, "EUR": 0.9}
    }

    SUPPORTED_CURRENCIES = EXCHANGE_RATES.keys()

    def __init__(self, amount: float, currency: str):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        currency = currency.upper()
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        self.amount = amount
        self.currency = currency

    def _convert_to(self, target_currency: str, visited=None) -> 'Price':
        target_currency = target_currency.upper()
        visited = visited or set()

        if self.currency == target_currency:
            return self

        if self.currency in visited:
            raise ValueError(f"Conversion loop detected for currency: {self.currency}")
        visited.add(self.currency)

        # Direct conversion is possible
        if target_currency in self.EXCHANGE_RATES.get(self.currency, {}):
            rate = self.EXCHANGE_RATES[self.currency][target_currency]
            return Price(self.amount * rate, target_currency)

        # Try to convert via intermediate currencies
        for intermediate_currency in self.EXCHANGE_RATES.get(self.currency, {}):
            try:
                intermediate_price = Price(self.amount * self.EXCHANGE_RATES[self.currency][intermediate_currency],
                                           intermediate_currency)
                return intermediate_price._convert_to(target_currency, visited)
            except ValueError:
                continue  # Try the next route

        raise ValueError(f"Conversion path from {self.currency} to {target_currency} not found")

    def __add__(self, other: 'Price') -> 'Price':
        if self.currency != other.currency:
            converted = other._convert_to(self.currency)
            return Price(self.amount + converted.amount, self.currency)
        return Price(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Price') -> 'Price':
        if self.currency != other.currency:
            converted = other._convert_to(self.currency)
        else:
            converted = other
        result = self.amount - converted.amount
        if result < 0:
            raise ValueError("Resulting amount cannot be negative.")
        return Price(result, self.currency)

    def __repr__(self):
        return f"{round(self.amount, 2)} {self.currency}"


class AuthDecorator:
    """Decorator for authorization checking"""

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
                print(f"Authenticated as: {self.authenticated_user['username']}")
                return func(*args, **kwargs)

            while True:
                print("\nAuthorization required")
                username = input("Username: ")
                password = input("Password: ")

                user = next((u for u in self.users
                             if u["username"] == username and u["password"] == password), None)

                if user:
                    self.authenticated_user = user
                    print(f"Welcome, {username}!")
                    return func(*args, **kwargs)
                print("Error: Invalid credentials")
        return wrapper


# Create decorator instance
auth = AuthDecorator()


@auth
def calculate_prices():
    """Price calculation function requiring authorization"""
    print("\nAvailable currencies: USD, EUR, CHF")
    try:
        a = Price(float(input("Amount 1: ")), input("Currency 1: "))
        b = Price(float(input("Amount 2: ")), input("Currency 2: "))

        print(f"\n{a} + {b} = {a + b}")
        print(f"{a} - {b} = {a - b}")
    except Exception as e:
        print(f"Error: {e}")


@auth
def show_balance():
    """Another protected function"""
    print(f"\nCurrent balance: {Price(1000, 'USD')}")


# Main menu
def main():
    while True:
        print("\n1: Price calculator")
        print("2: Show balance")
        print("3: Exit")
        choice = input("Select action: ")

        if choice == "1":
            calculate_prices()
        elif choice == "2":
            show_balance()
        elif choice == "3":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
