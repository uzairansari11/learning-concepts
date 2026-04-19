# ============================================================
# LESSON 14: Metaclasses
# ============================================================
#
# ── WHAT IS A METACLASS? ─────────────────────────────────
#
#   In Python, EVERYTHING is an object — including classes.
#   If classes are objects, they must be INSTANCES of something.
#   That something is a METACLASS.
#
#   Normal world:
#     object  →  is an instance of  →  class
#     "hello" →  is an instance of  →  str
#     [1,2,3] →  is an instance of  →  list
#
#   Meta level:
#     str     →  is an instance of  →  type   (the default metaclass)
#     list    →  is an instance of  →  type
#     YourClass → is an instance of →  type
#
#   A metaclass is the CLASS of a CLASS.
#   Just as a class controls how its instances behave,
#   a metaclass controls how CLASSES are created and behave.
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   A CLASS is like a blueprint (for houses).
#   A METACLASS is like the FACTORY that creates blueprints.
#   It decides the RULES all blueprints must follow:
#     - Every blueprint must have a "fire safety" section
#     - Every blueprint must be registered in a central registry
#     - Every blueprint's room names must be in UPPERCASE
#
# ── THE `type` FUNCTION ──────────────────────────────────
#
#   `type` is the built-in metaclass — the default class of all classes.
#
#   Two uses:
#     type(obj)           → returns the class of an object
#     type(name, bases, namespace) → CREATES a new class dynamically
#
# ── HOW PYTHON CREATES A CLASS ──────────────────────────
#
#   When Python processes:
#     class Dog(Animal):
#         species = "Canis familiaris"
#         def bark(self): ...
#
#   It does:
#     1. Collect the body into a namespace dict
#     2. Find the metaclass (default: type)
#     3. Call: metaclass("Dog", (Animal,), namespace)
#     4. That returns the new class object
#
#   A custom metaclass intercepts step 3 — letting you
#   transform or validate the class before it exists.
#
# ── METACLASS HOOKS ──────────────────────────────────────
#
#   __new__(mcs, name, bases, namespace)
#     → called BEFORE the class exists, builds and returns it
#     → use to transform the namespace (rename attrs, add methods)
#
#   __init__(cls, name, bases, namespace)
#     → called AFTER the class is created
#     → use for registration, validation, post-processing
#
# ── WHEN TO USE METACLASSES ─────────────────────────────
#
#   ✅ Building frameworks (ORMs, plugin systems, CLI tools)
#   ✅ Auto-registering all subclasses in a central registry
#   ✅ Enforcing class-level naming conventions or structure
#   ✅ Injecting methods/attributes into every class automatically
#
# ── WHEN NOT TO USE METACLASSES ─────────────────────────
#
#   ❌ Application-level code — too complex, confuses readers
#   ❌ When a class decorator does the job (simpler)
#   ❌ When __init_subclass__ does the job (even simpler, Py3.6+)
#   ❌ When a Mixin or ABC solves the problem
#
#   Rule: if you THINK you need a metaclass, you probably don't.
#   If you KNOW you need a metaclass, you probably do.
#
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 0 — type(): the default metaclass
# ════════════════════════════════════════════════════════════

print("── type() is the metaclass of every class ──")

print(type(int))          # <class 'type'>
print(type(str))          # <class 'type'>
print(type(list))         # <class 'type'>

class Dog:
    pass

print(type(Dog))          # <class 'type'>
print(isinstance(Dog, type))   # True — Dog is an instance of type

# type() can also CREATE classes dynamically at runtime
Cat = type(
    "Cat",                        # class name
    (object,),                    # base classes
    {                             # class body (namespace)
        "species": "Felis catus",
        "meow": lambda self: f"{self.__class__.__name__} says Meow!",
    }
)

c = Cat()
print(Cat.species)    # Felis catus
print(c.meow())       # Cat says Meow!


# ════════════════════════════════════════════════════════════
# PART 1 — Custom Metaclass: enforce naming conventions
# ════════════════════════════════════════════════════════════

print("\n── Metaclass: force UPPERCASE constants ──")


class UpperAttributeMeta(type):
    """
    Metaclass that uppercases all string attributes in a class body.
    Applied at CLASS CREATION TIME — before any object is created.
    """

    def __new__(mcs, name, bases, namespace):
        # Transform the namespace before the class is built
        new_namespace = {}
        for key, value in namespace.items():
            if not key.startswith("_") and isinstance(value, str):
                # Uppercase both key and value for string constants
                new_namespace[key.upper()] = value.upper()
            else:
                new_namespace[key] = value
        return super().__new__(mcs, name, bases, new_namespace)


class DatabaseConfig(metaclass=UpperAttributeMeta):
    # You write lowercase...
    host     = "localhost"
    port     = "5432"
    name     = "mydb"
    user     = "admin"


# ...but the metaclass uppercased everything for you
print(DatabaseConfig.HOST)    # LOCALHOST
print(DatabaseConfig.PORT)    # 5432
print(DatabaseConfig.NAME)    # MYDB
print(DatabaseConfig.USER)    # ADMIN


# ════════════════════════════════════════════════════════════
# PART 2 — Metaclass: auto-register all subclasses
# ════════════════════════════════════════════════════════════
#
# Use case: a plugin system where plugins are discovered automatically.
# Any class that inherits from BasePlugin is registered — automatically.

print("\n── Metaclass: auto plugin registry ──")


class PluginMeta(type):
    """Metaclass that maintains a registry of all concrete subclasses."""

    registry: dict[str, type] = {}

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        # Skip the abstract base class itself (it has no bases)
        if bases:
            PluginMeta.registry[name] = cls
            print(f"  [Registry] Registered plugin: {name}")


class BasePlugin(metaclass=PluginMeta):
    """Abstract base — all plugins inherit from here."""

    def run(self) -> str:
        raise NotImplementedError


# Each of these is registered automatically when Python processes them
class AuthPlugin(BasePlugin):
    def run(self) -> str: return "Running authentication check..."

class CachePlugin(BasePlugin):
    def run(self) -> str: return "Warming cache..."

class LogPlugin(BasePlugin):
    def run(self) -> str: return "Rotating log files..."

class SecurityPlugin(BasePlugin):
    def run(self) -> str: return "Scanning for vulnerabilities..."


print("\nAll registered plugins:")
for name, cls in PluginMeta.registry.items():
    plugin = cls()
    print(f"  {name}: {plugin.run()}")


# ════════════════════════════════════════════════════════════
# PART 3 — Metaclass: enforce interface (like ABC but manual)
# ════════════════════════════════════════════════════════════

print("\n── Metaclass: enforce required methods ──")


class InterfaceMeta(type):
    """Metaclass that checks required methods exist at class creation."""

    _required_methods: list[str] = []

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # Skip check on the base class itself
        if bases:
            for method in mcs._required_methods:
                if not callable(getattr(cls, method, None)):
                    raise TypeError(
                        f"Class '{name}' must implement '{method}()'"
                    )
        return cls


class ShapeMeta(InterfaceMeta):
    _required_methods = ["area", "perimeter"]


class GoodShape(metaclass=ShapeMeta):
    def area(self): return 0
    def perimeter(self): return 0


try:
    class BadShape(metaclass=ShapeMeta):
        def area(self): return 0
        # perimeter missing!
except TypeError as e:
    print(e)   # Class 'BadShape' must implement 'perimeter()'

print("GoodShape created successfully.")


# ════════════════════════════════════════════════════════════
# PART 4 — __init_subclass__: simpler alternative (Python 3.6+)
# ════════════════════════════════════════════════════════════
#
# Covers 80% of metaclass use cases with far less complexity.
# A parent class can react when it is SUBCLASSED.

print("\n── __init_subclass__: simpler plugin registry ──")


class BaseHandler:
    """Parent that auto-registers its children."""

    _handlers: dict[str, type] = {}

    def __init_subclass__(cls, handler_type: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if handler_type:
            BaseHandler._handlers[handler_type] = cls
            print(f"  [Auto-registered] {handler_type} → {cls.__name__}")

    def handle(self, request: str) -> str:
        raise NotImplementedError


class JSONHandler(BaseHandler, handler_type="json"):
    def handle(self, request: str) -> str:
        return f"Handling JSON: {request}"

class XMLHandler(BaseHandler, handler_type="xml"):
    def handle(self, request: str) -> str:
        return f"Handling XML: {request}"

class CSVHandler(BaseHandler, handler_type="csv"):
    def handle(self, request: str) -> str:
        return f"Handling CSV: {request}"


print("\nDispatching requests:")
for fmt, cls in BaseHandler._handlers.items():
    handler = cls()
    print(f"  {handler.handle(f'data.{fmt}')}")


# ════════════════════════════════════════════════════════════
# COMPARISON TABLE
# ════════════════════════════════════════════════════════════
#
#   TOOL               COMPLEXITY   USE WHEN
#   ─────────────────────────────────────────────────────────
#   @decorator         Low          Transform one class externally
#   __init_subclass__  Low          React when subclassed (registry)
#   Mixin              Low          Add methods to multiple classes
#   ABC                Medium       Enforce interface (abstract methods)
#   Metaclass          High         Control class CREATION itself
#
#   Prefer simpler tools. Reach for metaclasses only for
#   framework-level class-creation control.


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. type is the metaclass of all classes — every class is its instance
# 2. Metaclass controls HOW a class is built, not how its objects behave
# 3. __new__(mcs,...) → called BEFORE class exists (transform namespace)
# 4. __init__(cls,...) → called AFTER class exists (registration, setup)
# 5. Use metaclasses for frameworks, ORMs, plugin auto-registration
# 6. __init_subclass__ covers most metaclass needs — prefer it
# 7. "If in doubt, don't use a metaclass" — Tim Peters
