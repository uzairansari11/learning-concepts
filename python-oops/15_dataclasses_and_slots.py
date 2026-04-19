# ============================================================
# LESSON 15: Dataclasses & __slots__
# ============================================================
#
# ── WHAT IS @dataclass? ──────────────────────────────────
#
#   @dataclass is a decorator (Python 3.7+) that automatically
#   generates boilerplate methods for data-holding classes:
#
#     __init__   → so you don't write it manually
#     __repr__   → clean string representation
#     __eq__     → compare two instances field by field
#     __hash__   → (optional) so it can be used as dict key
#     __lt__, __le__, etc. → (optional) sorting support
#
#   It's NOT magic — it just reads your type-annotated class
#   variables and generates those methods for you.
#
# ── WHY DOES @dataclass EXIST? ───────────────────────────
#
#   Without it, a simple data class like:
#     class Point:
#         x: float
#         y: float
#
#   needs you to write:
#     def __init__(self, x, y): self.x=x; self.y=y
#     def __repr__(self): return f"Point({self.x}, {self.y})"
#     def __eq__(self, other): return self.x==other.x and self.y==other.y
#
#   That's 5 lines for every 2 fields.
#   In a class with 10 fields, that's 25+ lines of pure boilerplate.
#   @dataclass generates all of it from 3 lines.
#
# ── WHEN TO USE @dataclass ───────────────────────────────
#
#   ✅ Classes that primarily hold data (DTOs, config, records)
#   ✅ When you need __eq__ and __repr__ without writing them
#   ✅ API response models, database row models
#   ✅ Value objects in domain-driven design
#
# ── WHEN NOT TO USE @dataclass ───────────────────────────
#
#   ❌ Classes with complex behaviour (many non-trivial methods)
#   ❌ When you need a custom __init__ with complex logic
#      (use __post_init__ instead if possible)
#   ❌ When the class is more behaviour than data
#
# ── WHAT IS __slots__? ───────────────────────────────────
#
#   By default, every Python instance stores its attributes in
#   a dynamic dictionary (obj.__dict__).
#   This is flexible but costs memory and is slightly slower.
#
#   __slots__ = ("x", "y") tells Python:
#     "This class will ONLY EVER have these attributes.
#      Don't create __dict__ — use fixed slot descriptors instead."
#
#   Benefits:
#     ✅ ~40-50% less memory per instance
#     ✅ ~20-30% faster attribute access
#     ✅ Prevents accidental attribute creation
#
#   Cost:
#     ❌ No dynamic attributes (obj.new_attr = x fails)
#     ❌ Slightly harder to use with multiple inheritance
#     ❌ No __dict__ unless you add it to __slots__
#
# ── WHEN TO USE __slots__ ────────────────────────────────
#
#   ✅ You create MILLIONS of instances (nodes, coordinates, packets)
#   ✅ Memory is critical (embedded, large-scale data pipelines)
#   ✅ Attribute set is fixed and well-known
#
# ── WHEN NOT TO USE __slots__ ────────────────────────────
#
#   ❌ For regular application code — premature optimisation
#   ❌ When you need dynamic attributes
#   ❌ With complex multiple inheritance (tricky to set up correctly)
#
# ============================================================

from dataclasses import dataclass, field, asdict, astuple, replace
from typing import ClassVar


# ════════════════════════════════════════════════════════════
# PART 1 — Basic @dataclass
# ════════════════════════════════════════════════════════════

print("── Basic @dataclass ──")


@dataclass
class Point:
    x: float
    y: float

# Generated automatically: __init__, __repr__, __eq__

p1 = Point(3.0, 4.0)
p2 = Point(3.0, 4.0)
p3 = Point(1.0, 2.0)

print(p1)             # Point(x=3.0, y=4.0)     ← __repr__
print(p1 == p2)       # True                     ← __eq__ (field-by-field)
print(p1 == p3)       # False
print(p1 is p2)       # False (different objects)


# ════════════════════════════════════════════════════════════
# PART 2 — Defaults, field(), ClassVar, __post_init__
# ════════════════════════════════════════════════════════════

print("\n── @dataclass with defaults and validation ──")


@dataclass
class Product:
    # Required fields first
    name:     str
    price:    float

    # Fields with defaults — must come AFTER required fields
    category: str         = "General"
    in_stock:  bool       = True

    # Mutable default MUST use field(default_factory=...)
    # Never use: tags: list = []  ← shared across all instances!
    tags: list[str]       = field(default_factory=list)

    # ClassVar → NOT a dataclass field, just a class variable
    _created_count: ClassVar[int] = 0

    def __post_init__(self):
        # Runs right after __init__ — use for validation and transformation
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")
        # Normalise name
        self.name = self.name.strip().title()
        Product._created_count += 1

    @classmethod
    def count(cls) -> int:
        return cls._created_count

    def apply_discount(self, percent: float) -> "Product":
        # replace() creates a NEW instance with changed fields
        # (like immutable update — doesn't mutate original)
        new_price = self.price * (1 - percent / 100)
        return replace(self, price=round(new_price, 2))


p = Product("  laptop  ", 150_000, tags=["tech", "sale"])
print(p)
# Product(name='Laptop', price=150000, category='General', in_stock=True, tags=['tech', 'sale'])

print(p.name)          # Laptop  (normalised in __post_init__)
print(Product.count()) # 1

# Utility functions from dataclasses module
print(asdict(p))       # {'name': 'Laptop', 'price': 150000, ...}
print(astuple(p))      # ('Laptop', 150000, 'General', True, ['tech', 'sale'])

# replace() — immutable-style update
discounted = p.apply_discount(20)
print(discounted.price)   # 120000.0
print(p.price)            # 150000  ← original unchanged

# Validation
try:
    Product("Bad", -100)
except ValueError as e:
    print(e)   # Price cannot be negative: -100


# ════════════════════════════════════════════════════════════
# PART 3 — frozen=True (immutable dataclass)
# ════════════════════════════════════════════════════════════

print("\n── frozen=True (immutable + hashable) ──")


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lng: float
    label: str = ""

    def distance_to_origin(self) -> float:
        return (self.lat ** 2 + self.lng ** 2) ** 0.5


karachi = Coordinate(24.8607, 67.0011, "Karachi")
lahore  = Coordinate(31.5204, 74.3587, "Lahore")

print(karachi)                          # Coordinate(lat=24.8607, ...)
print(karachi.distance_to_origin())

# Immutable — cannot change fields
try:
    karachi.lat = 0.0
except Exception as e:
    print(f"Error: {e}")               # cannot assign to field 'lat'

# Frozen = hashable → usable as dict key or set member
locations = {karachi: "Port city", lahore: "Cultural capital"}
print(locations[Coordinate(24.8607, 67.0011, "Karachi")])  # Port city

location_set = {karachi, lahore}
print(len(location_set))   # 2


# ════════════════════════════════════════════════════════════
# PART 4 — order=True (sortable records)
# ════════════════════════════════════════════════════════════

print("\n── order=True (sorting support) ──")


@dataclass(order=True)
class Version:
    # Comparison is field-by-field in declaration order
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


versions = [Version(1, 10, 0), Version(2, 0, 0), Version(1, 9, 5), Version(1, 10, 1)]
print([str(v) for v in sorted(versions)])
# ['1.9.5', '1.10.0', '1.10.1', '2.0.0']

print(Version(2, 0, 0) > Version(1, 9, 9))   # True
print(min(versions))   # Version(major=1, minor=9, patch=5)


# ════════════════════════════════════════════════════════════
# PART 5 — __slots__ (memory optimisation)
# ════════════════════════════════════════════════════════════

print("\n── __slots__ vs regular class ──")


class NormalPoint:
    """Regular class — uses __dict__ for attribute storage."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class SlottedPoint:
    """Slotted class — NO __dict__, uses fixed descriptors."""
    __slots__ = ("x", "y")   # declare ONLY allowed attributes

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


n = NormalPoint(1.0, 2.0)
s = SlottedPoint(1.0, 2.0)

print(n.x, n.y)    # 1.0  2.0
print(s.x, s.y)    # 1.0  2.0

# Normal class allows new attributes at runtime
n.z = 99
print(n.z)         # 99

# Slotted class blocks undeclared attributes
try:
    s.z = 99
except AttributeError as e:
    print(e)       # 'SlottedPoint' object has no attribute 'z'

# Memory comparison
import sys
print(f"Normal __dict__ size: {sys.getsizeof(n.__dict__)} bytes")
# Normal __dict__ size: ~200 bytes

# Slotted has no __dict__
print(hasattr(s, '__dict__'))   # False

# Rough per-object size
print(f"Normal  object: {sys.getsizeof(n)} bytes")
print(f"Slotted object: {sys.getsizeof(s)} bytes")
# Slotted is ~40-50 bytes smaller per object


# ════════════════════════════════════════════════════════════
# PART 6 — @dataclass(slots=True) — Python 3.10+
# ════════════════════════════════════════════════════════════

print("\n── @dataclass(slots=True) — best of both worlds ──")


@dataclass(slots=True, frozen=True)
class Pixel:
    """High-volume object: slots for memory, frozen for safety."""
    x: int
    y: int
    r: int = 0
    g: int = 0
    b: int = 0

    def __str__(self):
        return f"Pixel({self.x},{self.y}) rgb({self.r},{self.g},{self.b})"


px = Pixel(100, 200, r=255, g=128, b=0)
print(px)                      # Pixel(100,200) rgb(255,128,0)
print(hash(px))                # hashable (frozen=True)
print(hasattr(px, '__dict__')) # False (slots=True)

# Create 1 million pixels efficiently
import time
start = time.time()
pixels = [Pixel(i % 1920, i // 1920) for i in range(1_920_000)]
elapsed = time.time() - start
print(f"Created 1.92M Pixels in {elapsed:.2f}s")


# ════════════════════════════════════════════════════════════
# PART 7 — Inheritance with __slots__
# ════════════════════════════════════════════════════════════

print("\n── Slots + Inheritance ──")


class Base:
    __slots__ = ("x",)

    def __init__(self, x):
        self.x = x


class Child(Base):
    # MUST declare __slots__ in child too — only NEW attributes
    # Inherited slots (x) are handled by parent
    __slots__ = ("y",)

    def __init__(self, x, y):
        super().__init__(x)
        self.y = y


c = Child(1, 2)
print(c.x, c.y)   # 1  2
print(hasattr(c, '__dict__'))   # False  (truly slot-only)


# ════════════════════════════════════════════════════════════
# QUICK REFERENCE — @dataclass parameters
# ════════════════════════════════════════════════════════════
#
#   @dataclass(
#       init     = True,     generate __init__  (default: True)
#       repr     = True,     generate __repr__  (default: True)
#       eq       = True,     generate __eq__    (default: True)
#       order    = False,    generate __lt__, __le__, __gt__, __ge__
#       frozen   = False,    make immutable + hashable
#       slots    = False,    use __slots__ (Python 3.10+)
#       kw_only  = False,    all fields must be keyword-only (Py 3.10+)
#       match_args = True,   for structural pattern matching (Py 3.10+)
#   )
#
# field() parameters:
#   default          = value           simple default
#   default_factory  = list            factory called per instance
#   repr             = True/False      include in __repr__
#   compare          = True/False      include in __eq__ / __lt__
#   hash             = True/False      include in __hash__
#   init             = True/False      include in __init__
#   metadata         = {}              arbitrary metadata dict


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. @dataclass generates __init__, __repr__, __eq__ from annotations
# 2. field(default_factory=list) for mutable defaults (NEVER use = [])
# 3. __post_init__ runs after __init__ — use for validation
# 4. frozen=True → immutable + hashable (usable as dict key / set member)
# 5. order=True → adds all comparison operators for sorting
# 6. replace(obj, field=new_val) → immutable-style field update
# 7. __slots__ → removes __dict__, saves memory, blocks new attributes
# 8. slots=True on @dataclass → cleanest modern approach (Python 3.10+)
