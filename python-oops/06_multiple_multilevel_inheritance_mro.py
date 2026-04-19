# ============================================================
# LESSON 6: Multiple & Multilevel Inheritance + MRO
# ============================================================
#
# ── WHAT IS MULTILEVEL INHERITANCE? ─────────────────────
#
#   A chain: Grandparent → Parent → Child
#   Each level inherits everything from above.
#
#   Example:
#     LivingThing → Animal → Dog
#     Dog gets breathe() from LivingThing AND eat() from Animal
#
# ── WHAT IS MULTIPLE INHERITANCE? ───────────────────────
#
#   A child inherits from TWO or MORE parents simultaneously.
#
#   Example:
#     class Duck(Flyable, Swimmable):
#     Duck can both fly AND swim.
#
# ── WHY DOES MULTIPLE INHERITANCE EXIST? ────────────────
#
#   Sometimes an object genuinely has behaviour from multiple
#   unrelated sources. A FlyingFish can fly AND swim.
#   No single parent covers both — so you inherit from two.
#
# ── THE DIAMOND PROBLEM ──────────────────────────────────
#
#   When two parents share a common grandparent:
#
#         Base
#        /    \
#      Left   Right
#        \    /
#        Child
#
#   Child inherits from both Left and Right.
#   Left and Right both inherit from Base.
#   Question: if Child calls super().__init__(), how many times
#   does Base.__init__ run? Without smart handling — TWICE.
#   That causes bugs (double-counting, double-init).
#
# ── WHAT IS MRO? ─────────────────────────────────────────
#
#   MRO = Method Resolution Order
#   The exact ordered list Python uses to search for methods
#   when you call something on an object.
#
#   Python uses the C3 Linearisation algorithm to compute MRO.
#   It guarantees:
#     - Child comes before parent
#     - Left parent before right parent (as listed in class def)
#     - No class appears twice
#
#   Check it:  ClassName.__mro__   or   help(ClassName)
#
# ── HOW super() SOLVES THE DIAMOND ──────────────────────
#
#   super() doesn't mean "call MY parent".
#   It means "call the NEXT class in MRO that hasn't been called yet".
#   This ensures each class in the chain runs EXACTLY ONCE.
#
# ── WHEN TO USE MULTIPLE INHERITANCE ────────────────────
#
#   ✅ Mixing in orthogonal behaviours (Fly + Swim)
#   ✅ Mixin classes (Lesson 12 — the clean version of this)
#   ✅ Framework patterns where multiple protocols apply
#
# ── WHEN NOT TO USE ──────────────────────────────────────
#
#   ❌ When it creates ambiguity or confusion about which method runs
#   ❌ Deep diamond hierarchies — use Mixins + Composition instead
#   ❌ When you can't clearly state the IS-A relationship for each parent
#
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 1 — Multilevel Inheritance (chain: A → B → C)
# ════════════════════════════════════════════════════════════

class LivingThing:
    def breathe(self):
        return "Breathing oxygen..."

    def __str__(self):
        return f"{self.__class__.__name__} object"


class Animal(LivingThing):         # inherits from LivingThing
    def __init__(self, name: str):
        self.name = name

    def eat(self):
        return f"{self.name} is eating."

    def sleep(self):
        return f"{self.name} is sleeping."


class Dog(Animal):                  # inherits from Animal → LivingThing
    def __init__(self, name: str, breed: str):
        super().__init__(name)      # calls Animal.__init__
        self.breed = breed

    def bark(self):
        return f"{self.name} says: Woof!"


print("── Multilevel Inheritance ──")
d = Dog("Rex", "Husky")

print(d.bark())       # Rex says: Woof!          ← Dog's own
print(d.eat())        # Rex is eating.            ← from Animal
print(d.sleep())      # Rex is sleeping.          ← from Animal
print(d.breathe())    # Breathing oxygen...       ← from LivingThing

# MRO shows the entire chain
print(Dog.__mro__)
# (<class 'Dog'>, <class 'Animal'>, <class 'LivingThing'>, <class 'object'>)


# ════════════════════════════════════════════════════════════
# PART 2 — Multiple Inheritance (C inherits from A AND B)
# ════════════════════════════════════════════════════════════

class Flyable:
    def fly(self):
        return "Soaring through the sky"

    def move(self):
        return "Moving by flying"

    def describe(self):
        return "I can fly"


class Swimmable:
    def swim(self):
        return "Gliding through water"

    def move(self):
        return "Moving by swimming"

    def describe(self):
        return "I can swim"


# Duck can both fly and swim — inherits from BOTH
class Duck(Flyable, Swimmable):
    def __init__(self, name: str):
        self.name = name

    def quack(self):
        return f"{self.name} says: Quack!"


print("\n── Multiple Inheritance ──")
duck = Duck("Donald")

print(duck.quack())       # Donald says: Quack!
print(duck.fly())         # Soaring through the sky   ← from Flyable
print(duck.swim())        # Gliding through water     ← from Swimmable

# When BOTH parents have move() and describe(), MRO decides which runs
# class Duck(Flyable, Swimmable) → Flyable is listed first → Flyable wins
print(duck.move())        # Moving by flying          ← Flyable wins (listed first)
print(duck.describe())    # I can fly                 ← Flyable wins

print(Duck.__mro__)
# [Duck, Flyable, Swimmable, object]

# To explicitly call a specific parent's version:
print(Swimmable.move(duck))    # Moving by swimming   ← forced


# ════════════════════════════════════════════════════════════
# PART 3 — Diamond Problem + super() solution
# ════════════════════════════════════════════════════════════
#
#         Base
#        /    \
#      Left   Right
#        \    /
#        Child
#
# Without super(): Base.__init__ runs TWICE (once from Left, once from Right)
# With super(): C3-MRO guarantees Base.__init__ runs EXACTLY ONCE

print("\n── Diamond Problem ──")


class Base:
    def __init__(self):
        print("  Base.__init__ called")
        self.value = 0

    def greet(self):
        return "Hello from Base"


class Left(Base):
    def __init__(self):
        print("  Left.__init__ called")
        super().__init__()    # follows MRO → calls Right next, not Base directly
        self.value += 10

    def greet(self):
        return f"Left says hi | {super().greet()}"


class Right(Base):
    def __init__(self):
        print("  Right.__init__ called")
        super().__init__()    # follows MRO → calls Base next
        self.value += 20

    def greet(self):
        return f"Right says hi | {super().greet()}"


class Child(Left, Right):
    def __init__(self):
        print("  Child.__init__ called")
        super().__init__()    # follows MRO: Left → Right → Base

    def greet(self):
        return f"Child says hi | {super().greet()}"


c = Child()
# Output (each __init__ runs EXACTLY ONCE):
#   Child.__init__ called
#   Left.__init__ called
#   Right.__init__ called
#   Base.__init__ called

print(f"value = {c.value}")   # 30 (0 + 10 + 20)

# greet() chain follows MRO too
print(c.greet())
# Child says hi | Left says hi | Right says hi | Hello from Base

print(Child.__mro__)
# [Child, Left, Right, Base, object]


# ════════════════════════════════════════════════════════════
# PART 4 — Visualising MRO with a real example
# ════════════════════════════════════════════════════════════

print("\n── MRO Visualisation ──")


class A:
    def hello(self): return "A"

class B(A):
    def hello(self): return f"B → {super().hello()}"

class C(A):
    def hello(self): return f"C → {super().hello()}"

class D(B, C):
    def hello(self): return f"D → {super().hello()}"


print(D().hello())    # D → B → C → A
print(D.__mro__)      # [D, B, C, A, object]

# Each class calls super() which moves to the NEXT in MRO list
# D → B → C → A  (not D → B → A then D → C → A!)
# That's what C3 linearisation guarantees.


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Not using super() in multiple inheritance
#   class Left(Base):
#       def __init__(self):
#           Base.__init__(self)   ← hardcoded, skips Right's __init__
#   Always use super() so MRO handles the chain correctly.
#
# MISTAKE 2: Forgetting that MRO is left-to-right
#   class Duck(Flyable, Swimmable) → Flyable.move() wins
#   class Duck(Swimmable, Flyable) → Swimmable.move() wins
#   Order in class(...) matters.
#
# MISTAKE 3: Building deep diamond hierarchies for business logic
#   Use Mixins (Lesson 12) instead — cleaner, more intentional.


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Multilevel = chain (A→B→C); Multiple = fan-in (A,B→C)
# 2. MRO = the ordered list Python searches for methods
# 3. MRO rule: child first, then left-to-right parents, no repeats
# 4. super() follows MRO — essential for correct multiple inheritance
# 5. Diamond problem: super() ensures each class runs EXACTLY ONCE
# 6. Order in class(A, B) matters — A's methods win over B's
# 7. Check: ClassName.__mro__  to debug unexpected method resolution
