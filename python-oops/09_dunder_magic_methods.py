# ============================================================
# LESSON 9: Dunder / Magic Methods
# ============================================================
#
# ── WHAT ARE DUNDER METHODS? ─────────────────────────────
#
#   Dunder = "Double UNDERscore" → __method__
#   Also called "magic methods" or "special methods".
#
#   They are methods Python calls AUTOMATICALLY in response to:
#     - Built-in functions:  print(obj), len(obj), abs(obj)
#     - Operators:           obj1 + obj2, obj1 == obj2, obj[key]
#     - Language syntax:     with obj:, for x in obj:, if obj:
#
#   You never call them directly — Python calls them for you.
#
# ── WHY DO THEY EXIST? ───────────────────────────────────
#
#   Without dunder methods, your custom class is a black box.
#   print(obj)     → <__main__.Vector object at 0x7f...>  (useless)
#   obj1 + obj2    → TypeError: unsupported operand type
#   len(obj)       → TypeError: object of type 'X' has no len()
#
#   By implementing dunders, your objects behave like NATIVE types:
#     print(v)        → "Vector(3, 4)"
#     v1 + v2         → Vector(4, 6)
#     len(v)          → 2
#
# ── WHY THIS MATTERS ─────────────────────────────────────
#
#   Python's entire standard library is built around protocol-based
#   interfaces via dunder methods.
#   - for loops use __iter__ and __next__
#   - with statements use __enter__ and __exit__
#   - sorted() uses __lt__
#   - dict keys use __hash__ and __eq__
#
#   By implementing the right dunders, your class integrates
#   seamlessly with ALL Python built-ins and 3rd-party libraries.
#
# ── WHEN TO IMPLEMENT DUNDERS ────────────────────────────
#
#   ✅ __str__ / __repr__   → always — every class benefits
#   ✅ __eq__               → when == comparison makes sense
#   ✅ __lt__ etc.          → when sorting/ordering makes sense
#   ✅ __len__ / __iter__   → when your class represents a collection
#   ✅ __add__ etc.         → for math/domain objects (Vector, Money)
#   ✅ __enter__ / __exit__ → when your class manages a resource
#
# ── WHEN NOT TO ──────────────────────────────────────────
#
#   ❌ Don't implement __add__ just because you can — only when
#      addition is meaningful for the domain
#   ❌ Never call dunders directly: obj.__str__()  → use str(obj)
#   ❌ If you define __eq__, Python auto-disables __hash__ — remember
#      to define __hash__ too if you want dict keys / set members
#
# ============================================================


class Vector:
    """2D vector — demonstrates the most important dunders."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # ────────────────────────────────────────────────────
    # STRING REPRESENTATIONS
    # ────────────────────────────────────────────────────

    def __str__(self) -> str:
        # Called by: print(v), str(v), f-strings: f"{v}"
        # Purpose: human-readable, for display
        return f"Vector({self.x}, {self.y})"

    def __repr__(self) -> str:
        # Called by: repr(v), REPL output, inside containers like [v1, v2]
        # Purpose: unambiguous, ideally eval()-able
        # Rule: if possible, make repr() output recreate the object
        return f"Vector(x={self.x!r}, y={self.y!r})"

    # ────────────────────────────────────────────────────
    # ARITHMETIC OPERATORS
    # ────────────────────────────────────────────────────

    def __add__(self, other: "Vector") -> "Vector":
        # v1 + v2  → Python calls  v1.__add__(v2)
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        # v1 - v2
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        # v * 3  → Python calls  v.__mul__(3)
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        # 3 * v  → Python first tries  int.__mul__(v) → NotImplemented
        #          then falls back to   v.__rmul__(3)
        # Without __rmul__, "3 * v" would fail even though "v * 3" works
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector":
        # v / 2
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vector":
        # -v  (unary minus)
        return Vector(-self.x, -self.y)

    def __pos__(self) -> "Vector":
        # +v  (unary plus — usually returns a copy)
        return Vector(self.x, self.y)

    # ────────────────────────────────────────────────────
    # COMPARISON OPERATORS
    # ────────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        # v1 == v2
        # NOTE: defining __eq__ makes __hash__ = None automatically!
        # Define __hash__ below if you need vectors as dict keys.
        if not isinstance(other, Vector):
            return NotImplemented    # let Python try the other side
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: "Vector") -> bool:
        # v1 < v2 — compare by magnitude
        return abs(self) < abs(other)

    def __le__(self, other: "Vector") -> bool:
        return abs(self) <= abs(other)

    def __hash__(self) -> int:
        # Required if you define __eq__ and still want dict keys / set members
        return hash((self.x, self.y))

    # ────────────────────────────────────────────────────
    # BUILT-IN FUNCTION HOOKS
    # ────────────────────────────────────────────────────

    def __abs__(self) -> float:
        # abs(v) → magnitude/length of vector: sqrt(x²+y²)
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __bool__(self) -> bool:
        # bool(v) / if v:
        # False only for the zero vector (0, 0)
        return self.x != 0 or self.y != 0

    def __round__(self, ndigits: int = 0) -> "Vector":
        # round(v, 2)
        return Vector(round(self.x, ndigits), round(self.y, ndigits))

    # ────────────────────────────────────────────────────
    # CONTAINER / SEQUENCE INTERFACE
    # ────────────────────────────────────────────────────

    def __len__(self) -> int:
        # len(v) → number of dimensions
        return 2

    def __getitem__(self, index: int) -> float:
        # v[0] → x,  v[1] → y,  v[2] → IndexError
        if index == 0: return self.x
        if index == 1: return self.y
        raise IndexError(f"Vector index {index} out of range (0 or 1 only)")

    def __setitem__(self, index: int, value: float):
        # v[0] = 10
        if index == 0: self.x = value
        elif index == 1: self.y = value
        else: raise IndexError(f"Vector index {index} out of range")

    def __iter__(self):
        # for component in v:  →  yields x then y
        # Also enables:  x, y = v   (tuple unpacking)
        yield self.x
        yield self.y

    def __contains__(self, value: float) -> bool:
        # value in v
        return value == self.x or value == self.y

    def __reversed__(self):
        # reversed(v)
        yield self.y
        yield self.x

    # ────────────────────────────────────────────────────
    # CALLABLE
    # ────────────────────────────────────────────────────

    def __call__(self, scale: float) -> "Vector":
        # v(2)  → makes the instance callable like a function
        return Vector(self.x * scale, self.y * scale)


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print("── String representations ──")
print(str(v1))              # Vector(3, 4)         — __str__
print(repr(v1))             # Vector(x=3, y=4)     — __repr__
print(f"v1 = {v1}")         # v1 = Vector(3, 4)    — f-string uses __str__
print([v1, v2])             # list uses __repr__   — [Vector(x=3, y=4), ...]

print("\n── Arithmetic ──")
print(v1 + v2)              # Vector(4, 6)         — __add__
print(v1 - v2)              # Vector(2, 2)         — __sub__
print(v1 * 3)               # Vector(9, 12)        — __mul__
print(2 * v1)               # Vector(6, 8)         — __rmul__
print(v1 / 2)               # Vector(1.5, 2.0)     — __truediv__
print(-v1)                  # Vector(-3, -4)       — __neg__

print("\n── Comparison ──")
print(v1 == Vector(3, 4))   # True                 — __eq__
print(v1 < v2)              # False (|v1|=5 > |v2|=2.24) — __lt__
print(v1 > v2)              # True  (Python derives __gt__ from __lt__)

print("\n── Built-in functions ──")
print(abs(v1))              # 5.0                  — __abs__
print(bool(v1))             # True                 — __bool__
print(bool(Vector(0, 0)))   # False
print(len(v1))              # 2                    — __len__
print(round(Vector(1.567, 2.891), 1))  # Vector(1.6, 2.9) — __round__

print("\n── Container behaviour ──")
print(v1[0], v1[1])         # 3  4                 — __getitem__
v1[0] = 10
print(v1)                   # Vector(10, 4)        — __setitem__
v1[0] = 3   # restore

for c in v1:                # __iter__
    print(c, end=" ")       # 3  4
print()

x, y = v1                   # tuple unpacking via __iter__
print(x, y)                 # 3  4

print(4 in v1)              # True                 — __contains__
print(9 in v1)              # False

print(list(reversed(v1)))   # [4, 3]               — __reversed__

print("\n── Callable ──")
print(v1(3))                # Vector(9, 12)        — __call__

print("\n── Hash (dict key) ──")
d = {v1: "origin vector"}   # works because __hash__ is defined
print(d[Vector(3, 4)])      # origin vector


# ════════════════════════════════════════════════════════════
# CONTEXT MANAGER DUNDERS (__enter__ / __exit__)
# ════════════════════════════════════════════════════════════

class DatabaseConnection:
    """Demonstrates the context manager protocol."""

    def __init__(self, host: str):
        self.host = host
        self.connection = None

    def __enter__(self):
        # Called at start of `with` block — set up resource
        print(f"Connecting to {self.host}...")
        self.connection = f"conn:{self.host}"
        return self   # what gets bound to `as` variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Called at END of `with` block — always, even if exception occurred
        # exc_type/val/tb = exception info (all None if no exception)
        print(f"Disconnecting from {self.host}.")
        self.connection = None
        return False  # False = don't suppress exceptions; True = suppress them

    def query(self, sql: str) -> str:
        if not self.connection:
            raise RuntimeError("Not connected")
        return f"[{self.connection}] Result of: {sql}"


print("\n── Context Manager ──")
with DatabaseConnection("localhost:5432") as db:
    print(db.query("SELECT * FROM users"))
# Connecting to localhost:5432...
# [conn:localhost:5432] Result of: SELECT * FROM users
# Disconnecting from localhost:5432.


# ════════════════════════════════════════════════════════════
# QUICK REFERENCE TABLE
# ════════════════════════════════════════════════════════════
#
# REPRESENTATION
#   __str__       → str(obj), print(obj), f-strings
#   __repr__      → repr(obj), REPL, inside containers
#   __format__    → format(obj, spec), f"{obj:spec}"
#
# ARITHMETIC
#   __add__       → +         __radd__    → + (right-hand)
#   __sub__       → -         __rsub__    → - (right-hand)
#   __mul__       → *         __rmul__    → * (right-hand)
#   __truediv__   → /         __floordiv__ → //
#   __mod__       → %         __pow__      → **
#   __neg__       → -x        __pos__      → +x
#   __abs__       → abs()
#
# COMPARISON
#   __eq__   →  ==      __ne__  → !=
#   __lt__   →  <       __le__  → <=
#   __gt__   →  >       __ge__  → >=
#   __hash__ →  hash(), dict keys, set members
#
# BUILT-INS
#   __len__    → len()       __bool__   → bool(), if obj:
#   __round__  → round()     __floor__  → math.floor()
#   __ceil__   → math.ceil() __trunc__  → math.trunc()
#
# CONTAINERS / SEQUENCES
#   __getitem__   → obj[key]       __setitem__ → obj[key]=val
#   __delitem__   → del obj[key]   __contains__ → in
#   __iter__      → for x in obj   __next__     → next()
#   __reversed__  → reversed()     __len__       → len()
#
# OBJECT LIFECYCLE
#   __init__  → constructor    __new__ → allocate memory
#   __del__   → destructor (called by GC — don't rely on it)
#   __call__  → obj()  (makes instance callable)
#   __copy__  → copy.copy()  __deepcopy__ → copy.deepcopy()
#
# CONTEXT MANAGER
#   __enter__ → start of `with` block
#   __exit__  → end of `with` block (error or not)


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Dunders let custom objects behave like Python built-in types
# 2. __str__  = human display;  __repr__  = developer/debugging
# 3. Define __hash__ whenever you define __eq__ (or set hash=...)
# 4. __iter__ + __next__ makes an object iterable (for loops, unpacking)
# 5. __enter__ + __exit__ enables the `with` statement
# 6. __call__ makes an instance usable like a function
# 7. Never call dunders directly — use the operator or built-in instead
