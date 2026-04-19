# ============================================================
# LESSON 4: Single Inheritance
# ============================================================
#
# ── WHAT IS INHERITANCE? ─────────────────────────────────
#
#   Inheritance is a mechanism where a CHILD class automatically
#   receives all the attributes and methods of a PARENT class,
#   without having to rewrite them.
#
#   The child can:
#     - USE the parent's methods as-is
#     - ADD new methods and attributes (extension)
#     - REPLACE (override) parent methods with custom behaviour
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   A SMARTPHONE inherits from a PHONE:
#     - It can still make calls (inherited)
#     - It adds: camera, apps, touchscreen (extension)
#     - It changes: dialling (override — uses touchscreen not buttons)
#
# ── THE IS-A RELATIONSHIP ────────────────────────────────
#
#   Only use inheritance when the IS-A relationship is TRUE:
#     ✅ Dog IS-A Animal       → correct
#     ✅ Car IS-A Vehicle      → correct
#     ❌ Car HAS-A Engine      → this is Composition (Lesson 11)
#     ❌ AdminUser IS-A Logger → wrong — should be a Mixin (Lesson 12)
#
# ── WHY DOES INHERITANCE EXIST? ─────────────────────────
#
#   CODE REUSE — without inheritance:
#     class Dog:  def eat(): ...  def sleep(): ...  def breathe(): ...
#     class Cat:  def eat(): ...  def sleep(): ...  def breathe(): ...
#     ← duplicated 100%
#
#   With inheritance:
#     class Animal: def eat(): ...  def sleep(): ...
#     class Dog(Animal): ...   ← gets eat and sleep for free
#     class Cat(Animal): ...   ← same
#
# ── TERMINOLOGY ──────────────────────────────────────────
#
#   Parent / Base / Super class → the class being inherited FROM
#   Child  / Derived / Sub class → the class that INHERITS
#
# ── WHEN TO USE INHERITANCE ─────────────────────────────
#
#   ✅ Clear IS-A relationship exists
#   ✅ Child shares most of the parent's behaviour
#   ✅ You want polymorphism (swap objects of different types)
#   ✅ Reducing code duplication across related classes
#
# ── WHEN NOT TO USE INHERITANCE ─────────────────────────
#
#   ❌ The relationship is HAS-A → use Composition instead
#   ❌ You just want to reuse one method → use a function or Mixin
#   ❌ Deep hierarchies (A→B→C→D→E) → fragile and hard to maintain
#   ❌ Forcing unrelated classes into a hierarchy
#
# ── SYNTAX ───────────────────────────────────────────────
#
#   class Child(Parent):
#       def __init__(self, ...):
#           Parent.__init__(self, ...)  ← initialise parent's attributes
#           self.extra = ...            ← add child's own attributes
#
# ============================================================


# ── Parent Class ──────────────────────────────────────────

class Animal:
    """Base class — all animals share these behaviours."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age  = age
        self.is_alive = True

    def eat(self) -> str:
        return f"{self.name} is eating."

    def sleep(self) -> str:
        return f"{self.name} is sleeping. Zzz..."

    def breathe(self) -> str:
        return f"{self.name} is breathing."

    def info(self) -> str:
        return (
            f"Name  : {self.name}\n"
            f"Age   : {self.age}\n"
            f"Type  : {self.__class__.__name__}"   # shows actual subclass name
        )

    def __str__(self) -> str:
        # self.__class__.__name__ → gives "Dog" or "Cat", not "Animal"
        return f"{self.__class__.__name__}(name={self.name}, age={self.age})"


# ── Child Class: Dog ─────────────────────────────────────

class Dog(Animal):
    """
    Dog IS-A Animal.
    Inherits: eat, sleep, breathe, info, __str__
    Adds:     breed, bark, fetch
    """

    def __init__(self, name: str, age: int, breed: str):
        # Step 1: call parent's __init__ to set name and age
        # If you skip this, self.name and self.age won't exist!
        Animal.__init__(self, name, age)

        # Step 2: add Dog-specific attributes
        self.breed = breed

    # NEW methods only Dogs have
    def bark(self) -> str:
        return f"{self.name} says: WOOF!"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetched the {item}! Good dog!"

    def info(self) -> str:
        # EXTEND parent's info — get parent output then add breed
        parent_info = super().info()    # calls Animal.info(self)
        return f"{parent_info}\nBreed : {self.breed}"


# ── Child Class: Cat ─────────────────────────────────────

class Cat(Animal):
    """
    Cat IS-A Animal.
    Inherits: eat, sleep, breathe, __str__
    Adds:     indoor, meow, purr
    """

    def __init__(self, name: str, age: int, indoor: bool = True):
        Animal.__init__(self, name, age)
        self.indoor = indoor

    def meow(self) -> str:
        return f"{self.name} says: Meow~"

    def purr(self) -> str:
        return f"{self.name} is purring contentedly... purrr"

    def info(self) -> str:
        parent_info = super().info()
        location = "Indoor" if self.indoor else "Outdoor"
        return f"{parent_info}\nType  : {location} cat"


# ── Child Class: Fish ────────────────────────────────────

class Fish(Animal):
    """
    Fish IS-A Animal.
    Inherits: eat, sleep
    Adds:     water_type, swim
    Overrides: breathe  (fish breathe differently)
    """

    def __init__(self, name: str, age: int, water_type: str = "freshwater"):
        Animal.__init__(self, name, age)
        self.water_type = water_type

    def swim(self) -> str:
        return f"{self.name} glides through the {self.water_type}."

    def breathe(self) -> str:
        # OVERRIDE — fish don't breathe air, they extract oxygen from water
        return f"{self.name} absorbs oxygen through its gills."


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

dog  = Dog("Bruno", 3, "Labrador")
cat  = Cat("Whiskers", 2, indoor=True)
fish = Fish("Nemo", 1, "saltwater")

print("── Inherited methods ──")
print(dog.eat())       # Bruno is eating.     ← from Animal
print(dog.sleep())     # Bruno is sleeping.   ← from Animal
print(cat.eat())       # Whiskers is eating.  ← from Animal

print("\n── Child-only methods ──")
print(dog.bark())           # Bruno says: WOOF!
print(dog.fetch("ball"))    # Bruno fetched the ball!
print(cat.meow())           # Whiskers says: Meow~
print(cat.purr())           # Whiskers is purring...
print(fish.swim())          # Nemo glides through the saltwater.

print("\n── Overridden method ──")
print(dog.breathe())        # Bruno is breathing.        ← inherited (no override)
print(fish.breathe())       # Nemo absorbs oxygen...    ← overridden

print("\n── Extended info() ──")
print(dog.info())
print()
print(cat.info())

print("\n── __str__ (inherited and dynamic) ──")
print(dog)    # Dog(name=Bruno, age=3)    ← Animal.__str__ with correct class name
print(cat)    # Cat(name=Whiskers, age=2)
print(fish)   # Fish(name=Nemo, age=1)


# ════════════════════════════════════════════════════════════
# CHECKING THE RELATIONSHIP
# ════════════════════════════════════════════════════════════

print("\n── isinstance / issubclass ──")
print(isinstance(dog, Dog))      # True  — dog is a Dog
print(isinstance(dog, Animal))   # True  — dog IS-A Animal
print(isinstance(dog, Cat))      # False — dog is not a Cat

print(issubclass(Dog, Animal))   # True
print(issubclass(Cat, Animal))   # True
print(issubclass(Dog, Cat))      # False

# Every class inherits from object (Python's root class)
print(issubclass(Animal, object))  # True

# Inspect the inheritance chain
print(Dog.__bases__)             # (<class '__main__.Animal'>,)
print(Dog.__mro__)               # [Dog, Animal, object]


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Forgetting to call parent __init__
#   class Dog(Animal):
#       def __init__(self, name, breed):
#           self.breed = breed       ← Animal.__init__ never called!
#           # self.name doesn't exist → AttributeError when you call eat()
#
# MISTAKE 2: Calling parent init AFTER setting child attributes is fine,
#   but be careful if parent __init__ calls a method overridden by the child.
#
# MISTAKE 3: Using inheritance for HAS-A relationships
#   class Car(Engine):  ← WRONG — Car is not an Engine
#   class Car:
#       def __init__(self):
#           self.engine = Engine()  ← RIGHT (Composition)


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Inheritance = child gets all parent attributes and methods free
# 2. Only use it for genuine IS-A relationships
# 3. Always call Parent.__init__() (or super().__init__()) in child
# 4. Child can ADD new methods (extension)
# 5. Child can REPLACE parent methods (override — Lesson 5)
# 6. Child can EXTEND parent methods with super() (Lesson 5)
# 7. isinstance(child_obj, ParentClass) → True
# 8. Every class ultimately inherits from Python's `object`
