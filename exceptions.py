class LibraryError(Exception):
    pass


class BookNotFoundError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass


class NoCopiesAvailableError(LibraryError):
    pass


class BorrowLimitExceededError(LibraryError):
    pass


class DuplicateISBNError(LibraryError):
    pass


class DuplicateMemberError(LibraryError):
    pass


class BookNotBorrowedError(LibraryError):
    pass
