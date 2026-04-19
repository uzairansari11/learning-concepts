# ============================================================
# BONUS LESSON: super() — Complete Deep Dive
# ============================================================
#
# ── WHAT IS super()? ─────────────────────────────────────
#
#   super() returns a PROXY OBJECT that delegates method calls
#   to the NEXT class in the MRO (Method Resolution Order).
#
#   KEY POINT:
#   super() does NOT mean "my parent class".
#   It means "the NEXT class in the MRO that hasn't run yet".
#   In simple single inheritance, that happens to be the parent.
#   In multiple inheritance, it could be a sibling class!
#
# ── WHY DOES super() EXIST? ─────────────────────────────
#
#   Without super(), calling a parent method is:
#     Animal.__init__(self, name)
#
#   Problems:
#     1. FRAGILE — if you rename Animal to LivingCreature, every
#        child breaks. You must update all references manually.
#     2. BROKEN IN MULTIPLE INHERITANCE — skips classes in MRO,
#        causing some __init__ methods to never be called.
#
#   With super():
#     super().__init__(name)
#
#   Benefits:
#     1. MRO-AWARE — follows the correct call order automatically
#     2. REFACTORING-SAFE — doesn't hardcode parent class name
#     3. COOPERATIVE — each class in MRO gets called exactly ONCE
#
# ── THE SYNTAX ───────────────────────────────────────────
#
#   Modern Python (3.x):
#     super().__init__(args)           ← no arguments needed
#     super().method_name(args)
#
#   Old Python 2 style (still valid but verbose):
#     super(CurrentClass, self).__init__(args)
#     super(ChildClass, self).method(args)
#
#   Always use the modern form (no arguments) in Python 3.
#
# ── WHAT super() RETURNS ─────────────────────────────────
#
#   super() returns a PROXY object (not the parent class itself).
#   The proxy has the SAME interface as the parent but redirects
#   calls to the next class in MRO.
#
#   When you call  super().eat()  inside Dog:
#     1. Python finds Dog's position in the MRO
#     2. Returns a proxy that searches from the NEXT position onward
#     3. That proxy finds and calls Animal.eat
#
# ── THE MOST CONFUSING PART ──────────────────────────────
#
#   Even inside a super() call, METHOD LOOKUP still starts
#   from the ORIGINAL object's class (not from the proxy's class).
#
#   This means:
#     class Animal:
#         def describe(self):
#             return self.sound()    ← 'self' here is still Dog!
#
#     class Dog(Animal):
#         def sound(self):
#             return "Woof"
#
#     d = Dog()
#     d.describe()   # calls Animal.describe, but self.sound() → Dog.sound()!
#
#   This is POLYMORPHISM at work — the object is always the entry point.
#
# ============================================================


# ════════════════════════════════════════════════════════════
# SECTION 1 — Basic super() in single inheritance
# ════════════════════════════════════════════════════════════

print("=" * 60)
print("SECTION 1: Basic super() in Single Inheritance")
print("=" * 60)


class Animal:
    def __init__(self, name: str, sound: str):
        print(f"    Animal.__init__ running | name={name}")
        self.name  = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says: {self.sound}"

    def describe(self) -> str:
        return f"I am {self.name}, an animal"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        print(f"    Dog.__init__ running | name={name}, breed={breed}")

        # super().__init__() calls Animal.__init__ with the right self
        # NOTICE: we don't pass 'self' — super() handles that
        super().__init__(name, "Woof")   # passes name + sound to Animal

        # AFTER super() → parent attributes (self.name) now exist
        self.breed = breed

    def describe(self) -> str:
        # EXTEND parent method — call it, then add more
        parent_desc = super().describe()    # "I am Bruno, an animal"
        return f"{parent_desc} | Breed: {self.breed}"

    def fetch(self) -> str:
        return f"{self.name} fetches the ball!"   # self.name set by Animal.__init__


print("\nCreating Dog:")
d = Dog("Bruno", "Labrador")
# Dog.__init__ running | name=Bruno, breed=Labrador
# Animal.__init__ running | name=Bruno

print(d.speak())     # Bruno says: Woof        ← inherited, not overridden
print(d.describe())  # I am Bruno, an animal | Breed: Labrador
print(d.fetch())     # Bruno fetches the ball!

print(f"\nDog MRO: {[c.__name__ for c in Dog.__mro__]}")
# ['Dog', 'Animal', 'object']


# ════════════════════════════════════════════════════════════
# SECTION 2 — What happens WITHOUT super()
# ════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SECTION 2: What Happens WITHOUT super()")
print("=" * 60)


class BadDog(Animal):
    def __init__(self, name: str, breed: str):
        # NOT calling super().__init__() at all!
        self.breed = breed
        # self.name and self.sound are NEVER set

    def speak(self):
        try:
            return f"{self.name} says: {self.sound}"
        except AttributeError as e:
            return f"Error: {e}"


print("\nBadDog without super().__init__:")
bad = BadDog("Rex", "Husky")
print(bad.speak())
# Error: 'BadDog' object has no attribute 'name'
# Because Animal.__init__ never ran → self.name never set


class HardcodedDog(Animal):
    def __init__(self, name: str, breed: str):
        # Hardcoded parent name — fragile!
        Animal.__init__(self, name, "Woof")   # works but...
        self.breed = breed
        # Problem: if Animal is renamed → must change everywhere
        # Problem: in multiple inheritance → may skip classes in MRO


print("\nHardcoded parent call works for simple cases:")
hd = HardcodedDog("Max", "Poodle")
print(hd.speak())   # Max says: Woof  ← works, but fragile


# ════════════════════════════════════════════════════════════
# SECTION 3 — super() in multi-level inheritance (chain)
# ════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SECTION 3: super() in Multi-Level Inheritance")
print("=" * 60)


class LivingThing:
    def __init__(self):
        print("    LivingThing.__init__")
        self.alive = True

    def breathe(self) -> str:
        return "Breathing"


class Animal2(LivingThing):
    def __init__(self, name: str):
        print(f"    Animal2.__init__ | name={name}")
        super().__init__()    # calls LivingThing.__init__
        self.name = name

    def eat(self) -> str:
        return f"{self.name} is eating"


class Dog2(Animal2):
    def __init__(self, name: str, breed: str):
        print(f"    Dog2.__init__ | name={name}, breed={breed}")
        super().__init__(name)   # calls Animal2.__init__
        self.breed = breed


class PoliceDog(Dog2):
    def __init__(self, name: str, breed: str, badge: str):
        print(f"    PoliceDog.__init__ | name={name}")
        super().__init__(name, breed)   # calls Dog2.__init__
        self.badge = badge

    def duty(self) -> str:
        return f"Officer {self.name} (badge {self.badge}) on duty!"


print("\nCreating PoliceDog (4-level chain):")
officer = PoliceDog("Rex", "German Shepherd", "K9-007")
# PoliceDog.__init__
# Dog2.__init__
# Animal2.__init__
# LivingThing.__init__
# ← each super() cascades to the next, bottom-up

print(f"alive: {officer.alive}")     # True  (from LivingThing)
print(f"name:  {officer.name}")      # Rex   (from Animal2)
print(f"breed: {officer.breed}")     # German Shepherd (from Dog2)
print(officer.breathe())             # Breathing (from LivingThing)
print(officer.eat())                 # Rex is eating (from Animal2)
print(officer.duty())                # Officer Rex... (from PoliceDog)

print(f"\nPoliceDog MRO: {[c.__name__ for c in PoliceDog.__mro__]}")
# [PoliceDog, Dog2, Animal2, LivingThing, object]


# ════════════════════════════════════════════════════════════
# SECTION 4 — super() in multiple inheritance (the critical part)
# ════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SECTION 4: super() in Multiple Inheritance")
print("=" * 60)

#
# WITHOUT super() — broken:
#   class Left(Base):
#       def __init__(self):
#           Base.__init__(self)   ← hardcoded
#
#   class Right(Base):
#       def __init__(self):
#           Base.__init__(self)   ← hardcoded
#
#   class Child(Left, Right):
#       def __init__(self):
#           Left.__init__(self)   ← calls Base.__init__
#           Right.__init__(self)  ← calls Base.__init__ AGAIN! Bug!
#
# WITH super() — cooperative, each class runs ONCE:
#   MRO: Child → Left → Right → Base → object
#   Child.super()  → calls Left
#   Left.super()   → calls Right  (not Base! MRO-aware)
#   Right.super()  → calls Base
#   Base.super()   → calls object
#   Each class runs exactly once — no double-init!


class Base:
    def __init__(self):
        print("    Base.__init__")
        self.base_value = 100

    def info(self) -> str:
        return "Base info"


class Left(Base):
    def __init__(self):
        print("    Left.__init__")
        super().__init__()   # follows MRO → calls Right next (not Base!)
        self.left_value = 10

    def info(self) -> str:
        return f"Left → {super().info()}"


class Right(Base):
    def __init__(self):
        print("    Right.__init__")
        super().__init__()   # follows MRO → calls Base next
        self.right_value = 20

    def info(self) -> str:
        return f"Right → {super().info()}"


class Child(Left, Right):
    def __init__(self):
        print("    Child.__init__")
        super().__init__()   # follows MRO: Left → Right → Base

    def info(self) -> str:
        return f"Child → {super().info()}"


print("\nCreating Child (diamond hierarchy):")
c = Child()
# Child.__init__
# Left.__init__
# Right.__init__
# Base.__init__     ← runs ONCE, not twice

print(f"base_value  = {c.base_value}")    # 100
print(f"left_value  = {c.left_value}")    # 10
print(f"right_value = {c.right_value}")   # 20
print(c.info())
# Child → Left → Right → Base info

print(f"\nChild MRO: {[c.__class__.__mro__[i].__name__ for i in range(len(c.__class__.__mro__))]}")
# [Child, Left, Right, Base, object]

# ── KEY INSIGHT ───────────────────────────────────────────
print("\n── KEY INSIGHT ──")
print("""
  When Left.__init__ calls super().__init__():
    "super" inside Left does NOT mean Base (Left's parent).
    It means the NEXT class after Left in Child's MRO.
    Child's MRO: Child → Left → Right → Base → object
    Next after Left = Right
    So Left.super() calls Right.__init__, not Base.__init__!

  This is COOPERATIVE MULTIPLE INHERITANCE.
  Every class cooperates by calling super() so the next
  class in MRO gets called. The chain completes correctly.
""")


# ════════════════════════════════════════════════════════════
# SECTION 5 — super() with methods (not just __init__)
# ════════════════════════════════════════════════════════════

print("=" * 60)
print("SECTION 5: super() with Regular Methods")
print("=" * 60)


class Logger:
    def log(self, msg: str) -> str:
        return f"[LOG] {msg}"


class TimestampLogger(Logger):
    def log(self, msg: str) -> str:
        base = super().log(msg)         # get Logger's formatted string
        return f"[2026-04-20] {base}"   # add timestamp on top


class PrefixLogger(TimestampLogger):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def log(self, msg: str) -> str:
        base = super().log(msg)          # get TimestampLogger's string
        return f"[{self.prefix}] {base}" # add prefix on top


logger = PrefixLogger("AUTH")
print(logger.log("User logged in"))
# [AUTH] [2026-04-20] [LOG] User logged in
# Each level EXTENDS the one below using super()

print(f"\nPrefixLogger MRO: {[c.__name__ for c in PrefixLogger.__mro__]}")
# [PrefixLogger, TimestampLogger, Logger, object]


# ════════════════════════════════════════════════════════════
# SECTION 6 — Common Mistakes with super()
# ════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SECTION 6: Common Mistakes")
print("=" * 60)

print("""
MISTAKE 1: Not calling super().__init__() at all
  class Dog(Animal):
      def __init__(self, name, breed):
          self.breed = breed    ← Animal.__init__ never called
          # self.name doesn't exist → AttributeError later
  FIX: Always call super().__init__() first

MISTAKE 2: Calling super().__init__() with WRONG arguments
  class Dog(Animal):
      def __init__(self, name, breed):
          super().__init__()     ← missing 'name' → TypeError!
  FIX: Pass all required args: super().__init__(name, ...)

MISTAKE 3: Using hardcoded parent name in multiple inheritance
  class Left(Base):
      def __init__(self):
          Base.__init__(self)   ← skips Right in the MRO!
  FIX: Always use super().__init__()

MISTAKE 4: super() after setting child attributes that depend on parent
  class Dog(Animal):
      def __init__(self, name, breed):
          self.tag = f"{self.name}-{breed}"  ← ERROR! self.name not set yet
          super().__init__(name, 'Woof')
  FIX: Call super().__init__() BEFORE accessing inherited attributes

MISTAKE 5: Returning from __init__
  class Dog(Animal):
      def __init__(self, name):
          return super().__init__(name)  ← __init__ must return None
  FIX: super().__init__(name)  (no return)
""")


# ════════════════════════════════════════════════════════════
# SECTION 7 — Quick Reference
# ════════════════════════════════════════════════════════════

print("=" * 60)
print("SECTION 7: Quick Reference")
print("=" * 60)

print("""
  CALLING PATTERN:
    super().__init__(args)         ← in __init__
    super().method_name(args)      ← in any method
    result = super().method()      ← capture return value

  WHAT super() IS:
    A proxy that searches from the NEXT position in MRO.
    NOT the parent class. NOT the base class. NEXT IN MRO.

  WHEN TO CALL super().__init__():
    ALWAYS in a child class that has its own __init__.
    Call it EARLY — before using any inherited attributes.

  WHEN TO CALL super().method():
    When you want to EXTEND (not fully replace) a parent method.
    You call parent's version + add your own behaviour.

  WHEN NOT TO CALL super().method():
    When you want a FULL REPLACEMENT — skip super() entirely.
    But be careful: Liskov Substitution Principle may be violated.

  MRO RULE (C3 Linearisation):
    Child first → left-to-right parents → then their parents → object
    Check: ClassName.__mro__
""")


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. super() = proxy to the NEXT class in MRO — not "my parent"
# 2. In simple inheritance: NEXT = parent class (looks the same)
# 3. In multiple inheritance: NEXT might be a sibling class!
# 4. Always call super().__init__() — skip it and parent data is lost
# 5. super() makes multiple inheritance COOPERATIVE (each class runs once)
# 6. Hardcoding parent name (Animal.__init__) breaks multiple inheritance
# 7. super().method() = EXTEND parent;  rewrite method = REPLACE parent
# 8. Always check __mro__ when debugging unexpected super() behaviour
