from datetime import date, datetime, timedelta

LOAN_PERIOD_DAYS = 14   # Books are due back 14 days after borrowing
FINE_PER_DAY = 10       # Rs. 10 per day late, charged after the loan period


class Transaction:

    def __init__(self, transaction_id: str, member_id: str, isbn: str,
                 borrow_date: str = None, due_date: str = None,
                 return_date: str = None, fine: float = 0.0):
        
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.isbn = isbn
        self.borrow_date = borrow_date or date.today().isoformat()

        if due_date:
            self.due_date = due_date
        else:
            borrow_dt = datetime.fromisoformat(self.borrow_date).date()
            self.due_date = (borrow_dt + timedelta(days=LOAN_PERIOD_DAYS)).isoformat()

        self.return_date = return_date
        self.fine = fine

    def is_returned(self) -> bool:
       
        return self.return_date is not None

    def is_overdue(self, as_of: date = None) -> bool:
        
        if self.is_returned():
            return False
        as_of = as_of or date.today()
        due = datetime.fromisoformat(self.due_date).date()
        return as_of > due

    def calculate_fine(self, return_on: date = None) -> float:
        
        return_on = return_on or date.today()
        due = datetime.fromisoformat(self.due_date).date()
        days_late = (return_on - due).days
        if days_late <= 0:
            return 0.0
        return float(days_late * FINE_PER_DAY)

    def mark_returned(self, return_on: date = None) -> float:
        
        return_on = return_on or date.today()
        self.fine = self.calculate_fine(return_on)
        self.return_date = return_on.isoformat()
        return self.fine

    def to_dict(self) -> dict:
        
        return {
            "transaction_id": self.transaction_id,
            "member_id": self.member_id,
            "isbn": self.isbn,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "fine": self.fine,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        
        return cls(
            transaction_id=data["transaction_id"],
            member_id=data["member_id"],
            isbn=data["isbn"],
            borrow_date=data.get("borrow_date"),
            due_date=data.get("due_date"),
            return_date=data.get("return_date"),
            fine=data.get("fine", 0.0),
        )

    def __repr__(self) -> str:
        status = "returned" if self.is_returned() else "out"
        return (f"Transaction(id={self.transaction_id!r}, member={self.member_id!r}, "
                f"isbn={self.isbn!r}, status={status})")
