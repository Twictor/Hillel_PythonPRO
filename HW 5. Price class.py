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

class Price:
    """Class for working with monetary amounts and currencies"""
    EXCHANGE_RATES = {
        "USD": {"CHF": 0.9},
        "EUR": {"CHF": 1.1},
        "CHF": {"USD": 1.1, "EUR": 0.9}
    }

    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency.upper()

    def _convert_to(self, target_currency: str) -> 'Price':
        if self.currency == target_currency:
            return self

        if target_currency not in self.EXCHANGE_RATES.get(self.currency, {}):
            chf = self._convert_to("CHF")
            return chf._convert_to(target_currency)

        rate = self.EXCHANGE_RATES[self.currency][target_currency]
        return Price(self.amount * rate, target_currency)

    def __add__(self, other: 'Price') -> 'Price':
        if self.currency != other.currency:
            converted = other._convert_to(self.currency)
            return Price(self.amount + converted.amount, self.currency)
        return Price(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Price') -> 'Price':
        if self.currency != other.currency:
            converted = other._convert_to(self.currency)
            return Price(self.amount - converted.amount, self.currency)
        return Price(self.amount - other.amount, self.currency)

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
    a = Price(float(input("Amount 1: ")), input("Currency 1: ").upper())
    b = Price(float(input("Amount 2: ")), input("Currency 2: ").upper())

    print(f"\n{a} + {b} = {a + b}")
    print(f"{a} - {b} = {a - b}")


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
