# ============================================================
# LESSON 2: Class Variables vs Instance Variables
# ============================================================
#
# ── WHAT IS AN INSTANCE VARIABLE? ───────────────────────
#
#   A variable that belongs to ONE specific object.
#   Every object gets its OWN separate copy.
#   Defined inside __init__ using self.variable_name
#
#   Example: each Dog has its own name, age, breed.
#   Changing Bruno's name does NOT change Max's name.
#
# ── WHAT IS A CLASS VARIABLE? ───────────────────────────
#
#   A variable that belongs to the CLASS ITSELF — shared by
#   ALL instances of that class.
#   Defined directly inside the class body (not in __init__).
#
#   Example: all Dogs belong to species "Canis familiaris"
#   You don't want to store that separately on every dog object.
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   Think of a SCHOOL:
#     Class variable  = school name ("City School")
#                       → same for every student
#     Instance variable = student name, roll number, grade
#                       → different for every student
#
# ── WHY DOES THIS DISTINCTION MATTER? ───────────────────
#
#   If you store shared data as an instance variable, you
#   waste memory — every object holds a copy of identical data.
#   Class variables save memory and ensure consistency.
#
#   Class variables are also useful as COUNTERS or DEFAULTS
#   shared across all instances.
#
# ── WHEN TO USE CLASS VARIABLES ─────────────────────────
#
#   ✅ Data truly shared by ALL instances (species, school name)
#   ✅ Counters that track total objects created
#   ✅ Default config values shared across objects
#   ✅ Constants related to the class
#
# ── WHEN NOT TO USE CLASS VARIABLES ─────────────────────
#
#   ❌ For data that should be unique per object → use instance var
#   ❌ For mutable defaults like lists/dicts — DANGEROUS GOTCHA
#      (all instances accidentally share the same list)
#
# ── THE BIG GOTCHA ───────────────────────────────────────
#
#   Writing to a class variable via an instance (dog1.species = "x")
#   does NOT modify the class variable.
#   It creates a NEW instance variable that SHADOWS the class var.
#   Only the one object is affected.
#   To truly change the class var: Dog.species = "x"
#
# ── HOW PYTHON RESOLVES ATTRIBUTE LOOKUP ────────────────
#
#   When you READ  obj.attr:
#     1. Python checks obj.__dict__  (instance variables first)
#     2. Then checks  type(obj).__dict__  (class variables)
#     3. Then walks up the inheritance chain
#     4. AttributeError if not found
#
#   When you WRITE  obj.attr = value:
#     Always writes to obj.__dict__ — NEVER to the class
#
# ============================================================


class Dog:

    # ── CLASS VARIABLES ────────────────────────────────
    # Defined at class level — shared by ALL Dog objects
    species    = "Canis familiaris"
    total_dogs = 0                    # counter

    def __init__(self, name: str, age: int, breed: str):
        # ── INSTANCE VARIABLES ─────────────────────────
        # Each Dog gets its OWN separate copy
        self.name  = name
        self.age   = age
        self.breed = breed

        # Updating a class variable: use ClassName.var, not self.var
        # self.total_dogs += 1 would create an instance var — WRONG
        Dog.total_dogs += 1

    def describe(self) -> str:
        return (
            f"{self.name} | Age: {self.age} | "
            f"Breed: {self.breed} | Species: {self.species}"
        )

    def birthday(self):
        self.age += 1
        return f"Happy birthday {self.name}! Now {self.age} years old."

    def __str__(self):
        return f"Dog({self.name}, age={self.age})"


# ════════════════════════════════════════════════════════════
# DEMO 1 — Basic usage
# ════════════════════════════════════════════════════════════

d1 = Dog("Bruno", 3, "Labrador")
d2 = Dog("Max",   5, "Poodle")
d3 = Dog("Bella", 2, "Beagle")

# Instance variables — unique per object
print(d1.name)    # Bruno
print(d2.name)    # Max
print(d3.age)     # 2

# Class variable — same for all, accessible on instance OR class
print(d1.species)      # Canis familiaris  ← via instance
print(d2.species)      # Canis familiaris
print(Dog.species)     # Canis familiaris  ← via class directly

# Counter updated on every creation
print(Dog.total_dogs)  # 3

# birthday() changes only THIS dog's age
print(d1.birthday())   # Happy birthday Bruno! Now 4 years old.
print(d1.age)          # 4
print(d2.age)          # 5  ← untouched


# ════════════════════════════════════════════════════════════
# DEMO 2 — The Gotcha: writing via instance SHADOWS class var
# ════════════════════════════════════════════════════════════

print("\n── GOTCHA DEMO ──")

# This looks like it modifies Dog.species — it does NOT.
# Python creates a NEW instance variable on d1 that SHADOWS Dog.species
d1.species = "Modified only on d1"

print(d1.species)    # Modified only on d1   ← d1's OWN instance var
print(d2.species)    # Canis familiaris       ← class var untouched
print(Dog.species)   # Canis familiaris       ← class var untouched

# To PROPERLY update the class variable for ALL objects:
Dog.species = "Canis lupus familiaris"
print(d2.species)    # Canis lupus familiaris  ← updated
print(d3.species)    # Canis lupus familiaris  ← updated
# d1 still has its own instance var shadowing the class var


# ════════════════════════════════════════════════════════════
# DEMO 3 — The MUTABLE class variable trap (very common bug)
# ════════════════════════════════════════════════════════════

print("\n── MUTABLE CLASS VAR TRAP ──")

class BuggyClass:
    shared_list = []   # ← ONE list shared by ALL instances

    def __init__(self, name):
        self.name = name

    def add(self, item):
        self.shared_list.append(item)   # mutates the ONE shared list


a = BuggyClass("A")
b = BuggyClass("B")

a.add("apple")
b.add("banana")

# Both see each other's data — BAD
print(a.shared_list)   # ['apple', 'banana']
print(b.shared_list)   # ['apple', 'banana']

# FIX: declare the list as an INSTANCE variable
class FixedClass:
    def __init__(self, name):
        self.name = name
        self.my_list = []   # each object gets its OWN list

    def add(self, item):
        self.my_list.append(item)


x = FixedClass("X")
y = FixedClass("Y")

x.add("apple")
y.add("banana")

print(x.my_list)   # ['apple']   ← independent
print(y.my_list)   # ['banana']  ← independent


# ════════════════════════════════════════════════════════════
# DEMO 4 — Inspecting __dict__ to see where things are stored
# ════════════════════════════════════════════════════════════

print("\n── INSTANCE vs CLASS DICT ──")

d4 = Dog("Rocky", 4, "Rottweiler")

# Instance __dict__ — ONLY instance variables
print(d4.__dict__)
# {'name': 'Rocky', 'age': 4, 'breed': 'Rottweiler'}
# species and total_dogs NOT here — they live on the class

# Class dict contains class variables (+ methods + more)
print(Dog.__dict__.get("species"))      # Canis lupus familiaris
print(Dog.__dict__.get("total_dogs"))   # 4 (d1, d2, d3, d4)


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Using mutable defaults as class variables
#   class Bag:
#       items = []       ← WRONG, shared across all Bag objects
#   Use:
#       def __init__(self):
#           self.items = []
#
# MISTAKE 2: Modifying class var via instance
#   dog1.total_dogs += 1  ← creates instance var, counter stays 0
#   Use:
#       Dog.total_dogs += 1
#
# MISTAKE 3: Mixing up class-level constants with instance data
#   If every user could have a different MAX_AGE, it's an instance var
#   If MAX_AGE is a fixed rule for all users, it's a class var


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Instance var (self.x)  → unique per object, in obj.__dict__
# 2. Class var (ClassName.x) → shared by all, in class.__dict__
# 3. READ via instance: obj.x → Python checks instance first, then class
# 4. WRITE via instance: obj.x = v → ALWAYS writes to instance dict
# 5. To update class var globally: ClassName.x = v
# 6. NEVER use mutable types (list, dict) as class variables
# 7. Use class vars for: counters, shared constants, defaults
# 8. Use instance vars for: anything unique to one object
