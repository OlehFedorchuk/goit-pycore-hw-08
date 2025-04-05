
from datetime import datetime, timedelta
from collections import UserDict
import pickle

class Field:
    """
    Base class for fields in a contact record.
    Stores a single value and provides string representation.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """
    Represents the name of a contact.
    Ensures the name is not empty.
    """
    def __init__(self, value):
        if not value:
            raise ValueError("The name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    """
    Represents a phone number for a contact.
    Ensures the phone number contains exactly 10 digits.
    """
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("The phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    """
    Represents the birthday of a contact.
    Ensures the date is in the format DD.MM.YYYY.
    """
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    """
    Represents a contact record.
    Stores a name, a list of phone numbers, and an optional birthday.
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        """
        Adds a phone number to the contact.
        """
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        """
        Removes a phone number from the contact.
        Returns True if the phone was removed, False otherwise.
        """
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        """
        Edits an existing phone number in the contact.
        Replaces old_phone with new_phone.
        Returns True if the phone was updated, False otherwise.
        """
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return "Phone updated."
        return "Phone not found."

    def add_birthday(self, birthday):
        """
        Adds a birthday to the contact.
        """
        self.birthday = Birthday(birthday)

    def __str__(self):
        """
        Returns a string representation of the contact.
        Includes name, phone numbers, and birthday (if set).
        """
        phone_str = ', '.join([p.value for p in self.phones])
        birthday_str = f", Birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_str}{birthday_str}"

class AddressBook(UserDict):
    """
    Represents an address book.
    Stores multiple contact records and provides methods to manage them.
    """
    def add_record(self, record):
        """
        Adds a contact record to the address book.
        """
        self.data[record.name.value] = record

    def find(self, name):
        """
        Finds a contact record by name.
        Returns the record if found, None otherwise.
        """
        return self.data.get(name)

    def delete(self, name):
        """
        Deletes a contact record by name.
        """
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """
        Returns a list of contacts with birthdays in the next 7 days.
        """
        upcoming_birthdays = []
        today = datetime.now()
        next_week = today + timedelta(days=7)
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                if today <= birthday <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

def input_error(func):
    """
    Decorator to handle input errors for functions.
    Catches ValueError and IndexError and returns an error message.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return f"Error: {str(e)}"
    return wrapper

def save_data(book):
    """
    Saves the address book data to a file using pickle.
    """
    with open('address_book.pkl', 'wb') as f:
        pickle.dump(book, f)
        
def load_data():
    """
    Loads the address book data from a file using pickle.
    Returns an AddressBook instance.
    """
    try:
        with open('address_book.pkl', 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()

@input_error
def add_birthday(args, book):
    """
    Adds a birthday to an existing contact.
    Args:
        args: List containing the contact name and birthday.
        book: The AddressBook instance.
    """
    name, birthday = args
    current_date = datetime.now()
    if current_date <= datetime.strptime(birthday, "%d.%m.%Y"):
        return "Birthday cannot be in the future."
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, book):
    """
    Shows the birthday of a contact.
    Args:
        args: List containing the contact name.
        book: The AddressBook instance.
    """
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}"
    elif record:
        return f"{name} does not have a birthday set."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(args, book):
    """
    Lists all upcoming birthdays in the next 7 days.
    Args:
        args: Unused.
        book: The AddressBook instance.
    """
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join([f"{record.name.value}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}" for record in upcoming])
    else:
        return "No upcoming birthdays in the next week."

@input_error
def add_contact(args, book: AddressBook):
    """
    Adds a new contact or updates an existing one.
    Args:
        args: List containing the contact name and phone number.
        book: The AddressBook instance.
    """
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

def parse_input(user_input):
    """
    Parses user input into a command and arguments.
    """
    return user_input.strip().lower().split()

def main():
    """
    Main function to run the assistant bot.
    Provides a command-line interface for managing contacts.
    """
    book = AddressBook()
    book = load_data()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            name, old_phone, new_phone = args
            record = book.find(name)
            if record:
                print(record.edit_phone(old_phone, new_phone))
            else:
                print(f"Contact {name} not found.")
        elif command == "delete":
            
            try:
                name = args[0]
                record = book.find(name)
                if record:
                    book.delete(name)
                    print(f"Contact {name} deleted.")
                else:
                    print(f"Contact {name} not found.")
            except IndexError:
                print("Please provide a name to delete.")
        elif command == "phone":
            name = args[0]
            record = book.find(name)
            if record:
                print(f"Phones: {', '.join(p.value for p in record.phones)}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            if not book.data:
                print("The contact book is empty.")
            else:
                for record in book.data.values():
                    print(record)
        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")
    save_data(book)
    print("Data saved.")

if __name__ == "__main__":
    main()
