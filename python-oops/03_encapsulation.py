# ============================================================
# LESSON 3: Encapsulation
# ============================================================
#
# ── WHAT IS ENCAPSULATION? ───────────────────────────────
#
#   Encapsulation means BUNDLING data and the methods that
#   operate on that data together, AND controlling how that
#   data is accessed or modified from outside the class.
#
#   Two parts:
#     1. Bundling  → data + methods live in one class
#     2. Hiding    → some data is hidden from direct outside access
#
# ── REAL-WORLD ANALOGY ──────────────────────────────────
#
#   Think of a BANK ACCOUNT:
#     - You can't reach into the vault and grab money directly
#     - You go through the COUNTER (methods: deposit, withdraw)
#     - The counter validates your request before acting
#
#   The balance is HIDDEN.  The methods are the INTERFACE.
#
# ── WHY DOES ENCAPSULATION EXIST? ───────────────────────
#
#   Without it:
#     account.balance = -99999     ← anyone can corrupt your data
#
#   With it:
#     account.balance = -99999     ← setter raises ValueError
#
#   Benefits:
#     ✅ Prevents invalid state (no negative balance)
#     ✅ You can change internal implementation without breaking callers
#     ✅ Makes debugging easier — only ONE place changes the data
#     ✅ Enforces business rules at the data level
#
# ── HOW PYTHON DOES IT ───────────────────────────────────
#
#   Python uses NAMING CONVENTIONS (not hard enforcement):
#
#   self.name    → PUBLIC
#                  Anyone can read/write freely.
#
#   self._name   → PROTECTED (single underscore)
#                  Convention: "this is internal, don't use outside"
#                  Python does NOT block access — it's a warning to devs.
#                  Respected by tools and good programmers.
#
#   self.__name  → PRIVATE (double underscore)
#                  Python applies NAME MANGLING:
#                  self.__balance  →  stored as  self._ClassName__balance
#                  Makes accidental access harder (not impossible).
#                  NOT truly private like Java/C++ — Python trusts you.
#
# ── WHAT IS @property? ───────────────────────────────────
#
#   @property lets you expose a CONTROLLED INTERFACE for
#   reading, writing, or deleting a private attribute.
#
#   You access it like an attribute (no parentheses),
#   but it actually calls a method underneath.
#
#   This means you can ADD VALIDATION without changing
#   how the caller interacts with the attribute.
#
# ── WHEN TO USE ENCAPSULATION ────────────────────────────
#
#   ✅ When an attribute needs validation before being set
#   ✅ When you want computed properties (area, full_name)
#   ✅ When internal implementation may change in the future
#   ✅ For sensitive data (passwords, account balance)
#
# ── WHEN NOT TO ──────────────────────────────────────────
#
#   ❌ Don't over-protect simple data that needs no validation
#      (making a property for every attribute is boilerplate)
#   ❌ Don't use __ just to "look secure" — it confuses readers
#      without real benefit if no validation is involved
#
# ============================================================


class BankAccount:

    def __init__(self, owner: str, initial_balance: float):
        # PUBLIC — owner's name, freely accessible
        self.owner = owner

        # PROTECTED — internal metadata, external code should avoid
        self._bank_name = "PyBank"
        self._transaction_history: list[str] = []

        # PRIVATE — name-mangled, must go through property
        # Stored as self._BankAccount__balance internally
        self.__balance = initial_balance
        self._log(f"Account created with balance {initial_balance}")

    # ── Internal helper (protected) ───────────────────────
    def _log(self, message: str):
        self._transaction_history.append(message)

    # ── @property: the GETTER ────────────────────────────
    #
    # Accessed as:  account.balance   (no parentheses)
    # Python sees the @property decorator and calls this method.
    # The caller doesn't know or care it's a method — clean interface.
    @property
    def balance(self) -> float:
        return self.__balance

    # ── @balance.setter: the SETTER ──────────────────────
    #
    # Called when:  account.balance = 5000
    # Lets us VALIDATE before actually setting the value.
    # Without this, @property is READ-ONLY (no setter = can't assign).
    @balance.setter
    def balance(self, amount: float):
        if not isinstance(amount, (int, float)):
            raise TypeError("Balance must be a number.")
        if amount < 0:
            raise ValueError("Balance cannot be negative.")
        old = self.__balance
        self.__balance = amount
        self._log(f"Balance set from {old} to {amount}")

    # ── @balance.deleter ─────────────────────────────────
    #
    # Called when:  del account.balance
    # Rarely used but lets you define cleanup behaviour.
    @balance.deleter
    def balance(self):
        self._log("Account closed — balance deleted")
        del self.__balance

    # ── Computed property (no backing attribute) ─────────
    #
    # full_summary doesn't store anything — it computes on demand.
    # Caller uses it as if it were a plain attribute.
    @property
    def full_summary(self) -> str:
        return (
            f"Account Owner : {self.owner}\n"
            f"Bank          : {self._bank_name}\n"
            f"Balance       : {self.__balance:,.2f} PKR"
        )

    # ── Business logic methods ────────────────────────────
    def deposit(self, amount: float) -> str:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount
        self._log(f"Deposited {amount}")
        return f"Deposited {amount:,.2f}. New balance: {self.__balance:,.2f}"

    def withdraw(self, amount: float) -> str:
        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")
        if amount > self.__balance:
            raise ValueError(f"Insufficient funds. Balance: {self.__balance:,.2f}")
        self.__balance -= amount
        self._log(f"Withdrew {amount}")
        return f"Withdrew {amount:,.2f}. New balance: {self.__balance:,.2f}"

    def statement(self) -> str:
        history = "\n  ".join(self._transaction_history)
        return f"Transaction History:\n  {history}"

    def __str__(self):
        return f"BankAccount(owner={self.owner}, balance={self.__balance:,.2f})"


# ════════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════════

acc = BankAccount("Uzair", 10000)

# ── Public access ────────────────────────────────────────
print(acc.owner)         # Uzair — free to read

# ── Protected access ─────────────────────────────────────
print(acc._bank_name)    # PyBank — accessible but bad practice
                         # A linter/IDE will warn about this

# ── Private: direct access FAILS ─────────────────────────
try:
    print(acc.__balance)
except AttributeError as e:
    print(f"AttributeError: {e}")   # object has no attribute '__balance'

# Python actually stores it as _BankAccount__balance (name mangling)
print(acc._BankAccount__balance)   # 10000 — possible but NEVER do this in real code

# ── Property getter — clean interface ─────────────────────
print(acc.balance)       # 10000

# ── Property setter — with validation ────────────────────
acc.balance = 15000
print(acc.balance)       # 15000

# ── Setter rejects invalid values ─────────────────────────
try:
    acc.balance = -500
except ValueError as e:
    print(e)             # Balance cannot be negative.

try:
    acc.balance = "hello"
except TypeError as e:
    print(e)             # Balance must be a number.

# ── Business methods ──────────────────────────────────────
print(acc.deposit(5000))       # Deposited 5,000.00. New balance: 20,000.00
print(acc.withdraw(3000))      # Withdrew 3,000.00. New balance: 17,000.00

try:
    acc.withdraw(999999)
except ValueError as e:
    print(e)                   # Insufficient funds...

# ── Computed property ─────────────────────────────────────
print(acc.full_summary)

# ── Transaction log ───────────────────────────────────────
print(acc.statement())

# ── Deleter ───────────────────────────────────────────────
del acc.balance   # Account closed — balance deleted


# ════════════════════════════════════════════════════════════
# COMMON MISTAKES
# ════════════════════════════════════════════════════════════
#
# MISTAKE 1: Using __ everywhere without reason
#   self.__name is fine, but don't do it for every attribute.
#   Use _ (protected) for "internal" and __ only when you truly
#   need name-mangling to avoid subclass conflicts.
#
# MISTAKE 2: Property without setter then trying to assign
#   @property
#   def x(self): return self._x
#   obj.x = 5  →  AttributeError: can't set attribute
#   Add @x.setter if you want to allow assignment.
#
# MISTAKE 3: Bypassing encapsulation in tests
#   Accessing obj._BankAccount__balance in tests defeats the purpose.
#   Test through the public interface instead.


# ════════════════════════════════════════════════════════════
# KEY TAKEAWAYS
# ════════════════════════════════════════════════════════════
#
# 1. Encapsulation = bundle data + methods + control access
# 2. _ (single)  → protected by convention, still accessible
# 3. __ (double) → name-mangled, harder to access accidentally
# 4. @property   → read attribute like a field, but runs a method
# 5. @x.setter   → intercept assignment and validate
# 6. Python doesn't enforce privacy — it trusts the programmer
# 7. Use encapsulation to enforce business rules, not just to hide
