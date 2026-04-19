# SOLID Principles — Quick Cheat Sheet

---

## One-Line Memory Tricks

| Principle | Remember it as |
|-----------|----------------|
| **S**ingle Responsibility | "One class, one job. One reason to change." |
| **O**pen/Closed | "Add new code, don't edit old code." |
| **L**iskov Substitution | "Child must not surprise you. Swap it in, nothing breaks." |
| **I**nterface Segregation | "Don't force useless methods on a class." |
| **D**ependency Inversion | "Depend on interfaces, not concrete classes." |

---

## The 5 Questions to Ask While Coding

Before you write or review a class, ask:

1. **SRP** → "Does this class do MORE than one thing?"
   - If yes → split it.

2. **OCP** → "To add this feature, am I editing existing code?"
   - If yes → add a new class/extension instead.

3. **LSP** → "If I replace the parent with this child, does anything break?"
   - If yes → fix the hierarchy.

4. **ISP** → "Am I forcing this class to implement methods it doesn't use?"
   - If yes → break the interface into smaller ones.

5. **DIP** → "Is my high-level logic importing a concrete class directly?"
   - If yes → introduce an abstraction (interface) between them.

---

## Red Flags (Code Smells That Indicate SOLID Violation)

| Code Smell | Which Principle is Violated |
|---|---|
| Class has 500+ lines with unrelated methods | SRP |
| Long if/elif/switch chains based on type | OCP |
| `isinstance()` checks before calling methods | LSP |
| Methods that just `pass` or `raise NotImplementedError` | ISP or LSP |
| `self.db = MySQLDatabase()` inside a class | DIP |
| Class imports change every time a new feature is added | OCP / SRP |
| Tests require a real database/email server | DIP |

---

## SOLID Applied Together — Mini Example

```python
from abc import ABC, abstractmethod


# SRP: Each class has one job
# ISP: Interfaces are small and focused
# DIP: Depend on abstractions

class MessageSender(ABC):              # Abstraction (DIP)
    @abstractmethod
    def send(self, to: str, body: str):
        pass

class EmailSender(MessageSender):      # OCP: extend by adding new class
    def send(self, to, body):
        print(f"Email to {to}: {body}")

class SMSSender(MessageSender):        # OCP: another extension
    def send(self, to, body):
        print(f"SMS to {to}: {body}")


class NotificationLogger(ABC):         # ISP: separate small interface
    @abstractmethod
    def log(self, message: str):
        pass

class ConsoleLogger(NotificationLogger):
    def log(self, message):
        print(f"[LOG] {message}")


# SRP: Only handles sending notifications (not logging, not DB)
# DIP: Depends on abstractions, not concrete classes
class NotificationService:
    def __init__(self, sender: MessageSender, logger: NotificationLogger):
        self.sender = sender
        self.logger = logger

    def notify(self, recipient: str, message: str):
        self.sender.send(recipient, message)
        self.logger.log(f"Notified {recipient}")


# Assemble dependencies outside (DIP / Dependency Injection)
service = NotificationService(
    sender=EmailSender(),
    logger=ConsoleLogger()
)
service.notify("ali@test.com", "Your order shipped!")

# Swap to SMS with ZERO changes to NotificationService
service2 = NotificationService(
    sender=SMSSender(),
    logger=ConsoleLogger()
)
service2.notify("+92-300-1234567", "Your order shipped!")
```

---

## SOLID Benefits Summary

| Benefit | How SOLID helps |
|---|---|
| **Easy to test** | DIP lets you inject fakes/mocks |
| **Safe to extend** | OCP means new features don't break old ones |
| **Easy to understand** | SRP means each class is small and focused |
| **Easy to swap** | DIP + LSP means implementations are interchangeable |
| **No wasted code** | ISP means no empty/useless method implementations |

---

## When SOLID Gets Overused

SOLID is a tool, not a religion.

- A 50-line script doesn't need 10 classes
- A simple CRUD endpoint doesn't need 5 interfaces
- Over-engineering is a real problem

**Apply SOLID when:**
- The codebase will grow
- Multiple developers work on it
- Features change frequently
- Testability matters

**Skip it when:**
- It's a small one-off script
- You're prototyping
- The abstraction costs more than it saves

---

*The best code is code that reads like a story — each piece does one clear thing,
and everything fits together without surprises.*
