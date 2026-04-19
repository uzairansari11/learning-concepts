# S — Single Responsibility Principle (SRP)

## The Rule

> A class should have ONE and only ONE reason to change.

In simple words:
**One class = One job. Do not mix responsibilities.**

---

## Real Life Analogy

Think of a restaurant.

- The **Chef** cooks food. That's his only job.
- The **Waiter** serves food. That's his only job.
- The **Cashier** handles billing. That's his only job.

Now imagine if the Chef also had to take orders, wash dishes, AND do billing.
- If the billing system changes, the Chef's work is affected.
- If the menu changes, the billing logic is mixed in there too.
- Total chaos.

**SRP says: Give each person (class) ONE clear responsibility.**

---

## Bad Code Example (Violates SRP)

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def calculate_pay(self):
        # Calculates salary
        return self.salary * 12

    def save_to_database(self):
        # Saves employee to DB
        print(f"Saving {self.name} to database...")

    def generate_report(self):
        # Generates HR report
        print(f"Report for {self.name}: Salary = {self.salary}")
```

### Why is this BAD?

This `Employee` class has 3 different jobs:
1. **Business Logic** — calculating pay
2. **Database Logic** — saving to DB
3. **Reporting Logic** — generating reports

If the HR team changes the report format → you touch `Employee` class.
If the DB team switches from SQL to MongoDB → you touch `Employee` class.
If the finance team changes pay calculation → you touch `Employee` class.

**3 different teams, 3 different reasons to change = 3 responsibilities = BAD.**

Every time one team makes a change, they risk breaking the other team's logic.

---

## Good Code Example (Follows SRP)

```python
# Responsibility 1: Only knows about Employee data
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary


# Responsibility 2: Only handles pay calculation
class PayCalculator:
    def calculate(self, employee: Employee):
        return employee.salary * 12


# Responsibility 3: Only handles database operations
class EmployeeRepository:
    def save(self, employee: Employee):
        print(f"Saving {employee.name} to database...")


# Responsibility 4: Only handles report generation
class EmployeeReportGenerator:
    def generate(self, employee: Employee):
        print(f"Report for {employee.name}: Salary = {employee.salary}")


# Usage
emp = Employee("Ali", 50000)

PayCalculator().calculate(emp)          # Finance team owns this
EmployeeRepository().save(emp)          # DB team owns this
EmployeeReportGenerator().generate(emp) # HR team owns this
```

### Why is this GOOD?

- Each class has exactly ONE reason to change.
- Finance team changes pay logic → only `PayCalculator` changes.
- DB team changes storage → only `EmployeeRepository` changes.
- HR team changes report format → only `EmployeeReportGenerator` changes.
- **Nothing else breaks.**

---

## Another Real Life Example — A Swiss Army Knife vs Specialist Tools

A Swiss Army Knife can do many things (cut, open bottles, file nails).
But would you perform surgery with it? No. You want a specialized scalpel.

In code:
- Swiss Army Knife class = does everything = hard to maintain
- Specialist classes = each does one thing = easy to maintain, test, and change

---

## SRP in Web Development (Node.js / Express Example)

### BAD — One function doing everything

```javascript
// This function validates input, saves to DB, AND sends email
async function registerUser(req, res) {
    const { email, password } = req.body;

    // Validation logic
    if (!email.includes('@')) {
        return res.status(400).json({ error: 'Invalid email' });
    }

    // Database logic
    const user = await db.query(
        'INSERT INTO users (email, password) VALUES (?, ?)',
        [email, password]
    );

    // Email logic
    await nodemailer.sendMail({
        to: email,
        subject: 'Welcome!',
        text: 'Thanks for registering.'
    });

    res.json({ success: true });
}
```

### GOOD — Each concern is separated

```javascript
// validator.js — Only validates
function validateUser(email, password) {
    if (!email.includes('@')) throw new Error('Invalid email');
    if (password.length < 6) throw new Error('Password too short');
}

// userRepository.js — Only handles DB
async function saveUser(email, password) {
    return await db.query(
        'INSERT INTO users (email, password) VALUES (?, ?)',
        [email, password]
    );
}

// emailService.js — Only handles email
async function sendWelcomeEmail(email) {
    await nodemailer.sendMail({
        to: email,
        subject: 'Welcome!',
        text: 'Thanks for registering.'
    });
}

// controller.js — Only orchestrates
async function registerUser(req, res) {
    const { email, password } = req.body;
    validateUser(email, password);
    await saveUser(email, password);
    await sendWelcomeEmail(email);
    res.json({ success: true });
}
```

Now:
- Email provider changes (SendGrid → Mailgun)? Only touch `emailService.js`
- Switch from MySQL to PostgreSQL? Only touch `userRepository.js`
- Add new validation rule? Only touch `validator.js`

---

## How to Spot SRP Violations

Ask yourself these questions about a class:

1. Can I describe what this class does WITHOUT using the word "and"?
   - "This class calculates pay" ✅
   - "This class calculates pay AND saves to DB AND sends emails" ❌

2. How many different teams would need to change this class?
   - 1 team → probably fine ✅
   - 3 teams → definitely violates SRP ❌

3. Does this class have methods that don't use any of its own properties?
   - A `generate_report()` method that doesn't use any Employee data → belongs elsewhere ❌

---

## Summary

| | Before SRP | After SRP |
|---|---|---|
| Number of classes | Few, fat classes | Many, focused classes |
| Change impact | One change = many files risky | One change = one file |
| Testing | Hard to unit test | Easy to test each class alone |
| Teamwork | Teams step on each other | Each team owns their class |

**The golden rule: If a class has multiple reasons to change, split it.**
