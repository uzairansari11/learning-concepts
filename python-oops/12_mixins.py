# ============================================================
# LESSON 12: Mixins
# ============================================================
#
# ── WHAT IS A MIXIN? ─────────────────────────────────────
#
#   A Mixin is a small, focused class designed to be MIXED INTO
#   other classes to ADD a specific, reusable piece of behaviour.
#
#   It is NOT a standalone class — it's never used on its own.
#   It does NOT represent a real-world entity.
#   It just packages ONE behaviour cleanly.
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   Think of MODULAR FURNITURE — IKEA-style:
#     - A shelf unit (the main class)
#     - A drawer module (a Mixin)
#     - A glass-door module (another Mixin)
#     - A lighting module (another Mixin)
#
#   You snap on whichever modules you need.
#   The modules don't know about each other.
#   The shelf unit gains new features by composition.
#
# ── HOW IS MIXIN DIFFERENT FROM REGULAR INHERITANCE? ────
#
#   Regular Inheritance → IS-A relationship, semantic meaning
#     class Dog(Animal):   Dog IS-A Animal — makes real sense
#
#   Mixin → ADD behaviour, no IS-A meaning
#     class User(LogMixin, SerializeMixin):
#     User is NOT a LogMixin. It just gets logging for free.
#
# ── HOW IS MIXIN DIFFERENT FROM COMPOSITION? ────────────
#
#   Composition  → HAS-A, separate object, method delegation
#     self.logger = Logger()
#     self.logger.log("...")   ← explicit call
#
#   Mixin → method directly on the class, transparent to caller
#     user.log("...")          ← looks like it's user's own method
#
# ── RULES FOR A GOOD MIXIN ───────────────────────────────
#
#   1. No __init__ (or a minimal one that calls super())
#      → doesn't own state, just adds methods
#   2. Never instantiated directly — only used as a base
#   3. Focused on ONE concern (logging, serialization, validation)
#   4. Named with "Mixin" suffix → clear intent
#   5. Placed BEFORE the real parent class in the class definition
#      class User(LogMixin, SerializeMixin, BaseModel):
#             ↑ mixins first          ↑ real parent last
#
# ── WHEN TO USE MIXINS ───────────────────────────────────
#
#   ✅ Adding cross-cutting concerns (logging, caching, validation)
#   ✅ The same behaviour is needed in UNRELATED classes
#      (User and Product both need logging — they share no parent)
#   ✅ You don't want to couple the classes with a common ancestor
#   ✅ Building frameworks and reusable component libraries
#
# ── WHEN NOT TO USE MIXINS ───────────────────────────────
#
#   ❌ If the behaviour IS the class identity → use inheritance
#   ❌ If the Mixin carries significant state → use composition
#   ❌ If you're using too many Mixins per class (>3-4) → reconsider
#   ❌ If the method name might clash with another Mixin or parent
#
# ── MIXIN vs DECORATOR ───────────────────────────────────
#
#   Decorator wraps a class and modifies it externally.
#   Mixin is mixed in at class definition — part of the MRO.
#   Both add behaviour, but Mixin is more natural for OOP hierarchies.
#
# ============================================================


# ════════════════════════════════════════════════════════════
# MIXIN LIBRARY — reusable, focused behaviours
# ════════════════════════════════════════════════════════════

class LogMixin:
    """Adds structured logging to any class.  No state of its own."""

    def log(self, message: str, level: str = "INFO"):
        # self.__class__.__name__ → gives the ACTUAL class name, not LogMixin
        print(f"[{level}] {self.__class__.__name__}: {message}")

    def log_error(self, message: str):
        self.log(message, level="ERROR")

    def log_warning(self, message: str):
        self.log(message, level="WARN")


class SerializeMixin:
    """Adds JSON-like serialization and deserialization."""

    def to_dict(self) -> dict:
        # Only public attributes (skip _ and __ prefixed ones)
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    def to_string(self) -> str:
        return str(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruct an object from a dictionary."""
        obj = cls.__new__(cls)
        obj.__dict__.update(data)
        return obj


class ValidateMixin:
    """Validates that required fields are present and non-empty."""

    _required_fields: list[str] = []   # subclass declares these

    def validate(self) -> bool:
        for field in self._required_fields:
            value = getattr(self, field, None)
            if value is None or value == "":
                raise ValueError(
                    f"[{self.__class__.__name__}] "
                    f"Required field '{field}' is missing or empty."
                )
        return True


class ReprMixin:
    """Auto-generates __repr__ from all public instance attributes."""

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"


class ComparableMixin:
    """Adds full comparison support. Subclass must define _compare_key."""

    def _compare_key(self):
        raise NotImplementedError("Define _compare_key() to enable comparison")

    def __eq__(self, other):
        if type(self) != type(other): return NotImplemented
        return self._compare_key() == other._compare_key()

    def __lt__(self, other):
        return self._compare_key() < other._compare_key()

    def __le__(self, other):
        return self._compare_key() <= other._compare_key()

    def __gt__(self, other):
        return self._compare_key() > other._compare_key()

    def __ge__(self, other):
        return self._compare_key() >= other._compare_key()

    def __hash__(self):
        return hash(self._compare_key())


# ════════════════════════════════════════════════════════════
# CLASSES USING MIXINS
# ════════════════════════════════════════════════════════════

# Order: Mixins first (left) → real parent last (right)
# This ensures MRO resolves Mixin methods before parent methods

class User(LogMixin, SerializeMixin, ValidateMixin, ReprMixin):
    _required_fields = ["name", "email"]

    def __init__(self, name: str, email: str, age: int):
        self.name  = name
        self.email = email
        self.age   = age

    def greet(self) -> str:
        return f"Hello, I am {self.name}!"


class Product(LogMixin, SerializeMixin, ReprMixin, ComparableMixin):
    def __init__(self, title: str, price: float, stock: int):
        self.title = title
        self.price = price
        self.stock = stock

    def _compare_key(self):
        return self.price   # products compared by price

    def buy(self, qty: int = 1):
        if qty > self.stock:
            self.log_warning(f"Requested {qty} but only {self.stock} in stock")
            return
        self.stock -= qty
        self.log(f"Sold {qty}x '{self.title}'. Remaining: {self.stock}")


class Order(LogMixin, SerializeMixin, ValidateMixin, ReprMixin):
    _required_fields = ["order_id", "customer"]

    def __init__(self, order_id: str, customer: str, total: float):
        self.order_id = order_id
        self.customer = customer
        self.total    = total

    def process(self):
        self.validate()
        self.log(f"Processing order {self.order_id} for {self.customer}")
        return f"Order {self.order_id} processed successfully"


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

print("── User with Mixins ──")
user = User("Uzair", "uzair@example.com", 25)

user.log("User created")              # [INFO] User: User created
user.log_warning("Weak password")     # [WARN] User: Weak password

print(repr(user))                     # User(name='Uzair', email=..., age=25)
print(user.to_dict())                 # {'name': 'Uzair', 'email': ..., 'age': 25}
print(user.to_string())
print(user.validate())                # True
print(user.greet())                   # Hello, I am Uzair!


print("\n── Product with Mixins ──")
p1 = Product("Laptop",  150_000, 10)
p2 = Product("Monitor",  45_000, 5)
p3 = Product("Mouse",     3_500, 50)

p1.buy(2)                             # [INFO] Product: Sold 2x...
p1.buy(15)                            # [WARN] Product: Requested 15 but only 8 in stock

print(repr(p1))
print(p1.to_dict())

# ComparableMixin — compare and sort products
print(p1 > p2)                        # True (150000 > 45000)
print(p3 < p2)                        # True (3500 < 45000)

products = [p1, p2, p3]
for p in sorted(products):            # uses __lt__ from ComparableMixin
    print(f"  {p.title}: {p.price:,}")
# Mouse: 3,500 / Monitor: 45,000 / Laptop: 150,000


print("\n── Order with Mixins ──")
order = Order("ORD-001", "Uzair", 153_500)
print(order.process())
print(order.to_dict())


print("\n── Validation failure ──")
try:
    bad = User("", "bad@mail.com", 20)
    bad.validate()
except ValueError as e:
    print(e)


print("\n── Serialise → reconstruct ──")
user_dict = user.to_dict()
user2 = User.from_dict(user_dict)    # from_dict from SerializeMixin
print(repr(user2))


print("\n── MRO for User ──")
print([c.__name__ for c in User.__mro__])
# ['User', 'LogMixin', 'SerializeMixin', 'ValidateMixin', 'ReprMixin', 'object']


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Mixin with state (heavy __init__)
#   class LogMixin:
#       def __init__(self):
#           self.log_history = []   ← now LogMixin owns state
#   This creates MRO complications. Keep Mixins stateless.
#
# MISTAKE 2: Mixin placed AFTER the real parent
#   class User(BaseModel, LogMixin):   ← LogMixin may be shadowed
#   Always: class User(LogMixin, BaseModel)   ← Mixins first
#
# MISTAKE 3: Mixin method name clashes
#   If LogMixin.log() and SerializeMixin.log() both exist,
#   MRO order decides which wins — naming conflicts are subtle bugs.
#   Use unique, descriptive method names in Mixins.


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Mixin = focused, reusable behaviour class — not a standalone entity
# 2. Rules: no __init__ state, never instantiated alone, single concern
# 3. Name with "Mixin" suffix for clarity
# 4. Place Mixins BEFORE the real parent in class(...) definition
# 5. Mixins + MRO → each method resolved in left-to-right order
# 6. Use for cross-cutting concerns: logging, serialization, validation
# 7. Mixin vs Composition: Mixin feels native; composition is explicit
