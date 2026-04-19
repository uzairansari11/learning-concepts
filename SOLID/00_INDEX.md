# SOLID Principles — Complete Guide

> 5 rules that make your code clean, scalable, and easy to change.

## What is SOLID?

SOLID is an acronym for 5 design principles introduced by Robert C. Martin (Uncle Bob).
They are the foundation of good Object-Oriented Programming (OOP).

| Letter | Principle                     | One-Line Summary                                      |
|--------|-------------------------------|-------------------------------------------------------|
| S      | Single Responsibility         | One class = One job                                   |
| O      | Open/Closed                   | Open to extend, Closed to modify                      |
| L      | Liskov Substitution           | Child class must work wherever parent class is used   |
| I      | Interface Segregation         | Don't force a class to implement what it doesn't need |
| D      | Dependency Inversion          | Depend on abstractions, not concrete classes          |

## Files in this folder

- `01_S_Single_Responsibility.md`
- `02_O_Open_Closed.md`
- `03_L_Liskov_Substitution.md`
- `04_I_Interface_Segregation.md`
- `05_D_Dependency_Inversion.md`

## Why should you care?

Without SOLID:
- Adding a feature breaks 5 other things
- Code is hard to test
- You are afraid to touch old code
- Every bug fix creates 2 new bugs

With SOLID:
- You can add features safely
- Code is easy to test in isolation
- You understand any part of the codebase quickly
- Changes are predictable

---
Start with `01_S_Single_Responsibility.md`
