# ============================================================
# LESSON 11: Composition vs Inheritance
# ============================================================
#
# ── THE TWO RELATIONSHIPS ────────────────────────────────
#
#   IS-A  (Inheritance):
#     "A Dog IS-A Animal"
#     The child IS a specialised version of the parent.
#     Child inherits all parent behaviour automatically.
#
#   HAS-A  (Composition):
#     "A Car HAS-A Engine"
#     One class CONTAINS an instance of another class.
#     The outer class DELEGATES work to the inner object.
#
# ── THE RULE ─────────────────────────────────────────────
#
#   PREFER COMPOSITION OVER INHERITANCE.
#   Use inheritance ONLY when IS-A is genuinely true and stable.
#
# ── WHY PREFER COMPOSITION? ─────────────────────────────
#
#   Problem with inheritance:
#     1. TIGHT COUPLING — child depends on parent internals
#     2. FRAGILE BASE CLASS — change parent → may break children
#     3. INFLEXIBLE — behaviour locked at class-definition time
#     4. HIERARCHY EXPLOSION — FlyingSwimmingBird? DomesticFlyingBird?
#
#   With composition:
#     1. LOOSE COUPLING — swap any component independently
#     2. FLEXIBLE — change behaviour at RUNTIME
#     3. TESTABLE — mock individual components in tests
#     4. REUSABLE — share components across unrelated classes
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   INHERITANCE approach for a PC:
#     class PCWithIntelCPU(IntelCPU, Samsung16GBRAM, SeagateSSD):
#     ← New PC model = new class. Can't swap parts. Very rigid.
#
#   COMPOSITION approach for a PC:
#     class PC:
#         def __init__(self, cpu, ram, storage):
#             self.cpu = cpu          ← HAS-A CPU
#             self.ram = ram          ← HAS-A RAM
#             self.storage = storage  ← HAS-A Storage
#     ← Swap any part at any time. Flexible.
#
# ── WHEN TO USE INHERITANCE ─────────────────────────────
#
#   ✅ Genuine IS-A: Dog IS-A Animal, ElectricCar IS-A Vehicle
#   ✅ Child needs MOST of the parent's behaviour
#   ✅ You want polymorphism across a family of types
#   ✅ Hierarchy is STABLE (won't change much)
#
# ── WHEN TO USE COMPOSITION ─────────────────────────────
#
#   ✅ HAS-A relationship: Car HAS-A Engine
#   ✅ You want to SWAP behaviour at runtime
#   ✅ Reusing code across UNRELATED classes
#   ✅ Building complex objects from simple parts
#   ✅ Hierarchy would get too deep (>3 levels → code smell)
#
# ── WHEN NOT TO USE DEEP INHERITANCE ────────────────────
#
#   ❌ Inheritance just to reuse ONE method → use a function or Mixin
#   ❌ Deep chains (A→B→C→D→E) → fragile, hard to understand
#   ❌ Overriding parent methods to do nothing → clear design smell
#
# ============================================================


# ════════════════════════════════════════════════════════════
# PART 1 — Problem with Inheritance for mixed behaviours
# ════════════════════════════════════════════════════════════

print("── Inheritance Limitation ──")

# How do you model a DUCK that can BOTH fly and swim?
# Inheritance forces you to pick one:

class FlyingAnimal:
    def move(self): return "Flying"

class SwimmingAnimal:
    def move(self): return "Swimming"

# Multiple inheritance works but gets messy fast:
# class Duck(FlyingAnimal, SwimmingAnimal)?
# What if you also need RunningAnimal, ClimbingAnimal?
# The hierarchy explodes.

# COMPOSITION SOLUTION: separate behaviour into components


# ════════════════════════════════════════════════════════════
# PART 2 — Strategy Pattern via Composition
# ════════════════════════════════════════════════════════════

print("\n── Composition: Swappable Behaviours ──")

# Step 1: Define behaviours as separate classes
class FlyBehaviour:
    def move(self) -> str: return "Soaring through the sky"

class SwimBehaviour:
    def move(self) -> str: return "Gliding through water"

class WalkBehaviour:
    def move(self) -> str: return "Walking on land"

class NoMoveBehaviour:
    def move(self) -> str: return "Cannot move"


# Step 2: Animal HAS-A movement behaviour (injected via __init__)
class Animal:
    def __init__(self, name: str, move_behaviour):
        self.name = name
        self._move = move_behaviour   # composition: HAS-A

    def move(self) -> str:
        return f"{self.name}: {self._move.move()}"

    def set_move(self, new_behaviour):
        # RUNTIME swap — impossible with inheritance
        self._move = new_behaviour
        return f"{self.name}'s movement updated."

    def __str__(self):
        return f"Animal({self.name})"


eagle  = Animal("Eagle",   FlyBehaviour())
fish   = Animal("Fish",    SwimBehaviour())
turtle = Animal("Turtle",  SwimBehaviour())
penguin = Animal("Penguin", WalkBehaviour())

print(eagle.move())     # Eagle: Soaring through the sky
print(fish.move())      # Fish: Gliding through water
print(penguin.move())   # Penguin: Walking on land

# Duck can fly AND swim — switch behaviour at runtime
duck = Animal("Duck", FlyBehaviour())
print(duck.move())      # Duck: Soaring through the sky

# Duck jumped into water — swap behaviour at runtime
print(duck.set_move(SwimBehaviour()))
print(duck.move())      # Duck: Gliding through water


# ════════════════════════════════════════════════════════════
# PART 3 — Composition for complex objects (PC example)
# ════════════════════════════════════════════════════════════

print("\n── PC Composition ──")


class CPU:
    def __init__(self, brand: str, cores: int, ghz: float):
        self.brand = brand
        self.cores = cores
        self.ghz   = ghz

    def process(self, task: str) -> str:
        return f"[{self.brand} {self.cores}-core @{self.ghz}GHz] Processing: {task}"

    def __str__(self) -> str:
        return f"CPU({self.brand}, {self.cores}-core, {self.ghz}GHz)"


class RAM:
    def __init__(self, size_gb: int, speed_mhz: int = 3200):
        self.size_gb   = size_gb
        self.speed_mhz = speed_mhz

    def load(self, program: str) -> str:
        return f"[{self.size_gb}GB RAM @{self.speed_mhz}MHz] Loading: {program}"

    def __str__(self) -> str:
        return f"RAM({self.size_gb}GB, {self.speed_mhz}MHz)"


class Storage:
    def __init__(self, size_tb: float, kind: str = "SSD"):
        self.size_tb = size_tb
        self.kind    = kind

    def read(self, file: str) -> str:
        return f"[{self.kind} {self.size_tb}TB] Reading: {file}"

    def write(self, file: str) -> str:
        return f"[{self.kind} {self.size_tb}TB] Writing: {file}"

    def __str__(self) -> str:
        return f"Storage({self.kind}, {self.size_tb}TB)"


class PC:
    # PC HAS-A CPU,  HAS-A RAM,  HAS-A Storage
    # Dependencies are INJECTED — not hardcoded inside the class
    def __init__(self, name: str, cpu: CPU, ram: RAM, storage: Storage):
        self.name    = name
        self.cpu     = cpu
        self.ram     = ram
        self.storage = storage

    def boot(self):
        print(f"\n[{self.name}] Booting...")
        print(self.storage.read("OS Kernel"))
        print(self.ram.load("Operating System"))
        print(self.cpu.process("Boot sequence complete"))

    def run(self, app: str):
        print(f"\n[{self.name}] Running: {app}")
        print(self.ram.load(app))
        print(self.cpu.process(app))

    def save(self, filename: str):
        print(self.storage.write(filename))

    def upgrade_ram(self, new_ram: RAM):
        print(f"[{self.name}] Upgrading RAM: {self.ram} → {new_ram}")
        self.ram = new_ram   # just swap the component!

    def upgrade_cpu(self, new_cpu: CPU):
        print(f"[{self.name}] Upgrading CPU: {self.cpu} → {new_cpu}")
        self.cpu = new_cpu

    def specs(self) -> str:
        return (
            f"PC: {self.name}\n"
            f"  CPU    : {self.cpu}\n"
            f"  RAM    : {self.ram}\n"
            f"  Storage: {self.storage}"
        )


# Build a PC by composing components
gaming_pc = PC(
    name    = "Gaming Rig",
    cpu     = CPU("Intel i9", 16, 5.0),
    ram     = RAM(32, 4800),
    storage = Storage(2.0, "NVMe SSD"),
)

print(gaming_pc.specs())
gaming_pc.boot()
gaming_pc.run("Cyberpunk 2077")
gaming_pc.save("savegame.dat")

# Upgrade components independently — no need to change PC class
gaming_pc.upgrade_ram(RAM(64, 6000))
gaming_pc.upgrade_cpu(CPU("Intel i9-Ultra", 24, 6.0))
gaming_pc.run("Next-gen game")


# ════════════════════════════════════════════════════════════
# PART 4 — Comparing the two approaches side-by-side
# ════════════════════════════════════════════════════════════

print("\n── Side-by-side: Report Generator ──")

# INHERITANCE approach
class BaseReport:
    def generate(self) -> str: return "Base report data"
    def save(self): return "Saving report..."

class PDFReport(BaseReport):
    def save(self): return "Saving as PDF"

class EmailReport(BaseReport):
    def save(self): return "Sending via email"

# Problem: what about PDFEmailReport? EmailCSVReport?
# Hierarchy explodes. Each combo needs a new class.


# COMPOSITION approach
class ReportData:
    def generate(self) -> str: return "Report: Q1 Sales — 1.2M PKR"

class PDFSaver:
    def save(self, data: str) -> str: return f"PDF saved: {data}"

class EmailSender:
    def save(self, data: str) -> str: return f"Email sent: {data}"

class CSVExporter:
    def save(self, data: str) -> str: return f"CSV exported: {data}"

class Report:
    def __init__(self, data_source, saver):
        self.data_source = data_source
        self.saver = saver

    def run(self) -> str:
        data = self.data_source.generate()
        return self.saver.save(data)


# Any combination without new classes
pdf_report   = Report(ReportData(), PDFSaver())
email_report = Report(ReportData(), EmailSender())
csv_report   = Report(ReportData(), CSVExporter())

print(pdf_report.run())     # PDF saved: Report: Q1 Sales...
print(email_report.run())   # Email sent: Report: Q1 Sales...
print(csv_report.run())     # CSV exported: Report: Q1 Sales...

# Change saver at runtime
pdf_report.saver = EmailSender()
print(pdf_report.run())     # Email sent: ...  (changed without new class)


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. IS-A → Inheritance;  HAS-A → Composition
# 2. Prefer Composition — it's more flexible and less fragile
# 3. Composition allows swapping behaviour at RUNTIME
# 4. Inheritance = tight coupling; Composition = loose coupling
# 5. Hierarchy deeper than 3 levels = code smell → use Composition
# 6. Composition = Dependency Injection (pass components via __init__)
# 7. Test Composition by mocking the injected components independently
