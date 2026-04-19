# ============================================================
# LESSON 13: Descriptors
# ============================================================
#
# ── WHAT IS A DESCRIPTOR? ────────────────────────────────
#
#   A Descriptor is an object that CONTROLS how attribute
#   access (get, set, delete) works on ANOTHER class.
#
#   When you write:   obj.attr
#   Python normally just looks up attr in obj.__dict__.
#   With a descriptor, Python calls a METHOD instead.
#
#   Three hooks:
#     __get__(self, obj, objtype)  → called on READ   (obj.attr)
#     __set__(self, obj, value)    → called on WRITE  (obj.attr = val)
#     __delete__(self, obj)        → called on DELETE (del obj.attr)
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   A descriptor is like a SECURITY GUARD for an attribute:
#     - Someone wants to READ the file   → guard checks ID, then grants access
#     - Someone wants to WRITE a file    → guard validates content, then stores
#     - Someone wants to DELETE a file   → guard logs the action, then removes
#
#   The file (attribute) doesn't change — the GUARD (descriptor)
#   intercepts and controls the access.
#
# ── WHY DO DESCRIPTORS EXIST? ────────────────────────────
#
#   Problem:
#     Validation logic scattered everywhere:
#       product.price = -100   ← no one stops this
#
#   Option 1: @property — works but you must write getter/setter per attribute
#     @property
#     def price(self): return self._price
#     @price.setter
#     def price(self, v): ...
#     → 10 attributes = 30 lines of boilerplate × every class
#
#   Option 2: Descriptor — define validation ONCE, reuse everywhere
#     class PositiveNumber: __get__, __set__  ← defined once
#     class Product:
#         price = PositiveNumber()   ← applied in one line
#         stock = PositiveNumber()   ← same validation, no repeat
#
#   @property is actually a built-in descriptor itself!
#   Descriptors are HOW @property, @classmethod, @staticmethod work.
#
# ── TWO TYPES OF DESCRIPTORS ─────────────────────────────
#
#   DATA DESCRIPTOR → implements __set__ (and/or __delete__)
#     Takes PRIORITY over instance __dict__.
#     Attribute write/read always goes through the descriptor.
#     Use for: validation, type checking, computed attributes.
#
#   NON-DATA DESCRIPTOR → implements ONLY __get__
#     Instance __dict__ takes PRIORITY.
#     Once a value is stored in obj.__dict__, descriptor is bypassed.
#     Use for: caching/lazy computation (store result after first call).
#
# ── WHEN TO USE DESCRIPTORS ─────────────────────────────
#
#   ✅ Same validation logic needed on multiple attributes or classes
#   ✅ Building frameworks, ORMs, data models (like Django models)
#   ✅ Lazy/cached properties (compute once, cache on instance)
#   ✅ Type-enforcing attributes
#
# ── WHEN NOT TO USE DESCRIPTORS ─────────────────────────
#
#   ❌ For a single attribute on one class → @property is simpler
#   ❌ When @dataclass + field validators are enough
#   ❌ When the added complexity outweighs the reuse benefit
#
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 1 — Data Descriptor: Reusable Validator
# ════════════════════════════════════════════════════════════

class PositiveNumber:
    """
    DATA DESCRIPTOR — ensures the attribute is always a positive number.
    Can be reused on any attribute in any class.
    """

    def __set_name__(self, owner_class, attr_name):
        # Called automatically when the descriptor is assigned to a class.
        # owner_class = the class that has this descriptor (e.g. Product)
        # attr_name   = the name used in that class (e.g. 'price')
        self._attr   = attr_name
        # Store actual value under a different name to avoid recursion
        self._private = f"_{attr_name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Accessed on the CLASS itself (not an instance): Product.price
            # Return the descriptor object so callers can inspect it
            return self
        return getattr(obj, self._private, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"'{self._attr}' must be a number. Got: {type(value).__name__}"
            )
        if value <= 0:
            raise ValueError(
                f"'{self._attr}' must be positive. Got: {value}"
            )
        setattr(obj, self._private, value)

    def __delete__(self, obj):
        print(f"[Descriptor] Deleting '{self._attr}'")
        delattr(obj, self._private)


class StringField:
    """DATA DESCRIPTOR — ensures a non-empty string."""

    def __set_name__(self, owner_class, attr_name):
        self._attr    = attr_name
        self._private = f"_{attr_name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self._private, "")

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError(f"'{self._attr}' must be a string.")
        if not value.strip():
            raise ValueError(f"'{self._attr}' cannot be empty.")
        setattr(obj, self._private, value.strip())


# Using descriptors in a class — ONE LINE per validated attribute

class Product:
    # Descriptors as CLASS attributes — shared but control each instance
    name  = StringField()
    price = PositiveNumber()
    stock = PositiveNumber()

    def __init__(self, name: str, price: float, stock: int):
        # These assignments trigger __set__ on each descriptor
        self.name  = name    # → StringField.__set__
        self.price = price   # → PositiveNumber.__set__
        self.stock = stock   # → PositiveNumber.__set__

    def buy(self, qty: int = 1):
        if qty > self.stock:
            raise ValueError("Not enough stock")
        self.stock -= qty
        return f"Bought {qty}x {self.name}. Left: {self.stock}"

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price}, stock={self.stock})"


print("── Data Descriptor Demo ──")
p = Product("Laptop", 150_000, 10)
print(p)                   # Product(name='Laptop', price=150000, stock=10)

p.price = 120_000          # __set__ → valid
print(p.price)             # 120000  ← __get__

print(p.buy(3))            # Bought 3x Laptop. Left: 7

# Validation fires on bad input
try:
    p.price = -100
except ValueError as e:
    print(e)               # 'price' must be positive. Got: -100

try:
    p.stock = "ten"
except TypeError as e:
    print(e)               # 'stock' must be a number. Got: str

try:
    p.name = ""
except ValueError as e:
    print(e)               # 'name' cannot be empty.

# Accessing descriptor on the CLASS (not instance)
print(Product.price)       # <PositiveNumber object> — returns the descriptor itself

# Delete
del p.price                # [Descriptor] Deleting 'price'


# ════════════════════════════════════════════════════════════
# PART 2 — Non-Data Descriptor: Lazy/Cached Property
# ════════════════════════════════════════════════════════════
#
# Problem: computing area/circumference every access is wasteful
# if the radius never changes.
# Solution: compute ONCE, cache on the instance, return cached forever.

print("\n── Non-Data (Lazy) Descriptor ──")


class LazyProperty:
    """
    NON-DATA DESCRIPTOR — computes value on first access, caches it.
    Second access hits obj.__dict__ directly (faster, no descriptor call).
    """

    def __init__(self, func):
        self.func = func
        self.attr_name = None

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # First access: compute and store in INSTANCE dict
        # Subsequent accesses: instance dict takes priority (non-data descriptor)
        value = self.func(obj)
        obj.__dict__[self.attr_name] = value   # cache it
        print(f"  [LazyProperty] Computed {self.attr_name}")
        return value


class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    @LazyProperty
    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    @LazyProperty
    def circumference(self) -> float:
        return 2 * 3.14159 * self.radius


c = Circle(5)

# First access — computes and caches
print(c.area)           # [LazyProperty] Computed area → 78.53975

# Second access — goes straight to c.__dict__, descriptor NOT called
print(c.area)           # 78.53975  (no "Computed" message)

print(c.circumference)  # [LazyProperty] Computed circumference → 31.4159
print(c.circumference)  # 31.4159  (cached)

# Verify it's in __dict__ now
print(c.__dict__)       # {'radius': 5, 'area': 78.53975, 'circumference': 31.4159}


# ════════════════════════════════════════════════════════════
# PART 3 — Seeing how @property is just a descriptor
# ════════════════════════════════════════════════════════════

print("\n── @property under the hood ──")

# These two are EQUIVALENT:

class WithProperty:
    def __init__(self, val):
        self._val = val

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self, v):
        if v < 0: raise ValueError("No negatives")
        self._val = v


class WithDescriptor:
    class _ValueDescriptor:
        def __get__(self, obj, _): return obj._val if obj else self
        def __set__(self, obj, v):
            if v < 0: raise ValueError("No negatives")
            obj._val = v

    value = _ValueDescriptor()

    def __init__(self, val):
        self._val = val


a = WithProperty(10)
a.value = 20
print(a.value)       # 20

b = WithDescriptor(10)
b.value = 20
print(b.value)       # 20


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Not using __set_name__ → attr_name unknown
#   Must define __set_name__ so the descriptor knows its own name.
#   Without it, you can't build the private storage name.
#
# MISTAKE 2: Storing value on self (the descriptor), not obj
#   def __set__(self, obj, value):
#       self.value = value   ← WRONG: shared across ALL instances!
#   Correct:
#       setattr(obj, self._private, value)
#
# MISTAKE 3: Making a non-data descriptor for validation
#   If you only define __get__, the instance dict bypasses it on write.
#   Validation requires __set__ → must be a DATA descriptor.


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Descriptor = object that controls attribute get/set/delete
# 2. DATA descriptor (has __set__) → beats instance __dict__
# 3. NON-DATA descriptor (only __get__) → instance __dict__ beats it
# 4. __set_name__ tells the descriptor its attribute name
# 5. Store values on obj (instance), not self (descriptor) — else shared!
# 6. @property, @classmethod, @staticmethod are all descriptors
# 7. Use for: DRY validation, lazy caching, ORM field definitions
