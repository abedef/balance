#!/Library/FrameWorks/Python.framework/Versions/3.5/bin/python3

import datetime
import os
import re


# Path to the file where transactions are saved
file_path = os.path.expanduser("~/") + ".transactions"


class EmptyInput(Exception):
    pass


class ShortInput(Exception):
    pass


class UnrecognizedInput(Exception):
    def __init__(self, value):
        self.value = value


class Transaction:
    def __init__(self, amt, tags, date=datetime.date.today()):
        """ (Transaction, float, list of str, datetime.date) -> NoneType

        Create a new Transaction object to store a monetary amount along with
        some related tags. Date is set to today's date by default.
        """
        self.is_negative = amt < 0
        self.dollars = int(abs(amt))
        self.cents = round((abs(amt) % 1) * 100)
        if self.cents == 100:
            self.dollars += 1
            self.cents = 0

        self.tags = tags
        self.date = date

    def __str__(self):
        """ (Transaction) -> str

        Return a string representation of this Transaction object.

        >>> x = Transaction(129.85, ["birthday", "food"])
        >>> str(x)
        '129.85 on 2015-11-30 #birthday #food'
        """
        if self.is_negative:
            string = "-"
        else:
            string = ""

        string += str(self.dollars)
        string += "."
        string += str(self.cents).zfill(2)

        string += " on "
        string += str(self.date)
        # string += self.date.strftime("%a %b %m, %Y")

        for tag in self.tags:
            string += " #" + tag

        return string

    def amt_width(self):
        """ (Transaction) -> int

        Return the width of the string representation of this Transaction
        object's amount attribute.

        >>> x = Transaction(129.85, ["birthday", "food"])
        >>> y = Transaction(0.00, [])
        >>> x.amt_width()
        6
        >>> y.amt_width()
        4
        """
        width = 0

        if self.is_negative:
            width += 1  # To account for the '-'

        width += len(str(self.dollars))
        width += 1      # To account for the '.'
        width += 2      # To account for the two decimal digits

        return width


class TransactionManager():
    def __init__(self):
        self.transactions = []
        self.undo_stack = []

    def save_file_exists(self):
        """ (TransactionManager) -> bool

        Return True if a transaction file exists on disk.
        Return False otherwise.
        """
        return os.path.isfile(file_path)

    def create_save_file(self):
        """ (TransactionManager) -> NoneType

        Create transaction file on disk. Do nothing if file already exists.
        """
        if not os.path.isfile(file_path):
            with open(file_path, "w") as f:
                pass

    def remove_save_file(self):
        """ (TransactionManager) -> NoneType

        Remove transaction file stored to disk.
        Do nothing if it does not exist.
        """
        if save_file_exists():
            os.remove(file_path)

    def save_transactions(self):
        """ (TransactionManager) -> NoneType

        Save the string representation of each stored Transaction to disk.
        """
        with open(file_path, "w") as f:
            for transaction in self.transactions:
                f.write(str(transaction))
                f.write("\n")

    def load_transactions(self):
        """ (TransactionManager) -> NoneType

        Update the list of Transaction objects to reflect those stored on disk.
        Create save file if it does not exist.
        """
        if self.save_file_exists():
            with open(file_path, "r") as f:
                lines = f.read().split("\n")

            for line in lines:
                if line == "":
                    continue

                words = line.split(" ")

                amt = float(words.pop(0))
                words.pop(0)

                date = datetime.date(int(words[0][:4]),
                                     int(words[0][5:7]),
                                     int(words[0][8:10]))
                words.pop(0)

                tags = []
                for word in words:
                    if word[1:] not in tags and word[1:] != "":
                        tags.append(word[1:])

                self.transactions.append(Transaction(amt, tags, date))
        else:
            self.create_save_file()

    def list_transactions(self):
        """ (TransactionManager) -> str

        Return the string representation of each stored Transaction object
        preceeded by an identification number.

        >>> tm.list_transactions()
        T00    100.00 on 2015-10-03 #bill #hydro
        ...
        T72     10.00 on 2015-11-30 #food
        """
        string = ""
        id_width = len(str(len(self.transactions) - 1))
        amt_width = 4   # Four characters in shortest amount (0.00)

        for transaction in self.transactions:
            if transaction.amt_width() > amt_width:
                amt_width = transaction.amt_width()

        for i in range(len(self.transactions)):
            string += "T" + str(i).zfill(id_width)
            string += " " * (4 + amt_width - self.transactions[i].amt_width())
            string += str(self.transactions[i]) + "\n"

        if string != "":
            string = string[:-1]

        return string

    def add_transaction(self, command):
        """ (TransactionManager, str) -> NoneType

        Parse command and add the contained transaction to the the
        list of transactions.
        """
        amounts = re.findall('[0-9]+\.[0-9][0-9]', command)
        dates = re.findall('on [0-9]{4}-[0-1][0-9]-[0-3][0-9]', command)
        raw_tags = re.findall(' #[A-Za-z]+', command)

        amt = 0
        tags = []

        if len(amounts) != 1 or len(dates) != 1:
            return

        amt = amounts[0]
        for tag in raw_tags:
            tags.append(tag[2:])

        transaction = Transaction(float(amt), tags)
        self.transactions.append(transaction)

    def remove_transaction(self, index):
        """ (TransactionManager, int) -> Transaction

        Remove and return the Transaction object at the given index.
        Raise IndexError if index is out of range.
        """
        return self.transactions.pop(index)

    def transactions_sum(self):
        """ (TransactionManager) -> (int, int)

        Return a Transaction object representing the sum of all stored
        Transaction object amounts.
        """
        sum_dollars = 0
        sum_cents = 0

        for t in self.transactions:
            sum_dollars += t.dollars * (-1 if t.is_negative else 1)
            sum_cents += t.cents * (-1 if t.is_negative else 1)

        sum_dollars += sum_cents // 100
        sum_cents += sum_cents % 100

        return Transaction(float(str(sum_dollars) + "." + str(sum_cents)),
                           ["total"])


def run():
    tm = TransactionManager()
    tm.load_transactions()

    while True:
        command = input("balance > ")

        if command == "exit":
            break
        elif command == "load":
            tm.load_transactions()
        elif command == "save":
            tm.save_transactions()
        elif command == "list" or command == "ls":
            print(tm.list_transactions())
        else:
            if re.findall('^-?[0-9]+\.[0-9][0-9]' +
                          ' on [0-9]{4}-[0-1][0-9]-[0-3][0-9]' +
                          '( #[a-zA-Z]+)*$', command) != []:
                tm.add_transaction(command)
            elif re.findall('(remove)|(rm) [0-9]+', command) != []:
                tm.remove_transaction(int(command.split()[1]))
            else:
                continue


if __name__ == "__main__":
    run()
