class missing_date_argument(IndexError):
    def __str__(self):
        return "The argument with the database file is missing "

class invalid_date_argument(ValueError):
    """The file with dates is missing"""

class event_alredy_exists(ValueError):
    """The event you try to insert is alredy in ted DB"""
