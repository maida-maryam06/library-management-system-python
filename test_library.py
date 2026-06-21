import os
import unittest
from datetime import date, timedelta

from library import Library
from book import Book
from member import Member, PremiumMember
from librarian import Librarian
from transaction import Transaction
from exceptions import (
    LibraryError,
    BookNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    BorrowLimitExceededError,
    DuplicateISBNError,
    DuplicateMemberError,
    BookNotBorrowedError,
)


class TestLibraryManagementSystem(unittest.TestCase):

    TEST_FILE = "test_library_data.json"

    def setUp(self):
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)
        self.library = Library("Test Library", "1 Test St", data_file=self.TEST_FILE)

        self.library.add_book(Book("Dune", "Frank Herbert", "111", "Sci-Fi", 2, 2, 1965))
        self.library.add_book(Book("1984", "George Orwell", "222", "Fiction", 1, 1, 1949))
        self.library.add_book(Book("Foundation", "Isaac Asimov", "333", "Sci-Fi", 1, 1, 1951))

        self.library.add_member(Member("M1", "Ali Khan", "ali@example.com", "0300-0000000"))
        self.library.add_member(PremiumMember("M2", "Sara Ahmed", "sara@example.com", "0301-1111111"))

    def tearDown(self):
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)

    # ------------------------------------------------------------------
    def test_01_add_book(self):
        self.assertEqual(len(self.library.books), 3)
        with self.assertRaises(DuplicateISBNError):
            self.library.add_book(Book("Dune 2", "Someone", "111", "Sci-Fi", 1, 1, 2000))

    def test_02_remove_book(self):
        self.library.remove_book("333")
        self.assertEqual(len(self.library.books), 2)

        with self.assertRaises(BookNotFoundError):
            self.library.remove_book("does-not-exist")

        # Borrow a copy, then removal should be blocked
        self.library.borrow_book("M1", "111")
        with self.assertRaises(LibraryError):
            self.library.remove_book("111")

    def test_03_search_books(self):
        by_title = self.library.search_books("dune")
        self.assertEqual(len(by_title), 1)
        self.assertEqual(by_title[0].isbn, "111")

        by_author = self.library.search_books("orwell")
        self.assertEqual(len(by_author), 1)
        self.assertEqual(by_author[0].isbn, "222")

        by_genre = self.library.search_books("sci-fi")
        self.assertEqual(len(by_genre), 2)

        no_match = self.library.search_books("nonexistent")
        self.assertEqual(no_match, [])

    def test_04_borrow_book_success(self):
        transaction = self.library.borrow_book("M1", "111")

        book = self.library._find_book("111")
        member = self.library._find_member("M1")

        self.assertEqual(book.copies_available, 1)
        self.assertIn("111", member.borrowed_books)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.member_id, "M1")
        self.assertEqual(transaction.isbn, "111")
        self.assertFalse(transaction.is_returned())
        self.assertIn(transaction, self.library.transactions)

    def test_05_borrow_book_no_copies_available(self):
        self.library.borrow_book("M1", "222")  # last copy of '1984' taken
        with self.assertRaises(NoCopiesAvailableError):
            self.library.borrow_book("M2", "222")

    def test_06_borrow_limit_basic_vs_premium(self):
        self.library.add_book(Book("Extra1", "X", "444", "Fic", 1, 1, 2000))
        self.library.add_book(Book("Extra2", "X", "555", "Fic", 1, 1, 2000))

        # Basic member M1 borrows up to the limit of 2
        self.library.borrow_book("M1", "111")
        self.library.borrow_book("M1", "222")
        with self.assertRaises(BorrowLimitExceededError):
            self.library.borrow_book("M1", "333")

        # Premium member M2 can borrow more than 2
        self.library.borrow_book("M2", "333")
        self.library.borrow_book("M2", "444")
        self.library.borrow_book("M2", "555")
        self.assertEqual(len(self.library._find_member("M2").borrowed_books), 3)

    def test_07_return_book_on_time_and_overdue_fine(self):
        transaction = self.library.borrow_book("M1", "111")

        # On-time return: no fine.
        fine = self.library.return_book("M1", "111")
        self.assertEqual(fine, 0.0)
        self.assertEqual(self.library._find_book("111").copies_available, 2)
        self.assertNotIn("111", self.library._find_member("M1").borrowed_books)

        # Overdue return: simulate by backdating the due date 5 days into the past
        transaction2 = self.library.borrow_book("M1", "222")
        transaction2.due_date = (date.today() - timedelta(days=5)).isoformat()
        fine2 = self.library.return_book("M1", "222")
        self.assertEqual(fine2, 50.0)  # 5 days late * Rs. 10/day

        # Returning a book that was never borrowed should raise
        with self.assertRaises(BookNotBorrowedError):
            self.library.return_book("M1", "333")

    def test_08_get_overdue_books(self):
        t1 = self.library.borrow_book("M1", "111")
        t2 = self.library.borrow_book("M2", "222")

        # Make t1 overdue, leave t2 on time
        t1.due_date = (date.today() - timedelta(days=2)).isoformat()

        overdue = self.library.get_overdue_books()
        overdue_ids = {t.transaction_id for t in overdue}

        self.assertIn(t1.transaction_id, overdue_ids)
        self.assertNotIn(t2.transaction_id, overdue_ids)

    def test_09_persistence_save_and_load(self):
        self.library.borrow_book("M2", "111")  # M2 is a PremiumMember

        reloaded = Library("Different Name", "Different Address", data_file=self.TEST_FILE)

        self.assertEqual(len(reloaded.books), 3)
        self.assertEqual(len(reloaded.members), 2)
        self.assertEqual(len(reloaded.transactions), 1)

        reloaded_m2 = reloaded._find_member("M2")
        self.assertIsInstance(reloaded_m2, PremiumMember)
        self.assertEqual(reloaded_m2.BORROW_LIMIT, 5)
        self.assertIn("111", reloaded_m2.borrowed_books)

        reloaded_book = reloaded._find_book("111")
        self.assertEqual(reloaded_book.copies_available, 1)

    def test_10_generate_report_and_librarian(self):
        report_text = self.library.generate_report()
        self.assertIn("Test Library", report_text)
        self.assertIn("Total titles in catalog: 3", report_text)

        librarian = Librarian("E1", "Bilal Tariq", "bilal@example.com", "morning")
        data = librarian.to_dict()
        rebuilt = Librarian.from_dict(data)
        self.assertEqual(rebuilt.employee_id, "E1")
        self.assertEqual(rebuilt.shift, "morning")

        with self.assertRaises(ValueError):
            Librarian("", "No ID", "x@example.com", "morning")


if __name__ == "__main__":
    unittest.main()
