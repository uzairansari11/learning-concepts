# ============================================================
# LESSON 10: Class Methods & Static Methods
# ============================================================
#
# ── THE THREE KINDS OF METHODS ───────────────────────────
#
#   Python has three types of methods inside a class.
#   They differ in WHAT they receive as the first argument
#   and WHAT they have access to.
#
#   1. INSTANCE METHOD   →  def method(self)
#      Receives the INSTANCE (object) as first arg.
#      Has access to: instance data (self.x) + class data (self.__class__)
#      Most common type.
#
#   2. CLASS METHOD      →  @classmethod
#                           def method(cls)
#      Receives the CLASS ITSELF as first arg (not the instance).
#      Has access to: class data, class variables
#      Cannot access instance data (there may be no instance).
#
#   3. STATIC METHOD     →  @staticmethod
#                           def method()
#      Receives NOTHING — no self, no cls.
#      Just a plain function that lives inside the class namespace.
#      Has access to: nothing (unless you explicitly pass it)
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   Think of a RESTAURANT:
#
#   Instance method → a SPECIFIC WAITER serving YOUR table
#                     (knows about your order, your table)
#
#   Class method    → the RESTAURANT MANAGER who knows about
#                     the whole restaurant (total tables, menu)
#                     but not any specific customer
#
#   Static method   → a UTILITY FUNCTION posted on the wall
#                     (conversion chart, tax formula)
#                     doesn't know about the restaurant or customers
#
# ── WHY CLASS METHODS? ───────────────────────────────────
#
#   The #1 use case: ALTERNATIVE CONSTRUCTORS (factory methods)
#
#   Python's __init__ can only have one signature.
#   But what if you want to create objects from:
#     - a string:  "2026-04-20"
#     - a dict:    {"year": 2026, "month": 4, "day": 20}
#     - a timestamp: 1713600000
#
#   Use @classmethod to create multiple "factory" methods,
#   each with its own parsing logic.
#
#   Also used for:
#     - Accessing/modifying class variables
#     - Factory methods in subclasses (cls() instead of ClassName())
#
# ── WHY STATIC METHODS? ──────────────────────────────────
#
#   Group utility/helper functions LOGICALLY with a class,
#   without requiring an instance or the class itself.
#
#   Could be a module-level function — but conceptually belongs here.
#   Examples: validation helpers, conversion formulas, constants logic.
#
# ── WHEN TO USE WHICH ────────────────────────────────────
#
#   ✅ Instance method → when you need self (most things)
#   ✅ Class method    → alternative constructors, class-level state
#   ✅ Static method   → utility logic with no state dependency
#
#   ❌ Don't use @classmethod when you only need the class name
#      inside — just use the class name directly
#   ❌ Don't use @staticmethod if the logic truly needs the class
#      — it should be a @classmethod or module function
#
# ============================================================


class Employee:

    # ── CLASS VARIABLES ────────────────────────────────
    company_name = "PyTech Solutions"
    _total_employees = 0
    _raise_percentage = 10   # default raise %

    # ── Instance Method ───────────────────────────────
    def __init__(self, name: str, department: str, salary: float):
        self.name = name
        self.department = department
        self.salary = salary
        Employee._total_employees += 1

    def describe(self) -> str:
        return (
            f"{self.name} | {self.department} | "
            f"Salary: {self.salary:,.0f} PKR"
        )

    def apply_raise(self) -> str:
        # Reads the class-level raise percentage
        increase = self.salary * (Employee._raise_percentage / 100)
        self.salary += increase
        return f"{self.name}'s new salary: {self.salary:,.0f} PKR"

    def __str__(self) -> str:
        return f"Employee({self.name}, {self.department})"

    # ── Class Methods ─────────────────────────────────
    #
    # Use 'cls' (convention) instead of 'self'.
    # 'cls' == the class itself (Employee, or a subclass if called on one).
    # This makes factory methods work correctly with inheritance.

    @classmethod
    def from_string(cls, emp_string: str) -> "Employee":
        """Alternative constructor: parse 'Name-Department-Salary'."""
        # cls() instead of Employee() → works correctly in subclasses too
        parts = emp_string.split("-")
        name, dept, salary = parts[0], parts[1], float(parts[2])
        return cls(name, dept, salary)

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        """Alternative constructor: create from a dictionary."""
        return cls(data["name"], data["department"], data["salary"])

    @classmethod
    def get_total(cls) -> int:
        """Access class-level state."""
        return cls._total_employees

    @classmethod
    def set_raise(cls, percentage: float):
        """Modify class-level raise — affects ALL employees."""
        if percentage < 0:
            raise ValueError("Raise percentage cannot be negative.")
        cls._raise_percentage = percentage
        print(f"Company raise updated to {percentage}% for all employees")

    # ── Static Methods ────────────────────────────────
    #
    # No self, no cls — just a plain function in class namespace.
    # Cannot access class or instance data unless passed explicitly.

    @staticmethod
    def is_valid_salary(salary: float) -> bool:
        """Utility: check if a salary value is valid."""
        return isinstance(salary, (int, float)) and salary > 0

    @staticmethod
    def tax_on_salary(salary: float) -> float:
        """Utility: calculate estimated tax (15%)."""
        return salary * 0.15

    @staticmethod
    def salary_grade(salary: float) -> str:
        """Utility: classify salary into grade."""
        if salary < 50_000:   return "Grade C"
        if salary < 100_000:  return "Grade B"
        return "Grade A"


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

print("── Instance Methods ──")
e1 = Employee("Uzair", "Engineering", 120_000)
e2 = Employee("Sara",  "Marketing",    85_000)

print(e1.describe())    # Uzair | Engineering | Salary: 120,000 PKR
print(e2.describe())

print(e1.apply_raise())  # Uzair's new salary: 132,000 PKR (10% raise)


print("\n── Class Methods (Alternative Constructors) ──")

# Create from a string (CSV-like format)
e3 = Employee.from_string("Ahmed-HR-75000")
print(e3.describe())    # Ahmed | HR | Salary: 75,000 PKR

# Create from a dict (e.g., from a JSON API response)
e4 = Employee.from_dict({
    "name": "Fatima",
    "department": "Finance",
    "salary": 95000
})
print(e4.describe())    # Fatima | Finance | Salary: 95,000 PKR

# Class-level state
print(f"Total employees: {Employee.get_total()}")   # 4

# Modify class-level raise for EVERYONE
Employee.set_raise(15)
print(e2.apply_raise())   # Sara's new salary: 97,750 PKR (15% raise)


print("\n── Static Methods ──")

# Can be called on the class OR an instance (but class is cleaner)
print(Employee.is_valid_salary(50000))    # True
print(Employee.is_valid_salary(-100))     # False
print(Employee.tax_on_salary(120000))     # 18000.0
print(Employee.salary_grade(120000))      # Grade A
print(Employee.salary_grade(45000))       # Grade C

# Also callable on instance (but unnecessary)
print(e1.is_valid_salary(e1.salary))      # True


# ════════════════════════════════════════════════════════════
# CLASS METHOD + INHERITANCE: the power of cls
# ════════════════════════════════════════════════════════════

print("\n── cls in subclasses ──")


class Manager(Employee):
    def __init__(self, name: str, department: str, salary: float, team_size: int):
        super().__init__(name, department, salary)
        self.team_size = team_size

    def describe(self) -> str:
        return f"{super().describe()} | Team: {self.team_size} people"


# from_string() inherited from Employee but cls == Manager
m = Manager.from_string("Bilal-Engineering-200000")
print(type(m))          # <class '__main__.Manager'>
print(m)                # Employee(Bilal, Engineering)

# If from_string used Employee() instead of cls():
# → would create an Employee, not a Manager (wrong!)
# That's why we always use cls() in @classmethod


# ════════════════════════════════════════════════════════════
# REAL-WORLD: Date class factory
# ════════════════════════════════════════════════════════════

print("\n── Date factory methods ──")


class Date:
    def __init__(self, day: int, month: int, year: int):
        self.day, self.month, self.year = day, month, year

    @classmethod
    def today(cls) -> "Date":
        import datetime
        t = datetime.date.today()
        return cls(t.day, t.month, t.year)

    @classmethod
    def from_iso(cls, iso: str) -> "Date":
        """Parse '2026-04-20' → Date."""
        year, month, day = map(int, iso.split("-"))
        return cls(day, month, year)

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def __str__(self):
        return f"{self.day:02d}/{self.month:02d}/{self.year}"


print(Date.today())                   # current date
print(Date.from_iso("2026-04-20"))    # 20/04/2026
print(Date.is_leap_year(2024))        # True
print(Date.is_leap_year(2025))        # False


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Using @staticmethod when you need cls
#   @staticmethod
#   def create(name):
#       return Employee(name, ...)    ← hardcoded class name
#   Problem: in a subclass, this creates Employee not Manager
#   Fix: use @classmethod with cls()
#
# MISTAKE 2: Using @classmethod when @staticmethod is enough
#   @classmethod
#   def validate(cls, value):   ← cls never used inside!
#   If you don't use cls, make it a @staticmethod
#
# MISTAKE 3: Calling @classmethod with self explicitly
#   Employee.from_string(self, "...")   ← WRONG
#   Python passes cls automatically, just like self for instance methods


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Instance method  → self   → operates on ONE object
# 2. Class method     → cls    → operates on the CLASS (factory, state)
# 3. Static method    → nothing → utility with no state dependency
# 4. Use @classmethod for alternative constructors (from_string, from_dict)
# 5. Always use cls() in @classmethod for correct subclass support
# 6. @staticmethod = conceptually belongs in the class but needs no state
# 7. Static methods are callable on both class and instance
