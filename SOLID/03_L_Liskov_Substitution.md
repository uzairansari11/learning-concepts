# L — Liskov Substitution Principle (LSP)

## The Rule

> If S is a subtype of T, then objects of type T may be replaced with objects of type S
> without altering any of the desirable properties of the program.

In simple words:
**A child class must be fully usable wherever the parent class is used.
No surprises. No broken behavior.**

---

## Real Life Analogy — Cars

Imagine you rent a car. The rental company says "we'll give you a car."
You expect a car that:
- Has 4 wheels
- Has a steering wheel
- Accelerates when you press the gas
- Brakes when you press the brake

Now they hand you a "SportsCar" (child of Car). You press the gas — it works.
You press the brake — it works. Great!

Now they hand you a "RocketCar" (also child of Car).
You press the brake — it EJECTS you out of the seat.

**RocketCar violated LSP.** It broke the expected behavior of a Car.
The child class didn't behave like the parent promised.

---

## Another Analogy — Employees

You have an `Employee` class. Every employee can:
- `work()` — do their job
- `take_break()` — take a lunch break

You create a `Contractor` subclass. Contractors can `work()` but legally they cannot
use the company's break room (they can't `take_break()`).

If you throw an exception in `Contractor.take_break()`, you've violated LSP.
Because wherever you use an Employee, a Contractor might blow up.

---

## Bad Code Example (Violates LSP)

The classic example: Rectangle and Square.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def area(self):
        return self.width * self.height


# A Square IS-A Rectangle mathematically... but is it in code?
class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Square must have equal sides

    def set_height(self, height):
        self.width = height  # Overrides width too!
        self.height = height


# Code that works with Rectangle
def resize_and_calculate(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(10)
    print(rect.area())  # We EXPECT 50 (5 * 10)


r = Rectangle(2, 3)
resize_and_calculate(r)  # Prints 50 ✅

s = Square(2, 2)
resize_and_calculate(s)  # Prints 100 (10 * 10) ❌ SURPRISE!
```

### Why is this BAD?

You passed a `Square` where a `Rectangle` was expected.
- You set width = 5, height = 10
- But Square silently changed width to 10 too
- The area is 100, not 50
- **The behavior is broken. LSP is violated.**

A Square is mathematically a Rectangle, but in this code model it behaves differently.
**The IS-A relationship in math doesn't always translate to IS-A in code.**

---

## Good Code Example (Follows LSP)

```python
from abc import ABC, abstractmethod

# Abstract base — only what ALL shapes share
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


# Now both work correctly as a Shape
def print_area(shape: Shape):
    print(shape.area())

print_area(Rectangle(5, 10))  # 50 ✅
print_area(Square(5))          # 25 ✅
```

No surprises. Both `Rectangle` and `Square` fulfill the `Shape` contract perfectly.

---

## Real World Example — Birds

### BAD (Violates LSP)

```python
class Bird:
    def fly(self):
        print("Flying!")

class Eagle(Bird):
    def fly(self):
        print("Eagle soaring!")  # ✅ Makes sense

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # ❌ VIOLATION!


def make_bird_fly(bird: Bird):
    bird.fly()  # Works for Eagle, CRASHES for Penguin


make_bird_fly(Eagle())   # ✅
make_bird_fly(Penguin()) # ❌ Exception!
```

### GOOD (Follows LSP)

```python
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def eat(self):
        pass

class FlyingBird(Bird):
    @abstractmethod
    def fly(self):
        pass

class SwimmingBird(Bird):
    @abstractmethod
    def swim(self):
        pass

class Eagle(FlyingBird):
    def eat(self):
        print("Eagle eating...")

    def fly(self):
        print("Eagle soaring!")

class Penguin(SwimmingBird):
    def eat(self):
        print("Penguin eating...")

    def swim(self):
        print("Penguin swimming!")


def make_fly(bird: FlyingBird):
    bird.fly()  # Only called on birds that CAN fly

make_fly(Eagle())   # ✅ Eagle soaring!
# make_fly(Penguin()) would be a TYPE ERROR — caught at compile time
```

Now the hierarchy reflects reality. Penguins are never passed to `make_fly`.

---

## Real World Example — User Authentication

### BAD (Violates LSP)

```python
class User:
    def login(self, password):
        print("Logged in with password")

    def reset_password(self, new_password):
        print(f"Password reset to {new_password}")


class GuestUser(User):
    def login(self, password):
        print("Logged in as guest (no password needed)")

    def reset_password(self, new_password):
        raise Exception("Guests cannot reset passwords!")  # ❌ VIOLATION


def handle_user(user: User):
    user.login("pass123")
    user.reset_password("newpass")  # CRASHES for GuestUser!
```

### GOOD (Follows LSP)

```python
from abc import ABC, abstractmethod

class BaseUser(ABC):
    @abstractmethod
    def login(self):
        pass

class AuthenticatedUser(BaseUser):
    def login(self):
        print("Logged in with credentials")

    def reset_password(self, new_password):
        print(f"Password reset to {new_password}")

class GuestUser(BaseUser):
    def login(self):
        print("Logged in as guest")
    # No reset_password — guests don't have passwords. That's fine.


def login_user(user: BaseUser):
    user.login()  # Works for ALL user types ✅
```

---

## The LSP Checklist

A subclass is LSP-compliant if:

| Rule | Example |
|------|---------|
| It doesn't throw exceptions the parent doesn't throw | `Square.set_height()` should not throw if `Rectangle.set_height()` doesn't |
| It doesn't weaken preconditions | Parent accepts any number → child shouldn't suddenly require positive-only |
| It doesn't strengthen postconditions | Parent returns a list → child shouldn't return null |
| It doesn't override methods to do nothing or throw | `Penguin.fly()` raising an exception ❌ |
| Behavior is consistent with parent's contract | `Square` changing width when you set height ❌ |

---

## How to Spot LSP Violations

1. **Empty overrides** — a child class overrides a method with nothing or a comment "not supported"
2. **Throwing NotImplementedException** in a subclass
3. **`isinstance()` checks everywhere** — if you're checking the type to handle special cases, LSP is broken
   ```python
   if isinstance(bird, Penguin):
       bird.swim()
   else:
       bird.fly()   # ← This smell means your hierarchy is wrong
   ```

4. **Surprising behavior** — calling a method on a child gives a different result than you'd expect from the parent

---

## Summary

| | Violates LSP | Follows LSP |
|---|---|---|
| Substitutability | Child breaks when used as parent | Child works perfectly as parent |
| Surprises | Unexpected exceptions or results | Predictable, consistent behavior |
| isinstance checks | Needed everywhere | Never needed |
| Hierarchy | Based on shallow "is-a" thinking | Based on behavioral contracts |

**The golden rule: A child class must HONOR every promise the parent class makes.**
