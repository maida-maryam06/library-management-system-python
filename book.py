class Book:

    def __init__(self, title: str, author: str, isbn: str, genre: str,
                 copies_total: int, copies_available: int, published_year: int):
        
        if not title or not str(title).strip():
            raise ValueError("Book title cannot be empty.")
        if not author or not str(author).strip():
            raise ValueError("Book author cannot be empty.")
        if not isbn or not str(isbn).strip():
            raise ValueError("Book ISBN cannot be empty.")
        if copies_total < 0 or copies_available < 0:
            raise ValueError("Copy counts cannot be negative.")
        if copies_available > copies_total:
            raise ValueError("copies_available cannot exceed copies_total.")

        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.copies_total = copies_total
        self.copies_available = copies_available
        self.published_year = published_year

    def is_available(self) -> bool:
        return self.copies_available > 0

    def matches(self, query: str) -> bool:
        
        query_lower = query.lower().strip()
        return (
            query_lower in self.title.lower()
            or query_lower in self.author.lower()
            or query_lower in self.genre.lower()
        )

    def to_dict(self) -> dict:
        
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            "copies_total": self.copies_total,
            "copies_available": self.copies_available,
            "published_year": self.published_year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        
        return cls(
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            genre=data["genre"],
            copies_total=data["copies_total"],
            copies_available=data["copies_available"],
            published_year=data["published_year"],
        )

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, isbn={self.isbn!r}, available={self.copies_available}/{self.copies_total})"
