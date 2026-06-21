class Librarian:

    VALID_SHIFTS = {"morning", "evening", "night"}

    def __init__(self, employee_id: str, name: str, email: str, shift: str):
        
        if not employee_id or not str(employee_id).strip():
            raise ValueError("employee_id cannot be empty.")
        if not name or not str(name).strip():
            raise ValueError("Librarian name cannot be empty.")

        self.employee_id = employee_id
        self.name = name
        self.email = email
        self.shift = shift

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "email": self.email,
            "shift": self.shift,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Librarian":
        
        return cls(
            employee_id=data["employee_id"],
            name=data["name"],
            email=data["email"],
            shift=data["shift"],
        )

    def __repr__(self) -> str:
        return f"Librarian(employee_id={self.employee_id!r}, name={self.name!r}, shift={self.shift!r})"
