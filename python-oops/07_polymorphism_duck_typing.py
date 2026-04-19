# ============================================================
# LESSON 7: Polymorphism & Duck Typing
# ============================================================
#
# ── WHAT IS POLYMORPHISM? ────────────────────────────────
#
#   Polymorphism = "many forms" (Greek: poly + morphe)
#   The SAME interface (function call, operator) produces
#   DIFFERENT behaviour depending on the OBJECT it's called on.
#
#   One function call → many possible outcomes based on type.
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   A REMOTE CONTROL has one "power" button.
#   Press it on a TV → TV turns on.
#   Press it on an AC → AC turns on.
#   Same button. Same action. Different outcome.
#
# ── WHY DOES POLYMORPHISM EXIST? ────────────────────────
#
#   Without it, you'd need separate functions for each type:
#     make_dog_speak(dog)
#     make_cat_speak(cat)
#     make_robot_speak(robot)
#
#   With polymorphism:
#     make_it_speak(anything)    ← one function, all types
#
#   Benefits:
#     ✅ Less code duplication
#     ✅ Easily add new types without changing existing code
#     ✅ Write flexible, generic code (loops, callbacks, plugins)
#
# ── TYPES OF POLYMORPHISM IN PYTHON ─────────────────────
#
#   1. Method-based (inheritance + override)
#      Same method name, different class → different result
#
#   2. Duck Typing (Python-specific, dynamic)
#      Python doesn't check TYPE — only whether the METHOD exists
#
#   3. Operator Polymorphism (built-in)
#      +, *, len() behave differently based on the operand type
#
# ── WHAT IS DUCK TYPING? ─────────────────────────────────
#
#   "If it walks like a duck and quacks like a duck, it IS a duck."
#
#   Python doesn't require objects to inherit from a common base.
#   It only checks: "Does this object have the method I need?"
#   If yes → it works. If no → AttributeError.
#
#   This is fundamentally different from Java/C++ which require
#   explicit type hierarchies.
#
# ── WHEN TO USE POLYMORPHISM ─────────────────────────────
#
#   ✅ When you have multiple types with the same interface
#   ✅ When writing generic functions that handle many object types
#   ✅ For plugin/strategy patterns (swap behaviour at runtime)
#   ✅ When iterating over a mixed collection of objects
#
# ── WHEN NOT TO RELY ON DUCK TYPING ALONE ───────────────
#
#   ❌ When the interface contract matters — use ABC (Lesson 8)
#      to enforce it and catch errors at class-definition time
#   ❌ In large teams where implicit contracts get broken silently
#
# ── EAFP vs LBYL ─────────────────────────────────────────
#
#   Python style: EAFP — Easier to Ask Forgiveness than Permission
#     try: obj.save()
#     except AttributeError: obj.send()
#
#   vs LBYL (Look Before You Leap — more Java-like):
#     if hasattr(obj, 'save'): obj.save()
#
#   Both work; EAFP is more Pythonic.
#
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 1 — Method-based Polymorphism (inheritance + override)
# ════════════════════════════════════════════════════════════

class Shape:
    """Base — defines the interface all shapes must follow."""

    def area(self) -> float:
        # Raise so subclasses that forget to override are caught
        raise NotImplementedError(f"{self.__class__.__name__} must implement area()")

    def perimeter(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        # Uses self.area() — will call the CHILD's version (polymorphism)
        return (
            f"{self.__class__.__name__:12s} | "
            f"area = {self.area():8.2f} | "
            f"perimeter = {self.perimeter():.2f}"
        )


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2
        return (s * (s-self.a) * (s-self.b) * (s-self.c)) ** 0.5

    def perimeter(self) -> float:
        return self.a + self.b + self.c


# ONE function — works on ANY Shape subclass
def print_shape_info(shape: Shape):
    print(shape.describe())


shapes: list[Shape] = [
    Circle(5),
    Rectangle(4, 6),
    Triangle(3, 4, 5),
]

print("── Method-based Polymorphism ──")
for s in shapes:
    print_shape_info(s)   # each calls its OWN area() and perimeter()

# Total area — generic calculation over mixed types
total = sum(s.area() for s in shapes)
print(f"Total area: {total:.2f}")


# ════════════════════════════════════════════════════════════
# PART 2 — Duck Typing (no inheritance required)
# ════════════════════════════════════════════════════════════

print("\n── Duck Typing ──")

# These classes share NO parent — they just all have speak()
class Dog:
    def speak(self) -> str: return "Woof!"

class Cat:
    def speak(self) -> str: return "Meow!"

class Robot:
    def speak(self) -> str: return "Beep boop."

class Baby:
    def speak(self) -> str: return "Waaah!"

class Car:
    def speak(self) -> str: return "Vroom!"   # cars "speak" too?


# Python doesn't check TYPE — only that speak() exists
def make_it_speak(entity):
    print(f"{entity.__class__.__name__:8s}: {entity.speak()}")


speakers = [Dog(), Cat(), Robot(), Baby(), Car()]
for s in speakers:
    make_it_speak(s)


# ════════════════════════════════════════════════════════════
# PART 3 — Operator Polymorphism (same operator, different types)
# ════════════════════════════════════════════════════════════

print("\n── Operator Polymorphism ──")

# The + operator behaves differently for each type
print(1    + 2)           # 3            (integer addition)
print(1.5  + 2.5)         # 4.0          (float addition)
print("a"  + "b")         # ab           (string concatenation)
print([1]  + [2, 3])      # [1, 2, 3]    (list concatenation)

# len() is polymorphic too
print(len("hello"))        # 5   (string)
print(len([1, 2, 3]))      # 3   (list)
print(len({"a": 1}))       # 1   (dict)

# The * operator
print("abc" * 3)           # abcabcabc   (string)
print([0] * 4)             # [0,0,0,0]   (list)
print(3 * 7)               # 21          (int)


# ════════════════════════════════════════════════════════════
# PART 4 — Duck Typing with EAFP (real-world pattern)
# ════════════════════════════════════════════════════════════

print("\n── EAFP Duck Typing ──")

class PDFExporter:
    def export(self, data: str) -> str:
        return f"Exporting '{data}' as PDF"

class CSVExporter:
    def export(self, data: str) -> str:
        return f"Exporting '{data}' as CSV"

class EmailSender:
    # Different method name — no export(), only send()
    def send(self, data: str) -> str:
        return f"Sending '{data}' via email"


def process(handler, data: str):
    # EAFP: try the common interface, fall back gracefully
    try:
        print(handler.export(data))
    except AttributeError:
        try:
            print(handler.send(data))
        except AttributeError:
            print(f"{handler.__class__.__name__} has no export/send method")


process(PDFExporter(), "Report Q1")    # Exporting 'Report Q1' as PDF
process(CSVExporter(), "Sales Data")  # Exporting 'Sales Data' as CSV
process(EmailSender(), "Invoice")     # Sending 'Invoice' via email


# ════════════════════════════════════════════════════════════
# PART 5 — Polymorphism with a real-world plugin system
# ════════════════════════════════════════════════════════════

print("\n── Plugin System ──")

class StripePayment:
    def pay(self, amount: float) -> str:
        return f"Stripe charged {amount:.2f}"

class PayPalPayment:
    def pay(self, amount: float) -> str:
        return f"PayPal sent {amount:.2f}"

class JazzCashPayment:
    def pay(self, amount: float) -> str:
        return f"JazzCash transferred {amount:.2f}"


def checkout(payment_method, amount: float):
    # Doesn't care which payment class — just needs pay()
    result = payment_method.pay(amount)
    print(f"Payment complete: {result}")


checkout(StripePayment(), 1500)
checkout(PayPalPayment(), 2500)
checkout(JazzCashPayment(), 750)
# Swap payment method without changing checkout() logic


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Checking type instead of using duck typing
#   WRONG:
#     if type(shape) == Circle:
#         area = 3.14 * r**2
#     elif type(shape) == Rectangle: ...
#   RIGHT: call shape.area() — let polymorphism handle it
#
# MISTAKE 2: Duck typing without any contract → silent bugs
#   If 10 classes need speak(), use an ABC (Lesson 8) to enforce it.
#   Duck typing works; ABC enforces at definition time (safer at scale).
#
# MISTAKE 3: Operator polymorphism surprises
#   "1" + 1 → TypeError  (can't concat str and int)
#   Python is polymorphic but still type-safe for operators


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Polymorphism = same call, different result depending on the object
# 2. Method-based: achieved via inheritance + method override
# 3. Duck typing: Python only checks IF the method exists, not the TYPE
# 4. Operators (+, *, len) are polymorphic by default in Python
# 5. Use duck typing for flexibility; use ABC when you need enforcement
# 6. EAFP (try/except) is the Pythonic way to handle duck typing
# 7. Polymorphism is what makes generic functions and plugin systems work
