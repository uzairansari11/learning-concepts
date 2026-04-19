# D — Dependency Inversion Principle (DIP)

## The Rule

> 1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
> 2. Abstractions should not depend on details. Details should depend on abstractions.

In simple words:
**Your important business logic should NOT care about the specific tools you use.
It should talk to an abstraction (interface), not a concrete class.**

---

## Real Life Analogy — Power Outlets

Your laptop (high-level) doesn't care if the power comes from:
- A wall socket
- A generator
- A solar panel
- A power bank

It just knows it needs a "power source" with a standard plug interface.

The laptop depends on the **plug standard (abstraction)**, not on the **specific power source (concrete)**.

If you hardwire your laptop to the wall socket, you can't use it anywhere else.

**DIP says: Connect through standards (interfaces), not through specific implementations.**

---

## Another Analogy — A Manager and His Team

A Manager (high-level) shouldn't care if work is done by:
- A full-time employee
- A freelancer
- An automated bot

The manager just calls `doWork()` on whoever/whatever is assigned.

If the manager directly calls `John.writeCode()`, when John leaves, the manager is broken.
If the manager calls `worker.doWork()`, any worker can be swapped in.

---

## Bad Code Example (Violates DIP)

```python
# LOW-LEVEL module — a specific database implementation
class MySQLDatabase:
    def save(self, data):
        print(f"Saving '{data}' to MySQL database")

    def find(self, id):
        print(f"Finding record {id} in MySQL")
        return {"id": id, "data": "some data"}


# HIGH-LEVEL module — business logic
class UserService:
    def __init__(self):
        # DIRECTLY depends on MySQLDatabase (concrete class)
        self.db = MySQLDatabase()  # ❌ Hardwired!

    def create_user(self, user_data):
        # Business logic
        print("Validating user...")
        self.db.save(user_data)  # Tightly coupled to MySQL

    def get_user(self, user_id):
        return self.db.find(user_id)


service = UserService()
service.create_user("Ali")
```

### Why is this BAD?

- `UserService` is **hardwired** to `MySQLDatabase`.
- Tomorrow you want to switch to PostgreSQL, MongoDB, or use an in-memory DB for testing?
  - You have to **modify** `UserService`.
- Want to test `UserService` without a real database?
  - You can't. It always creates a real `MySQLDatabase`.
- **High-level business logic is at the mercy of low-level infrastructure.**

---

## Good Code Example (Follows DIP)

```python
from abc import ABC, abstractmethod

# ABSTRACTION — the interface both sides depend on
class DatabaseInterface(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def find(self, id):
        pass


# LOW-LEVEL module — depends on the abstraction
class MySQLDatabase(DatabaseInterface):
    def save(self, data):
        print(f"Saving '{data}' to MySQL database")

    def find(self, id):
        print(f"Finding record {id} in MySQL")
        return {"id": id, "data": "mysql data"}


# Another LOW-LEVEL module — also depends on the abstraction
class MongoDatabase(DatabaseInterface):
    def save(self, data):
        print(f"Saving '{data}' to MongoDB")

    def find(self, id):
        print(f"Finding record {id} in MongoDB")
        return {"id": id, "data": "mongo data"}


# For testing — a fake database that doesn't touch real storage
class InMemoryDatabase(DatabaseInterface):
    def __init__(self):
        self.storage = {}

    def save(self, data):
        self.storage[len(self.storage)] = data
        print(f"Saved to memory: {data}")

    def find(self, id):
        return self.storage.get(id)


# HIGH-LEVEL module — depends on ABSTRACTION, not concrete class
class UserService:
    def __init__(self, db: DatabaseInterface):  # ✅ Depends on interface
        self.db = db  # Injected from outside

    def create_user(self, user_data):
        print("Validating user...")
        self.db.save(user_data)

    def get_user(self, user_id):
        return self.db.find(user_id)


# In production: use MySQL
service = UserService(MySQLDatabase())
service.create_user("Ali")

# Switch to MongoDB? Just swap the dependency
service = UserService(MongoDatabase())
service.create_user("Ali")

# In tests: use in-memory — no real DB needed!
service = UserService(InMemoryDatabase())
service.create_user("Ali")
```

### Why is this GOOD?

- `UserService` doesn't know or care what database is used.
- Swap MySQL → MongoDB? Change ONE LINE where you inject it.
- Testing? Inject `InMemoryDatabase`. No real DB, no network, blazing fast.
- **Business logic is clean. Infrastructure is swappable.**

---

## This technique has a name: Dependency Injection (DI)

DIP is the **principle** — "depend on abstractions."
DI is the **technique** — "inject the concrete dependency from outside."

```python
# The dependency is INJECTED (passed in), not created inside
service = UserService(MySQLDatabase())  # Injection happens here
```

The class doesn't create its own dependencies — it receives them.
This is called **Constructor Injection**.

---

## Real World Example — Notification System

### BAD (Violates DIP)

```python
class EmailSender:
    def send(self, message, recipient):
        print(f"Sending email to {recipient}: {message}")


class OrderService:
    def __init__(self):
        self.notifier = EmailSender()  # ❌ Hardwired to email

    def place_order(self, order):
        print(f"Order {order} placed!")
        self.notifier.send("Your order is placed!", order['email'])
        # What if we want to also send SMS? Push notification?
        # We'd have to edit this class every time.
```

### GOOD (Follows DIP)

```python
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str):
        pass


class EmailNotification(NotificationService):
    def send(self, message, recipient):
        print(f"Email to {recipient}: {message}")


class SMSNotification(NotificationService):
    def send(self, message, recipient):
        print(f"SMS to {recipient}: {message}")


class PushNotification(NotificationService):
    def send(self, message, recipient):
        print(f"Push to {recipient}: {message}")


class OrderService:
    def __init__(self, notifier: NotificationService):  # ✅ Depends on abstraction
        self.notifier = notifier

    def place_order(self, order):
        print(f"Order {order['id']} placed!")
        self.notifier.send("Your order is placed!", order['contact'])


# Use email in production
order_service = OrderService(EmailNotification())
order_service.place_order({"id": 1, "contact": "ali@email.com"})

# Switch to SMS — zero changes to OrderService
order_service = OrderService(SMSNotification())
order_service.place_order({"id": 2, "contact": "+92-300-1234567"})
```

---

## Real World Example — Logger

```python
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self, message: str):
        pass

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"[LOG] {message}")

class FileLogger(Logger):
    def log(self, message):
        with open("app.log", "a") as f:
            f.write(f"[LOG] {message}\n")

class CloudLogger(Logger):
    def log(self, message):
        print(f"Sending to CloudWatch: {message}")


class PaymentProcessor:
    def __init__(self, logger: Logger):
        self.logger = logger  # ✅ Injected

    def process(self, amount):
        self.logger.log(f"Processing payment of {amount}")
        # ... payment logic


# Development: log to console
processor = PaymentProcessor(ConsoleLogger())

# Production: log to cloud
processor = PaymentProcessor(CloudLogger())

# Testing: log to file for inspection
processor = PaymentProcessor(FileLogger())
```

---

## DIP in Frameworks (Spring, Django, etc.)

Most modern frameworks are built on DIP.

**Django REST Framework:**
```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Injected behavior
    pagination_class = PageNumberPagination  # Injected behavior
```

You don't hardcode authentication logic inside the view.
You inject it via `permission_classes`. That's DIP in action.

**Angular (TypeScript):**
```typescript
@Injectable()
export class UserService {
    constructor(private http: HttpClient) {}  // HttpClient injected by Angular's DI system
}
```

---

## DIP vs DI — Key Difference

| | DIP (Principle) | DI (Technique) |
|---|---|---|
| What it is | A design rule | A coding pattern to achieve DIP |
| What it says | Depend on abstractions | Pass dependencies from outside |
| Example | Use `DatabaseInterface` not `MySQL` | Constructor takes a `DatabaseInterface` |

DI is how you implement DIP.

---

## The Dependency Direction

```
WITHOUT DIP:
  UserService  ──depends on──▶  MySQLDatabase
  (high-level)                  (low-level)

WITH DIP:
  UserService  ──depends on──▶  DatabaseInterface  ◀──depends on──  MySQLDatabase
  (high-level)                  (abstraction)                        (low-level)
```

Both high-level and low-level modules depend on the abstraction in the middle.
The **direction of dependency is inverted** — that's where the name comes from.

---

## Summary

| | Violates DIP | Follows DIP |
|---|---|---|
| Dependency creation | Class creates its own dependencies (`self.db = MySQL()`) | Dependencies injected from outside |
| Coupling | Tightly coupled to specific implementations | Loosely coupled to abstractions |
| Testability | Hard — real databases required | Easy — inject mock/fake objects |
| Swappability | Change implementation = edit business logic | Change implementation = swap injected class |

**The golden rule: High-level business logic should never know the name of a concrete class.**
