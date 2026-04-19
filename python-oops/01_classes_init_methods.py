# ============================================================
# LESSON 1: Classes, __init__, and Instance Methods
# ============================================================
#
# ── WHAT IS A CLASS? ─────────────────────────────────────
#
#   A class is a BLUEPRINT or TEMPLATE for creating objects.
#   It defines what DATA (attributes) an object will hold
#   and what ACTIONS (methods) it can perform.
#
#   Think of it like a HOUSE BLUEPRINT:
#     - The blueprint is the CLASS
#     - Each house built from it is an OBJECT (instance)
#     - Two houses from the same blueprint are independent —
#       painting one red doesn't paint the other.
#
# ── WHY DO CLASSES EXIST? ────────────────────────────────
#
#   Before OOP, code was just a list of functions and variables.
#   As programs grew bigger, it became hard to manage "which
#   variable belongs to which function".
#
#   Classes BUNDLE related data + behaviour together into one
#   logical unit. This makes code:
#     - Easier to read  (everything about a User is in User class)
#     - Easier to reuse (create 1000 Users from one blueprint)
#     - Easier to maintain (change the blueprint, all instances benefit)
#
# ── WHAT IS AN OBJECT (INSTANCE)? ───────────────────────
#
#   An object is one specific thing created FROM the class.
#   When you call  Bird("Parrot")  Python:
#     1. Allocates memory for a new Bird object
#     2. Calls __init__ to fill in its data
#     3. Returns the object to you
#
# ── WHAT IS __init__? ────────────────────────────────────
#
#   __init__ is the CONSTRUCTOR — a special method Python
#   calls automatically every time you create a new object.
#   Its job: set the initial state (attributes) of the object.
#
#   You CANNOT return a value from __init__ (return None only).
#   If you need something created before init, use __new__.
#
# ── WHAT IS self? ────────────────────────────────────────
#
#   'self' is a reference to the OBJECT BEING CREATED/USED.
#   Python passes it automatically as the first argument.
#   You can name it anything, but 'self' is the universal convention.
#
#   b = Bird("Parrot")
#   b.walk()       →  Python silently calls  Bird.walk(b)
#                      'self' inside walk() == b
#
# ── WHAT IS AN INSTANCE METHOD? ─────────────────────────
#
#   A function defined inside a class that operates on
#   a specific instance (object). It always receives 'self'.
#
# ── WHEN TO USE CLASSES ──────────────────────────────────
#
#   ✅ When you need multiple objects of the same "type"
#      (10 users, 100 products, 50 bank accounts)
#   ✅ When data and behaviour naturally belong together
#   ✅ When you want to model real-world entities
#   ✅ When you need inheritance, encapsulation, or polymorphism
#
# ── WHEN NOT TO USE CLASSES ──────────────────────────────
#
#   ❌ For a one-off utility that just needs a function
#   ❌ When a simple dictionary or namedtuple is enough
#   ❌ Don't create classes just to have classes — it adds
#      complexity without benefit
#
# ============================================================


# ── Defining a Class ──────────────────────────────────────
#
# Syntax:
#   class ClassName:       ← CamelCase by convention
#       def __init__(self, param1, param2):
#           self.attr = param1   ← instance attribute
#
#       def method_name(self):   ← instance method
#           ...

class Bird:

    # __init__ = constructor
    # Runs automatically when:  b = Bird("Parrot", "Parrot Family")
    # 'self' = the new Bird object being created
    def __init__(self, name: str, species: str, can_fly: bool = True):
        # Instance attributes — each Bird object has its OWN copy
        self.name = name
        self.species = species
        self.can_fly = can_fly
        self.color: str | None = None   # optional attribute, starts as None

    # ── Instance Methods ──────────────────────────────────
    #
    # 'self' gives the method access to THIS object's data.
    # Without self, the method would have no way to know
    # WHICH bird's name to use.

    def walk(self) -> str:
        return f"{self.name} can walk"

    def fly(self) -> str:
        if self.can_fly:
            return f"{self.name} soars through the sky!"
        return f"{self.name} cannot fly — it has wings but uses them to swim."

    def describe(self) -> str:
        # A method can call other methods via self
        return (
            f"Name    : {self.name}\n"
            f"Species : {self.species}\n"
            f"Can Fly : {self.can_fly}\n"
            f"Color   : {self.color or 'Unknown'}"
        )

    # __str__  → what print(object) shows (for humans)
    # Without this, print(b) shows: <__main__.Bird object at 0x...>
    def __str__(self) -> str:
        return f"Bird({self.name}, {self.species})"

    # __repr__ → unambiguous representation (for developers/debugging)
    def __repr__(self) -> str:
        return f"Bird(name={self.name!r}, species={self.species!r}, can_fly={self.can_fly!r})"


# ════════════════════════════════════════════════════════════
# USING THE CLASS
# ════════════════════════════════════════════════════════════

# Creating objects (instances) — Python calls __init__ for you
parrot  = Bird("Parrot",  "Parrot Family",  can_fly=True)
penguin = Bird("Penguin", "Penguin Family", can_fly=False)
eagle   = Bird("Eagle",   "Eagle Family")    # can_fly defaults to True

# Accessing attributes with dot notation
print(parrot.name)         # Parrot
print(penguin.species)     # Penguin Family
print(eagle.can_fly)       # True

# Calling methods — Python automatically passes the object as 'self'
print(parrot.walk())       # Parrot can walk
print(parrot.fly())        # Parrot soars through the sky!
print(penguin.fly())       # Penguin cannot fly...

# Full description
print(parrot.describe())

# __str__ in action
print(parrot)              # Bird(Parrot, Parrot Family)
print(str(parrot))         # Bird(Parrot, Parrot Family)

# __repr__ in action — you'll see this in the REPL
print(repr(parrot))        # Bird(name='Parrot', species='Parrot Family', can_fly=True)


# ── Each object is FULLY INDEPENDENT ────────────────────
#
# Changing one object's attribute does NOT affect others.
# Each object has its OWN copy of instance attributes.

parrot.name = "Polly"
print(parrot.name)         # Polly   — changed
print(penguin.name)        # Penguin — untouched

parrot.color = "Green"     # setting an attribute declared in __init__
print(parrot.color)        # Green
print(penguin.color)       # None   — its own separate copy


# ── Type and identity checks ──────────────────────────────

print(type(parrot))               # <class '__main__.Bird'>
print(isinstance(parrot, Bird))   # True
print(parrot is penguin)          # False — different objects in memory
print(id(parrot) == id(penguin))  # False — different memory addresses


# ── Common Mistake #1: Forgetting self ───────────────────
#
# WRONG:
#   class Dog:
#       def bark():          ← missing self
#           return "Woof"
#   d = Dog()
#   d.bark()    → TypeError: bark() takes 0 positional arguments but 1 was given
#
# RIGHT:
#   def bark(self):
#       return "Woof"


# ── Common Mistake #2: Calling __init__ manually ─────────
#
# WRONG:  b.__init__("NewName", "Species")  — don't do this
# RIGHT:  Just create a new object:  b = Bird("NewName", "Species")


# ── Common Mistake #3: Not using self for attributes ─────
#
# WRONG:
#   def __init__(self, name):
#       name = name       ← this is a LOCAL variable, lost after __init__
#
# RIGHT:
#   def __init__(self, name):
#       self.name = name  ← stored on the object


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. class  = blueprint;  object = one instance built from it
# 2. __init__ is called automatically on object creation
# 3. self = reference to the current object — always first param
# 4. Instance attributes (self.x) are UNIQUE to each object
# 5. Methods are functions inside a class that use self
# 6. __str__  → human-readable string   (used by print)
# 7. __repr__ → developer-readable string (used by repr/REPL)
# 8. Every Python object is an instance of some class
