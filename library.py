import json
import os
from datetime import date

from book import Book
from member import Member, PremiumMember
from transaction import Transaction
from exceptions import (
    LibraryError,
    BookNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    DuplicateISBNError,
    DuplicateMemberError,
    BookNotBorrowedError,
)

DATA_FILE = "library_data.json"


class Library:

    def __init__(self, name: str, address: str, data_file: str = DATA_FILE):
        
        self.name = name
        self.address = address
        self.books = []
        self.members = []
        self.transactions = []
        self.data_file = data_file
        self._next_transaction_number = 1
        self.load_data()

    
    def load_data(self) -> None:
        
        if not os.path.exists(self.data_file):
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        self.name = raw.get("name", self.name)
        self.address = raw.get("address", self.address)
        self.books = [Book.from_dict(b) for b in raw.get("books", [])]
        self.members = [Member.from_dict(m) for m in raw.get("members", [])]
        self.transactions = [Transaction.from_dict(t) for t in raw.get("transactions", [])]

        
        max_seen = 0
        for t in self.transactions:
            try:
                num = int(t.transaction_id.replace("T", ""))
                max_seen = max(max_seen, num)
            except (ValueError, AttributeError):
                continue
        self._next_transaction_number = max_seen + 1

    def save_data(self) -> None:
        
        payload = {
            "name": self.name,
            "address": self.address,
            "books": [b.to_dict() for b in self.books],
            "members": [m.to_dict() for m in self.members],
            "transactions": [t.to_dict() for t in self.transactions],
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    # Internal helpers
    def _find_book(self, isbn: str) -> Book:
        
        for book in self.books:
            if book.isbn == isbn:
                return book
        raise BookNotFoundError(f"No book found with ISBN '{isbn}'.")

    def _find_member(self, member_id: str) -> Member:
        
        for member in self.members:
            if member.member_id == member_id:
                return member
        raise MemberNotFoundError(f"No member found with ID '{member_id}'.")

    def _new_transaction_id(self) -> str:
        
        tid = f"T{self._next_transaction_number:04d}"
        self._next_transaction_number += 1
        return tid

    # book management
    def add_book(self, book: Book) -> None:
       
        for existing in self.books:
            if existing.isbn == book.isbn:
                raise DuplicateISBNError(f"A book with ISBN '{book.isbn}' already exists.")
        self.books.append(book)
        self.save_data()

    def remove_book(self, isbn: str) -> None:
        
        book = self._find_book(isbn)
        if book.copies_available < book.copies_total:
            raise LibraryError(
                f"Cannot remove '{book.title}': copies are currently borrowed."
            )
        self.books.remove(book)
        self.save_data()

    def search_books(self, query: str) -> list:
       
        return [book for book in self.books if book.matches(query)]

    
    # Member management
    def add_member(self, member: Member) -> None:
        
        for existing in self.members:
            if existing.member_id == member.member_id:
                raise DuplicateMemberError(
                    f"A member with ID '{member.member_id}' already exists."
                )
        self.members.append(member)
        self.save_data()

    # Borrowing and returning
    def borrow_book(self, member_id: str, isbn: str) -> Transaction:
        
        member = self._find_member(member_id)
        book = self._find_book(isbn)

        if not book.is_available():
            raise NoCopiesAvailableError(
                f"No copies of '{book.title}' are currently available."
            )

        # Polymorphic call: Member vs PremiumMember enforce different limits
        member.validate_borrow()

        book.copies_available -= 1
        member.borrowed_books.append(isbn)

        transaction = Transaction(
            transaction_id=self._new_transaction_id(),
            member_id=member_id,
            isbn=isbn,
        )
        self.transactions.append(transaction)
        self.save_data()
        return transaction

    def return_book(self, member_id: str, isbn: str) -> float:
        
        member = self._find_member(member_id)
        book = self._find_book(isbn)

        if isbn not in member.borrowed_books:
            raise BookNotBorrowedError(
                f"Member '{member.name}' does not currently have '{book.title}' borrowed."
            )

        open_transaction = None
        for t in self.transactions:
            if t.member_id == member_id and t.isbn == isbn and not t.is_returned():
                open_transaction = t
                break

        if open_transaction is None:
            raise BookNotBorrowedError(
                f"No active loan transaction found for member '{member_id}' and ISBN '{isbn}'."
            )

        fine = open_transaction.mark_returned()
        book.copies_available += 1
        member.borrowed_books.remove(isbn)
        self.save_data()
        return fine

    # Reporting
    def get_overdue_books(self) -> list:
        
        return [t for t in self.transactions if t.is_overdue()]

    def generate_report(self) -> str:
        
        total_titles = len(self.books)
        total_copies = sum(b.copies_total for b in self.books)
        available_copies = sum(b.copies_available for b in self.books)

        basic_count = sum(1 for m in self.members if m.membership_type == "basic")
        premium_count = sum(1 for m in self.members if m.membership_type == "premium")

        currently_borrowed = [t for t in self.transactions if not t.is_returned()]
        overdue = self.get_overdue_books()

        lines = []
        lines.append("=" * 50)
        lines.append(f"LIBRARY REPORT: {self.name}")
        lines.append("=" * 50)
        lines.append(f"Address: {self.address}")
        lines.append("-" * 50)
        lines.append(f"Total titles in catalog: {total_titles}")
        lines.append(f"Total copies owned:      {total_copies}")
        lines.append(f"Copies available now:    {available_copies}")
        lines.append("-" * 50)
        lines.append(f"Total members:           {len(self.members)}")
        lines.append(f"  Basic members:         {basic_count}")
        lines.append(f"  Premium members:       {premium_count}")
        lines.append("-" * 50)
        lines.append(f"Total transactions:      {len(self.transactions)}")
        lines.append(f"Currently borrowed:      {len(currently_borrowed)}")
        lines.append(f"Currently overdue:       {len(overdue)}")
        if overdue:
            lines.append("-" * 50)
            lines.append("Overdue details:")
            for t in overdue:
                projected_fine = t.calculate_fine()
                lines.append(
                    f"  Txn {t.transaction_id} | Member {t.member_id} | "
                    f"ISBN {t.isbn} | Due {t.due_date} | Fine so far: Rs. {projected_fine:.2f}"
                )
        lines.append("=" * 50)

        report = "\n".join(lines)
        print(report)
        return report
