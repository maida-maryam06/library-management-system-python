# Library Management System (Python OOP)

A fully **object-oriented Library Management System** built in Python,
demonstrating class design, inheritance, custom exceptions, and JSON
persistence. Tracks books, members (basic/premium), borrowing,
returning, overdue fines, and reporting through a command-line
interface. Built as the OOP task for the Enischyo Interns Python
Development internship program.

**Keywords:** python oop project, library management system, inheritance,
custom exception class, JSON persistence, CLI application, unittest,
internship project, python class design.

## Quick start

```bash
git clone https://github.com/maida-maryam06/library-management-system.git
cd library-management-system
python main.py
```

No external dependencies — pure Python standard library (`json`, `os`,
`datetime`, `unittest`).

## Features

- **Full OOP class design**, each with complete docstrings:
  - `Book` — title, author, ISBN, genre, copy counts, published year
  - `Member` — basic membership (max 2 borrowed books at once)
  - `PremiumMember(Member)` — inherits from Member, raises the borrow
    limit to 5 and **overrides** `validate_borrow()` accordingly
  - `Librarian` — staff member with employee ID and shift
  - `Transaction` — one borrow/return record with due date and fine
  - `Library` — the central orchestrator owning all books, members, and transactions
- **Custom exception hierarchy** rooted at `LibraryError`, used for
  every error case (book/member not found, no copies available, borrow
  limit exceeded, duplicate ISBN/member ID, returning a book never borrowed).
- **Core `Library` methods:**
  - `add_book()` / `remove_book()` — catalog management, with removal
    blocked while copies are out on loan
  - `search_books(query)` — matches title **OR** author **OR** genre, case-insensitively
  - `borrow_book(member_id, isbn)` — validates availability and borrow
    limit, decrements `copies_available`, appends to the member's
    `borrowed_books`, creates a `Transaction`
  - `return_book(member_id, isbn)` — closes the transaction, charges
    **Rs. 10/day** fine for every day past the 14-day loan period
  - `get_overdue_books()` — all transactions still out and past due
  - `generate_report()` — formatted summary (catalog size, membership
    breakdown, overdue list with running fines)
- **JSON persistence**: on startup, `Library` loads `library_data.json`
  (if present) and **reconstructs live objects** — including correctly
  rebuilding `PremiumMember` instances (not generic `Member`) so the
  5-book limit survives a restart.
- **Interactive CLI menu** with `try/except LibraryError` handling
  around every operation.
- **10 unit tests** (`unittest`) covering every major method, the
  inheritance/override behavior, the custom exceptions, and the
  JSON round-trip.

## Project structure

```
library-management-system/
├── book.py             # Book class
├── member.py           # Member base class + PremiumMember subclass
├── librarian.py        # Librarian class
├── transaction.py      # Transaction class (borrow/return/fine logic)
├── exceptions.py        # LibraryError and subclasses
├── library.py           # Library orchestrator (all core methods + JSON persistence)
├── main.py              # CLI menu application
├── test_library.py       # unittest suite (10 tests)
└── README.md
```

`library_data.json` is created automatically the first time you run
`main.py` and add a book or member — it is not committed empty, since
the app generates it on first use.

## Borrowing rules

| Membership | Max books borrowed at once |
|------------|------------------------------|
| Basic      | 2                            |
| Premium    | 5                             |

- Loan period: **14 days** from the borrow date.
- Late fine: **Rs. 10 per day** for every day past the due date (no
  fine for on-time or early returns).

## Running the app

```bash
python3 main.py
```

```
========================================
   LIBRARY MANAGEMENT SYSTEM
========================================
1. Add a book
2. Remove a book
3. Search books (title/author/genre)
4. Register a member
5. Borrow a book
6. Return a book
7. View overdue books
8. Generate library report
9. List all books
10. List all members
11. Exit
========================================
```

Every action saves immediately to `library_data.json`, so you can quit
and resume later without losing data.

## Running the tests

```bash
python -m unittest test_library.py -v
```

The test suite uses a separate `test_library_data.json` file (created
and deleted automatically in `setUp`/`tearDown`), so running the tests
never touches your real `library_data.json`.

### Actual test output

The following is the real output from running the test suite in this
repo (10 tests, all passing):

```
test_01_add_book (test_library.TestLibraryManagementSystem.test_01_add_book) ... ok
test_02_remove_book (test_library.TestLibraryManagementSystem.test_02_remove_book) ... ok
test_03_search_books (test_library.TestLibraryManagementSystem.test_03_search_books) ... ok
test_04_borrow_book_success (test_library.TestLibraryManagementSystem.test_04_borrow_book_success) ... ok
test_05_borrow_book_no_copies_available (test_library.TestLibraryManagementSystem.test_05_borrow_book_no_copies_available) ... ok
test_06_borrow_limit_basic_vs_premium (test_library.TestLibraryManagementSystem.test_06_borrow_limit_basic_vs_premium) ... ok
test_07_return_book_on_time_and_overdue_fine (test_library.TestLibraryManagementSystem.test_07_return_book_on_time_and_overdue_fine) ... ok
test_08_get_overdue_books (test_library.TestLibraryManagementSystem.test_08_get_overdue_books) ... ok
test_09_persistence_save_and_load (test_library.TestLibraryManagementSystem.test_09_persistence_save_and_load) ... ok
test_10_generate_report_and_librarian (test_library.TestLibraryManagementSystem.test_10_generate_report_and_librarian) ... ==================================================

LIBRARY REPORT: Test Library
==================================================
Address: 1 Test St
--------------------------------------------------
Total titles in catalog: 3
Total copies owned:      4
Copies available now:    4
--------------------------------------------------
Total members:           2
  Basic members:         1
  Premium members:       1
--------------------------------------------------
Total transactions:      0
Currently borrowed:      0
Currently overdue:       0
==================================================
ok

----------------------------------------------------------------------
Ran 10 tests in 0.106s

OK
```

## Design notes

- **Why a separate `Transaction` class?** `borrow_book()` is required
  to "create a Transaction record," so transactions are modeled as
  first-class objects with their own borrow/due/return dates and fine
  calculation, rather than as loose fields bolted onto `Member` or `Book`.
- **Why does `PremiumMember` override `validate_borrow()` instead of just
  changing `BORROW_LIMIT`?** Both are actually done together:
  `BORROW_LIMIT` is a class attribute that `PremiumMember` overrides to
  `5`, and `validate_borrow()` is overridden too so the **error message**
  correctly says "Premium member" vs the basic message — `Library.borrow_book()`
  calls `member.validate_borrow()` polymorphically without needing to
  know which subclass it's dealing with.
- **Why block `remove_book()` while copies are on loan?** Removing a
  book that members currently have borrowed would leave their
  `borrowed_books` lists and open `Transaction` records pointing at a
  title that no longer exists in the catalog — an inconsistent state
  the system actively prevents.
- **Why is `Librarian` not a subclass of `Member`?** A librarian doesn't
  borrow books and has a different attribute set (`employee_id`,
  `shift`) — modeling them as siblings rather than parent/child avoids
  inheriting irrelevant fields and methods.


## License

MIT — free to use, copy, and modify.
