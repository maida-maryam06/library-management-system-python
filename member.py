from datetime import date

from exceptions import BorrowLimitExceededError


class Member:

    BORROW_LIMIT = 2  # Basic members may borrow at most 2 books at once

    def __init__(self, member_id: str, name: str, email: str, phone: str,
                 join_date: str = None, borrowed_books: list = None):
        
        if not member_id or not str(member_id).strip():
            raise ValueError("member_id cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Member name cannot be empty.")
        if not email or not str(email).strip():
            raise ValueError("Member email cannot be empty.")

        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.membership_type = "basic"
        self.join_date = join_date or date.today().isoformat()
        self.borrowed_books = list(borrowed_books) if borrowed_books else []

    def can_borrow(self) -> bool:
        
        return len(self.borrowed_books) < self.BORROW_LIMIT

    def validate_borrow(self) -> None:
        
        if not self.can_borrow():
            raise BorrowLimitExceededError(
                f"Member '{self.name}' has reached the basic borrow limit "
                f"of {self.BORROW_LIMIT} books."
            )

    def to_dict(self) -> dict:

        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "membership_type": self.membership_type,
            "join_date": self.join_date,
            "borrowed_books": list(self.borrowed_books),
        }

    @classmethod

    def from_dict(cls, data: dict) -> "Member":
        
        if data.get("membership_type") == "premium":
            return PremiumMember(
                member_id=data["member_id"],
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                join_date=data.get("join_date"),
                borrowed_books=data.get("borrowed_books", []),
            )
        return cls(
            member_id=data["member_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            join_date=data.get("join_date"),
            borrowed_books=data.get("borrowed_books", []),
        )

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(member_id={self.member_id!r}, "
                f"name={self.name!r}, borrowed={len(self.borrowed_books)})")


class PremiumMember(Member):

    BORROW_LIMIT = 5  # Premium members may borrow up to 5 books at once

    def __init__(self, member_id: str, name: str, email: str, phone: str,
                 join_date: str = None, borrowed_books: list = None):
        
        super().__init__(member_id, name, email, phone, join_date, borrowed_books)
        self.membership_type = "premium"

    def validate_borrow(self) -> None:
        
        if not self.can_borrow():
            raise BorrowLimitExceededError(
                f"Premium member '{self.name}' has reached the borrow limit "
                f"of {self.BORROW_LIMIT} books."
            )
