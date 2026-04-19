# O — Open/Closed Principle (OCP)

## The Rule

> Software entities (classes, functions, modules) should be:
> - **OPEN** for extension (you can add new behavior)
> - **CLOSED** for modification (you don't change existing code)

In simple words:
**Add new features by ADDING new code, not by EDITING old code.**

---

## Real Life Analogy

Think of a **smartphone**.

Your phone's OS is closed — you can't change its core code.
But it's open — you can install new apps to extend its functionality.

Want to add a new feature? Install an app. Don't rebuild the phone.

**OCP says: Design your code like a phone — extendable without rebuilding.**

---

## Another Analogy — Electrical Sockets

A power socket is:
- **Closed for modification** — you don't rewire the wall for every device
- **Open for extension** — any device with the right plug can use it

You can plug in a phone, laptop, TV, fan — all without changing the socket.

---

## Bad Code Example (Violates OCP)

Imagine you're building a payment system.

```python
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit_card":
            print(f"Processing credit card payment of {amount}")
        elif payment_type == "paypal":
            print(f"Processing PayPal payment of {amount}")
        elif payment_type == "stripe":
            print(f"Processing Stripe payment of {amount}")
        # Every new payment method = edit this file again!
```

### Why is this BAD?

Every time you add a new payment method (Apple Pay, Crypto, Bank Transfer):
- You EDIT this existing class
- You risk breaking credit card and PayPal logic while adding Crypto
- This class grows endlessly with `if/elif` chains
- You violate OCP: you're MODIFYING instead of EXTENDING

**The existing, tested code is at risk every single time.**

---

## Good Code Example (Follows OCP)

```python
from abc import ABC, abstractmethod

# The ABSTRACT base — this never changes
class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass


# Each payment type is a NEW class — existing code untouched
class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        print(f"Processing credit card payment of {amount}")


class PayPalPayment(PaymentMethod):
    def process(self, amount):
        print(f"Processing PayPal payment of {amount}")


class StripePayment(PaymentMethod):
    def process(self, amount):
        print(f"Processing Stripe payment of {amount}")


# Adding Apple Pay? Just add a NEW class. Touch NOTHING else.
class ApplePayPayment(PaymentMethod):
    def process(self, amount):
        print(f"Processing Apple Pay payment of {amount}")


# The processor works with ANY payment method
class PaymentProcessor:
    def process(self, payment: PaymentMethod, amount):
        payment.process(amount)


# Usage
processor = PaymentProcessor()
processor.process(CreditCardPayment(), 100)
processor.process(ApplePayPayment(), 200)
```

### Why is this GOOD?

- Added Apple Pay? Created a new class. **Zero changes to existing code.**
- `CreditCardPayment` is completely untouched.
- `PaymentProcessor` is completely untouched.
- **Old code is safe. New feature is isolated.**

---

## Real World Example — Shape Area Calculator

### BAD (Violates OCP)

```python
class AreaCalculator:
    def calculate(self, shape, dimensions):
        if shape == "circle":
            return 3.14 * dimensions["radius"] ** 2
        elif shape == "rectangle":
            return dimensions["width"] * dimensions["height"]
        elif shape == "triangle":
            return 0.5 * dimensions["base"] * dimensions["height"]
        # Adding hexagon? Edit this class again!
```

### GOOD (Follows OCP)

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

# Adding Hexagon? New class only. Nothing else changes.
class Hexagon(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return (3 * (3 ** 0.5) / 2) * self.side ** 2


class AreaCalculator:
    def calculate(self, shape: Shape):
        return shape.area()  # Works for ALL shapes, forever


calc = AreaCalculator()
print(calc.calculate(Circle(5)))       # 78.5
print(calc.calculate(Rectangle(4, 6))) # 24
print(calc.calculate(Hexagon(3)))      # works without touching AreaCalculator
```

---

## OCP in JavaScript / TypeScript (Frontend Example)

### BAD

```javascript
function renderNotification(type, message) {
    if (type === 'success') {
        return `<div class="green">${message}</div>`;
    } else if (type === 'error') {
        return `<div class="red">${message}</div>`;
    } else if (type === 'warning') {
        return `<div class="yellow">${message}</div>`;
    }
    // New notification type = edit this function
}
```

### GOOD

```javascript
const notificationRenderers = {
    success: (msg) => `<div class="green">${msg}</div>`,
    error:   (msg) => `<div class="red">${msg}</div>`,
    warning: (msg) => `<div class="yellow">${msg}</div>`,
};

// Adding "info" type? Just ADD to the map. No existing code touched.
notificationRenderers.info = (msg) => `<div class="blue">${msg}</div>`;

function renderNotification(type, message) {
    return notificationRenderers[type](message);
}
```

---

## How to Spot OCP Violations

Look for these warning signs:

1. **Long if/else or switch chains** that check types
   ```python
   if type == "A": ...
   elif type == "B": ...
   elif type == "C": ...  # ← every new type = modify this
   ```

2. **Comments like "add new case here"** in the middle of a function

3. **You're editing an existing class** every time a new business requirement comes in

4. **Tests for old features break** when you add new features

---

## The Key Insight

The trick is to identify **what changes** and **what stays the same**.

- **What stays the same** → make it abstract / an interface (closed)
- **What changes** → make it a concrete implementation (open to extend)

| Part | Role | Should be |
|------|------|-----------|
| `PaymentMethod` (abstract) | contract that never changes | Closed for modification |
| `CreditCardPayment`, `PayPalPayment` | specific implementations | Open for extension |

---

## Summary

| | Violates OCP | Follows OCP |
|---|---|---|
| Adding new feature | Edit existing class | Add new class |
| Risk to old code | High (can break existing logic) | Zero (old code untouched) |
| if/else chains | Grows every time | Never grows |
| Testing | Re-test everything on each change | Only test new code |

**The golden rule: When requirements change, ADD new code. Don't EDIT old code.**
