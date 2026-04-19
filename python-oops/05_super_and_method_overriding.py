# ============================================================
# LESSON 5: super() and Method Overriding
# ============================================================
#
# ── WHAT IS METHOD OVERRIDING? ──────────────────────────
#
#   When a child class defines a method with the SAME NAME as
#   one in the parent class, the child's version REPLACES the
#   parent's for that class and its instances.
#
#   Python's method lookup (MRO) always checks the child first.
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   A COMPANY has a generic process() method:
#     "Log the request, handle it, save results"
#
#   The REFUND_TEAM overrides process():
#     "Check eligibility, reverse the payment, notify customer"
#
#   Same name, same call from outside — completely different
#   behaviour inside.
#
# ── WHAT IS super()? ────────────────────────────────────
#
#   super() returns a PROXY OBJECT that delegates method calls
#   to the PARENT class (according to MRO order).
#
#   Two main uses:
#     1. super().__init__(...)  → call parent's constructor
#     2. super().method(...)    → call parent's version of a method
#                                 (so you can EXTEND it, not just replace)
#
# ── super() vs ParentClass.method() ─────────────────────
#
#   Animal.__init__(self, name)  → EXPLICIT, hardcoded parent name
#   super().__init__(name)       → DYNAMIC, follows MRO
#
#   In simple single inheritance, both work.
#   In multiple inheritance, ONLY super() works correctly.
#   ALWAYS prefer super().
#
# ── WHEN TO OVERRIDE ────────────────────────────────────
#
#   ✅ Child has genuinely different behaviour for a method
#   ✅ You want to EXTEND (add to) the parent's behaviour
#   ✅ You want to RESTRICT or change what the parent does
#
# ── WHEN NOT TO OVERRIDE ────────────────────────────────
#
#   ❌ If you're just calling super() and doing nothing else
#      → pointless override, delete it
#   ❌ If the override breaks the expected contract (Liskov principle)
#      → callers expect consistent behaviour from the base type
#
# ── LISKOV SUBSTITUTION PRINCIPLE ───────────────────────
#
#   A child object must be usable wherever a parent object is
#   expected — without breaking the program.
#
#   If your override changes the fundamental contract
#   (e.g., withdraw() now deposits instead), you're violating LSP.
#
# ============================================================


# ── Base Class ────────────────────────────────────────────

class Vehicle:
    """Base for all vehicles."""

    def __init__(self, brand: str, model: str, speed_kmh: int):
        self.brand     = brand
        self.model     = model
        self.speed_kmh = speed_kmh
        self.is_running = False

    def start(self) -> str:
        self.is_running = True
        return f"{self.brand} {self.model} engine started."

    def stop(self) -> str:
        self.is_running = False
        return f"{self.brand} {self.model} stopped."

    def move(self) -> str:
        if not self.is_running:
            return f"{self.brand} {self.model} is not running. Start it first."
        return f"{self.brand} {self.model} moving at {self.speed_kmh} km/h."

    def fuel_type(self) -> str:
        return "Unknown fuel"

    def specs(self) -> str:
        return (
            f"Brand   : {self.brand}\n"
            f"Model   : {self.model}\n"
            f"Speed   : {self.speed_kmh} km/h\n"
            f"Fuel    : {self.fuel_type()}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.brand} {self.model})"


# ── Child: Car — OVERRIDES fuel_type ─────────────────────

class Car(Vehicle):
    def __init__(self, brand: str, model: str, speed_kmh: int, doors: int):
        # super().__init__ calls Vehicle.__init__ — DRY, MRO-safe
        super().__init__(brand, model, speed_kmh)
        self.doors = doors   # Car-specific attribute

    # FULL OVERRIDE — replaces parent's version entirely
    def fuel_type(self) -> str:
        return "Petrol / Diesel"

    # NEW method — doesn't exist in parent
    def honk(self) -> str:
        return f"{self.brand}: Beep beep!"

    # EXTENDING specs() — reuse parent output, add car-specific info
    def specs(self) -> str:
        parent_specs = super().specs()          # gets Vehicle's version
        return f"{parent_specs}\nDoors   : {self.doors}"


# ── Child: ElectricCar — overrides again at another level ─

class ElectricCar(Car):
    def __init__(self, brand: str, model: str, speed_kmh: int,
                 doors: int, battery_kwh: int):
        super().__init__(brand, model, speed_kmh, doors)  # calls Car.__init__
        self.battery_kwh = battery_kwh

    # OVERRIDE again — more specific than Car
    def fuel_type(self) -> str:
        return "Electric (lithium-ion battery)"

    # EXTEND move() — add silent-drive message after parent's output
    def move(self) -> str:
        base = super().move()   # calls Car → Vehicle.move()
        return f"{base} [Silent electric drive]"

    # EXTEND specs()
    def specs(self) -> str:
        parent_specs = super().specs()          # Car's specs (which includes Vehicle's)
        return f"{parent_specs}\nBattery : {self.battery_kwh} kWh"

    def charge(self) -> str:
        return f"{self.brand} {self.model} charging {self.battery_kwh} kWh..."


# ── Child: Bicycle — overrides start/stop (no engine) ────

class Bicycle(Vehicle):
    def __init__(self, brand: str, model: str, speed_kmh: int, gears: int):
        super().__init__(brand, model, speed_kmh)
        self.gears = gears

    # Override — bicycle has no engine start/stop
    def start(self) -> str:
        self.is_running = True
        return f"{self.brand} {self.model} rider is pedalling."

    def stop(self) -> str:
        self.is_running = False
        return f"{self.brand} {self.model} brakes applied."

    def fuel_type(self) -> str:
        return "Human power"


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

car = Car("Toyota", "Camry", 200, 4)
ev  = ElectricCar("Tesla", "Model S", 250, 4, 100)
bike = Bicycle("Trek", "FX3", 40, 21)

print("── fuel_type() at each level ──")
v = Vehicle("Generic", "X1", 0)
print(v.fuel_type())    # Unknown fuel      ← Vehicle
print(car.fuel_type())  # Petrol / Diesel   ← Car (overrides)
print(ev.fuel_type())   # Electric          ← ElectricCar (overrides again)
print(bike.fuel_type()) # Human power       ← Bicycle (overrides)

print("\n── start() override in Bicycle ──")
print(car.start())      # Toyota Camry engine started.  ← inherited from Vehicle
print(bike.start())     # Trek FX3 rider is pedalling.  ← overridden

print("\n── move() extended in ElectricCar ──")
car.start()
ev.start()
print(car.move())       # Toyota Camry moving at 200 km/h.
print(ev.move())        # Tesla Model S moving at 250 km/h. [Silent electric drive]

print("\n── specs() extended through chain ──")
print(ev.specs())
# Brand   : Tesla
# Model   : Model S
# Speed   : 250 km/h
# Fuel    : Electric (lithium-ion battery)
# Doors   : 4
# Battery : 100 kWh

print("\n── __str__ inherited and dynamic ──")
print(car)    # Car(Toyota Camry)
print(ev)     # ElectricCar(Tesla Model S)
print(bike)   # Bicycle(Trek FX3)

# MRO shows exactly who gets called for each method
print("\n── MRO ──")
print(ElectricCar.__mro__)
# [ElectricCar, Car, Vehicle, object]


# ════════════════════════════════════════════════════════════
# VISUALISING super() CALL CHAIN
# ════════════════════════════════════════════════════════════
#
# ev.specs()
#   → ElectricCar.specs()
#       → super().specs()   (calls Car.specs)
#           → super().specs()  (calls Vehicle.specs)
#               → self.fuel_type()  ← Python looks up from ElectricCar!
#                   → ElectricCar.fuel_type() ← most-derived wins
#
# This is why MRO matters: even inside super() calls,
# attribute lookup still starts from the actual object's class.


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Not calling super().__init__ in child
#   class Car(Vehicle):
#       def __init__(self, brand, doors):
#           self.doors = doors     ← Vehicle.__init__ never called!
#           # self.brand, self.speed DON'T EXIST → AttributeError
#
# MISTAKE 2: Using parent name directly instead of super()
#   Vehicle.__init__(self, brand, model, speed)  → brittle
#   If you rename Vehicle → MotorVehicle, all children break.
#   super().__init__(...) adapts automatically.
#
# MISTAKE 3: super() without __init__ arguments
#   super().__init__()   ← missing required args → TypeError


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Method override = child redefines a parent method by same name
# 2. Python always calls the MOST DERIVED (child) version first
# 3. super().__init__() → initialise parent ALWAYS
# 4. super().method() → EXTEND parent logic instead of replacing it
# 5. Prefer super() over ParentClass.method(self) — it's MRO-safe
# 6. Use @override (Python 3.12+) to document intentional overrides
# 7. Liskov: child override must not break expected behaviour
