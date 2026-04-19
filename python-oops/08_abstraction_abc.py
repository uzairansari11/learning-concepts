# ============================================================
# LESSON 8: Abstraction — ABC and @abstractmethod
# ============================================================
#
# ── WHAT IS ABSTRACTION? ─────────────────────────────────
#
#   Abstraction = hiding HOW something works and only exposing
#   WHAT it does (the interface).
#
#   You use a TV remote without knowing how infrared signals work.
#   You call list.sort() without knowing the Timsort algorithm.
#   That's abstraction — use the WHAT, ignore the HOW.
#
# ── WHAT IS AN ABSTRACT CLASS (ABC)? ────────────────────
#
#   An abstract class is a class that:
#     1. CANNOT be instantiated directly (you can't create it)
#     2. DEFINES a contract — a set of methods every subclass MUST implement
#     3. Can have both abstract methods AND regular concrete methods
#
#   Think of it as a LEGAL CONTRACT:
#     "Any class that inherits from me MUST implement these methods.
#      If you don't, Python will refuse to create your object."
#
# ── WHY USE ABC? ─────────────────────────────────────────
#
#   Without ABC:
#     class PaymentGateway:
#         def pay(self): pass    ← silently does nothing
#     class Stripe(PaymentGateway): pass   ← forgets to implement pay()
#     stripe = Stripe()
#     stripe.pay()   ← silently does nothing — no error until too late!
#
#   With ABC:
#     class PaymentGateway(ABC):
#         @abstractmethod
#         def pay(self): ...
#     class Stripe(PaymentGateway): pass   ← TypeError immediately on creation!
#     Stripe()  → TypeError: Can't instantiate abstract class Stripe
#                 with abstract method pay
#
#   ABC catches missing implementations AT CLASS CREATION TIME,
#   not at runtime when the method is finally called.
#
# ── WHEN TO USE ABC ──────────────────────────────────────
#
#   ✅ You're defining a plugin/strategy interface (payment, storage, auth)
#   ✅ Multiple teams/contributors will write implementations
#   ✅ You want compile-time-like safety in Python
#   ✅ You want to share some common methods while forcing others
#   ✅ You're building a framework that others extend
#
# ── WHEN NOT TO USE ABC ──────────────────────────────────
#
#   ❌ For simple single-use classes — overkill
#   ❌ When duck typing is sufficient (Lesson 7)
#   ❌ When all methods would be abstract (just use a Protocol instead)
#
# ── ABC vs Protocol (Python 3.8+) ────────────────────────
#
#   ABC  → explicit inheritance required (class Stripe(PaymentGateway))
#   Protocol → structural — any class with the right methods qualifies,
#              even without inheriting (better for duck-typing scenarios)
#
# ============================================================

from abc import ABC, abstractmethod


# ════════════════════════════════════════════════════════════
# PART 1 — Basic ABC with @abstractmethod
# ════════════════════════════════════════════════════════════

class PaymentGateway(ABC):
    """
    Abstract contract for all payment gateways.
    Any subclass MUST implement pay() and refund().
    """

    # @abstractmethod = subclass MUST override this
    # If it doesn't, Python raises TypeError when you try to create an object
    @abstractmethod
    def pay(self, amount: float) -> str:
        """Charge the customer the given amount."""
        ...   # ... or pass — body is irrelevant, never runs

    @abstractmethod
    def refund(self, amount: float) -> str:
        """Refund the customer the given amount."""
        ...

    # CONCRETE method — shared by all subclasses (not abstract)
    # Subclasses get this for free, no need to override
    def receipt(self, amount: float) -> str:
        return (
            f"[{self.__class__.__name__}] "
            f"Receipt: {amount:,.2f} PKR processed."
        )

    def validate_amount(self, amount: float):
        if amount <= 0:
            raise ValueError(f"Amount must be positive. Got: {amount}")


# ── Concrete Implementations ──────────────────────────────

class StripePayment(PaymentGateway):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def pay(self, amount: float) -> str:
        self.validate_amount(amount)     # inherited from ABC
        return f"Stripe charged {amount:,.2f} PKR (key: {self.api_key[:6]}...)"

    def refund(self, amount: float) -> str:
        self.validate_amount(amount)
        return f"Stripe refunded {amount:,.2f} PKR"


class JazzCashPayment(PaymentGateway):
    def __init__(self, phone: str):
        self.phone = phone

    def pay(self, amount: float) -> str:
        self.validate_amount(amount)
        return f"JazzCash charged {amount:,.2f} PKR to {self.phone}"

    def refund(self, amount: float) -> str:
        return f"JazzCash refunded {amount:,.2f} PKR to {self.phone}"


class CryptoPayment(PaymentGateway):
    def __init__(self, wallet: str):
        self.wallet = wallet

    def pay(self, amount: float) -> str:
        return f"Crypto transferred {amount:,.2f} USDT to {self.wallet[:8]}..."

    def refund(self, amount: float) -> str:
        return f"Crypto refunded {amount:,.2f} USDT to {self.wallet[:8]}..."


# ── Demo ─────────────────────────────────────────────────

print("── ABC Demo ──")

# CANNOT instantiate an abstract class
try:
    gw = PaymentGateway()
except TypeError as e:
    print(f"Error: {e}")
# TypeError: Can't instantiate abstract class PaymentGateway
# with abstract method pay, refund

# Concrete classes work fine
gateways: list[PaymentGateway] = [
    StripePayment("sk_live_abc123xyz"),
    JazzCashPayment("0300-1234567"),
    CryptoPayment("0xAbCdEf1234567890ABCD"),
]

for gw in gateways:
    print(gw.pay(5000))
    print(gw.refund(500))
    print(gw.receipt(5000))   # inherited concrete method
    print()


# ── Partial implementation → still abstract ───────────────

class IncompletePayment(PaymentGateway):
    def pay(self, amount: float) -> str:
        return "Paid"
    # refund() is NOT implemented!

try:
    bad = IncompletePayment()
except TypeError as e:
    print(f"Incomplete class error: {e}")
# TypeError: Can't instantiate abstract class IncompletePayment
# with abstract method refund


# ════════════════════════════════════════════════════════════
# PART 2 — Abstract Properties
# ════════════════════════════════════════════════════════════

print("\n── Abstract Properties ──")


class Shape(ABC):
    """Abstract base — all shapes must expose area and perimeter."""

    @property
    @abstractmethod
    def area(self) -> float:
        ...

    @property
    @abstractmethod
    def perimeter(self) -> float:
        ...

    # Concrete method using the abstract properties
    def summary(self) -> str:
        return (
            f"{self.__class__.__name__}: "
            f"area={self.area:.2f}, perimeter={self.perimeter:.2f}"
        )


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    @property
    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    @property
    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    @property
    def area(self) -> float:
        return self.side ** 2

    @property
    def perimeter(self) -> float:
        return 4 * self.side


for shape in [Circle(5), Square(4)]:
    print(shape.summary())
# Circle: area=78.54, perimeter=31.42
# Square: area=16.00, perimeter=16.00


# ════════════════════════════════════════════════════════════
# PART 3 — ABC vs Protocol (brief comparison)
# ════════════════════════════════════════════════════════════

print("\n── Protocol (structural typing) ──")

from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

# No need to inherit from Drawable — just have draw()
class Circle2:
    def draw(self) -> str: return "Drawing a circle"

class Square2:
    def draw(self) -> str: return "Drawing a square"

class Car:   # completely unrelated — but has draw()
    def draw(self) -> str: return "Drawing a car"


def render(item: Drawable):
    print(item.draw())

# All three work — no inheritance needed
render(Circle2())   # Drawing a circle
render(Square2())   # Drawing a square
render(Car())       # Drawing a car

# ABC  → "you must explicitly sign the contract"
# Protocol → "if you have the right methods, you qualify automatically"


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Forgetting @abstractmethod → method exists but is empty
#   class Gateway(ABC):
#       def pay(self): pass      ← NOT abstract! Subclass can skip it.
#   Always add @abstractmethod to enforce it.
#
# MISTAKE 2: Wrong order for abstract property
#   @abstractmethod
#   @property           ← WRONG ORDER
#
#   Correct:
#   @property
#   @abstractmethod     ← property decorator FIRST


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Abstraction = expose WHAT, hide HOW
# 2. ABC cannot be instantiated — it's a contract only
# 3. @abstractmethod forces every subclass to implement that method
# 4. If a subclass misses any abstract method → TypeError on creation
# 5. ABC can have concrete methods shared by all subclasses
# 6. Abstract property: @property then @abstractmethod (order matters)
# 7. ABC = explicit inheritance contract; Protocol = structural/duck-typing
