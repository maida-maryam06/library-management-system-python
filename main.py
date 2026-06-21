from library import Library
from book import Book
from member import Member, PremiumMember
from exceptions import LibraryError

MENU_TEXT = """
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
"""


def prompt_int(prompt_text: str) -> int:
    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Please enter a valid whole number.")


def handle_add_book(library: Library) -> None:
    try:
        title = input("Title: ").strip()
        author = input("Author: ").strip()
        isbn = input("ISBN: ").strip()
        genre = input("Genre: ").strip()
        copies_total = prompt_int("Total copies: ")
        published_year = prompt_int("Published year: ")
        book = Book(title, author, isbn, genre, copies_total, copies_total, published_year)
        library.add_book(book)
        print(f"Book '{title}' added successfully with {copies_total} copies.")
    except (LibraryError, ValueError) as e:
        print(f"Error: {e}")


def handle_remove_book(library: Library) -> None:
    try:
        isbn = input("ISBN to remove: ").strip()
        library.remove_book(isbn)
        print("Book removed successfully.")
    except LibraryError as e:
        print(f"Error: {e}")


def handle_search_books(library: Library) -> None:
    query = input("Search query: ").strip()
    results = library.search_books(query)
    if not results:
        print("No matching books found.")
        return
    print(f"Found {len(results)} book(s):")
    for book in results:
        print(f"  {book.isbn:<8} {book.title:<30} by {book.author:<20} "
              f"[{book.genre}] available={book.copies_available}/{book.copies_total}")


def handle_register_member(library: Library) -> None:
    try:
        member_id = input("Member ID: ").strip()
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        membership_type = input("Membership type (basic/premium): ").strip().lower()

        if membership_type == "premium":
            member = PremiumMember(member_id, name, email, phone)
        elif membership_type == "basic":
            member = Member(member_id, name, email, phone)
        else:
            print("Invalid membership type. Must be 'basic' or 'premium'.")
            return

        library.add_member(member)
        print(f"Member '{name}' registered as {membership_type}.")
    except (LibraryError, ValueError) as e:
        print(f"Error: {e}")


def handle_borrow_book(library: Library) -> None:
    try:
        member_id = input("Member ID: ").strip()
        isbn = input("Book ISBN: ").strip()
        transaction = library.borrow_book(member_id, isbn)
        print(f"Borrowed successfully. Due date: {transaction.due_date} "
              f"(Transaction {transaction.transaction_id})")
    except LibraryError as e:
        print(f"Error: {e}")


def handle_return_book(library: Library) -> None:
    try:
        member_id = input("Member ID: ").strip()
        isbn = input("Book ISBN: ").strip()
        fine = library.return_book(member_id, isbn)
        if fine > 0:
            print(f"Returned. Overdue fine: Rs. {fine:.2f}")
        else:
            print("Returned on time. No fine.")
    except LibraryError as e:
        print(f"Error: {e}")


def handle_overdue_books(library: Library) -> None:
    overdue = library.get_overdue_books()
    if not overdue:
        print("No overdue books. Nice!")
        return
    print(f"{len(overdue)} overdue transaction(s):")
    for t in overdue:
        fine = t.calculate_fine()
        print(f"  Txn {t.transaction_id} | Member {t.member_id} | ISBN {t.isbn} | "
              f"Due {t.due_date} | Fine so far: Rs. {fine:.2f}")


def handle_list_books(library: Library) -> None:
    if not library.books:
        print("No books in the catalog yet.")
        return
    for book in library.books:
        print(f"  {book.isbn:<8} {book.title:<30} by {book.author:<20} "
              f"[{book.genre}] available={book.copies_available}/{book.copies_total}")


def handle_list_members(library: Library) -> None:
    if not library.members:
        print("No members registered yet.")
        return
    for member in library.members:
        print(f"  {member.member_id:<8} {member.name:<20} ({member.membership_type}) "
              f"borrowed={len(member.borrowed_books)}/{member.BORROW_LIMIT}")


def main():
    library = Library("City Central Library", "12 Library Road, Lahore")
    print(f"Loaded {len(library.books)} book(s) and {len(library.members)} member(s) "
          f"from {library.data_file}")

    actions = {
        "1": handle_add_book,
        "2": handle_remove_book,
        "3": handle_search_books,
        "4": handle_register_member,
        "5": handle_borrow_book,
        "6": handle_return_book,
        "7": handle_overdue_books,
        "8": lambda lib: lib.generate_report(),
        "9": handle_list_books,
        "10": handle_list_members,
    }

    while True:
        print(MENU_TEXT)
        choice = input("Choose an option (1-11): ").strip()

        if choice == "11":
            print("Goodbye!")
            break
        elif choice in actions:
            actions[choice](library)
        else:
            print("Invalid option. Please choose a number from 1 to 11.")


if __name__ == "__main__":
    main()
