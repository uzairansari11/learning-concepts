# I — Interface Segregation Principle (ISP)

## The Rule

> Clients should not be forced to depend on methods they do not use.

In simple words:
**Don't create one big interface. Create small, focused interfaces.
A class should only implement what it actually needs.**

---

## Real Life Analogy — Job Contract

Imagine you're hired as a **graphic designer**.
Your job contract says you must:
- Design graphics ✅ (your actual job)
- Write code ❌ (not your job)
- Fix servers ❌ (not your job)
- Do customer support ❌ (not your job)

This is a "fat contract" forcing you to sign up for things you don't do.
You end up with methods you have no idea how to implement.

**ISP says: Give each person a contract with ONLY what they need to do.**

---

## Another Analogy — TV Remote

A universal TV remote has 50 buttons.
Your smart TV only uses 20 of them.
Your old DVD player only uses 10.

If you force every device to implement all 50 buttons, most of them would implement
those extra buttons by doing nothing (or crashing).

**ISP says: Create specialized remotes for each device — only the buttons they use.**

---

## Bad Code Example (Violates ISP)

```python
from abc import ABC, abstractmethod

# ONE FAT interface that tries to cover everything
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

    @abstractmethod
    def get_paid(self):
        pass


# Human worker — implements everything fine
class HumanWorker(Worker):
    def work(self):
        print("Human working...")

    def eat(self):
        print("Human eating lunch...")

    def sleep(self):
        print("Human sleeping...")

    def get_paid(self):
        print("Human getting paid...")


# Robot worker — has to implement eat and sleep... but robots don't eat or sleep!
class RobotWorker(Worker):
    def work(self):
        print("Robot working 24/7...")

    def eat(self):
        pass  # Robots don't eat — forced to have this useless method ❌

    def sleep(self):
        pass  # Robots don't sleep — forced to have this useless method ❌

    def get_paid(self):
        pass  # Robots don't get paid — forced to have this useless method ❌
```

### Why is this BAD?

- `RobotWorker` is forced to implement `eat()`, `sleep()`, `get_paid()` even though robots need none of these.
- If you change the `eat()` method signature in the interface, `RobotWorker` is affected for no reason.
- **Classes are being polluted with irrelevant methods.**

---

## Good Code Example (Follows ISP)

```python
from abc import ABC, abstractmethod

# Small, focused interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Payable(ABC):
    @abstractmethod
    def get_paid(self):
        pass


# Human implements ALL relevant interfaces
class HumanWorker(Workable, Eatable, Sleepable, Payable):
    def work(self):
        print("Human working...")

    def eat(self):
        print("Human eating lunch...")

    def sleep(self):
        print("Human sleeping...")

    def get_paid(self):
        print("Human getting paid...")


# Robot ONLY implements what it actually does
class RobotWorker(Workable):
    def work(self):
        print("Robot working 24/7...")


# Usage — each function only requires what it needs
def assign_work(worker: Workable):
    worker.work()

def lunch_break(worker: Eatable):
    worker.eat()


assign_work(HumanWorker())  # ✅
assign_work(RobotWorker())  # ✅

lunch_break(HumanWorker())  # ✅
# lunch_break(RobotWorker())  # ← Type error! Robots can't eat. Caught early.
```

---

## Real World Example — Printers

### BAD (Violates ISP)

```python
class Machine(ABC):
    @abstractmethod
    def print(self, document):
        pass

    @abstractmethod
    def scan(self, document):
        pass

    @abstractmethod
    def fax(self, document):
        pass


class AllInOnePrinter(Machine):
    def print(self, document):
        print(f"Printing {document}")

    def scan(self, document):
        print(f"Scanning {document}")

    def fax(self, document):
        print(f"Faxing {document}")


# Old basic printer can only print — but forced to implement scan and fax
class OldPrinter(Machine):
    def print(self, document):
        print(f"Printing {document}")

    def scan(self, document):
        raise NotImplementedError("This printer cannot scan!")  # ❌

    def fax(self, document):
        raise NotImplementedError("This printer cannot fax!")   # ❌
```

### GOOD (Follows ISP)

```python
from abc import ABC, abstractmethod

class Printable(ABC):
    @abstractmethod
    def print(self, document):
        pass

class Scannable(ABC):
    @abstractmethod
    def scan(self, document):
        pass

class Faxable(ABC):
    @abstractmethod
    def fax(self, document):
        pass


# Old printer only needs to print
class OldPrinter(Printable):
    def print(self, document):
        print(f"Printing {document}")  # ✅ Only what it can do


# All-in-one implements everything it can
class AllInOnePrinter(Printable, Scannable, Faxable):
    def print(self, document):
        print(f"Printing {document}")

    def scan(self, document):
        print(f"Scanning {document}")

    def fax(self, document):
        print(f"Faxing {document}")
```

---

## Real World Example — API Interfaces (TypeScript)

### BAD

```typescript
interface UserService {
    getUser(id: string): User;
    createUser(data: UserData): User;
    deleteUser(id: string): void;
    updateUser(id: string, data: Partial<UserData>): User;
    sendWelcomeEmail(user: User): void;       // Email concern mixed in
    generateReport(userId: string): Report;  // Reporting concern mixed in
    exportToCSV(users: User[]): string;       // Export concern mixed in
}
```

### GOOD

```typescript
interface UserReader {
    getUser(id: string): User;
}

interface UserWriter {
    createUser(data: UserData): User;
    updateUser(id: string, data: Partial<UserData>): User;
    deleteUser(id: string): void;
}

interface UserNotifier {
    sendWelcomeEmail(user: User): void;
}

interface UserReporter {
    generateReport(userId: string): Report;
    exportToCSV(users: User[]): string;
}

// Read-only admin dashboard only needs UserReader
class AdminDashboard implements UserReader {
    getUser(id: string): User { ... }
}

// Email service only needs UserNotifier
class EmailService implements UserNotifier {
    sendWelcomeEmail(user: User): void { ... }
}

// Full user management implements reader + writer
class UserManagementService implements UserReader, UserWriter {
    ...
}
```

---

## Signs of ISP Violations

1. **Empty method implementations** — a class implements an interface method with `pass` or `{}` or `throw new Error("Not implemented")`

2. **Classes that implement interfaces but only use 2 out of 10 methods**

3. **A fat interface** that has methods from completely different domains (printing + faxing + emailing + reporting)

4. **Cascading changes** — changing one method in an interface forces changes in many unrelated classes

---

## ISP vs SRP — What's the Difference?

They're related but different:

| | SRP | ISP |
|---|---|---|
| Focus | Classes | Interfaces |
| Rule | A class should have one reason to change | Don't force classes to implement methods they don't use |
| Problem it solves | Fat classes | Fat interfaces |

A fat interface often leads to SRP violations — if a class implements a fat interface,
it ends up with multiple responsibilities.

---

## Summary

| | Violates ISP | Follows ISP |
|---|---|---|
| Interface size | One giant interface | Many small, focused interfaces |
| Class methods | Many empty/useless methods | Only methods the class actually uses |
| Change impact | Changing interface affects many unrelated classes | Changes only affect relevant classes |
| Flexibility | Low — everything coupled to one interface | High — compose only what you need |

**The golden rule: Prefer many small specific interfaces over one large general interface.**
