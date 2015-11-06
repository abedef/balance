#!/Library/FrameWorks/Python.framework/Versions/3.5/bin/python3

import datetime
import os
import re


# Path to the file where transactions are saved
file_path = os.path.expanduser("~/") + ".transactions"


class InvalidInputError(Exception):
    pass


class ShortInputError(Exception):
    pass


class UnrecognizedInputError(Exception):
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

        >>> x = Transaction(129.85, ['birthday', 'food'])
        >>> str(x)
        '129.85 on 2015-11-30 #birthday #food'
        """
        if self.is_negative:
            string = '-'
        else:
            string = ''

        string += str(self.dollars)
        string += '.'
        string += str(self.cents).zfill(2)

        string += ' on '
        string += str(self.date)
        # string += self.date.strftime('%a %b %m, %Y')

        for tag in self.tags:
            string += ' #' + tag

        return string


class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.undo_stack = []    # TODO Implement undo functionality

    def save_transactions(self):
        """ (TransactionManager) -> NoneType

        Save Transaction objects to the file specified by file_path, each
        separated by newline characters.
        """
        with open(file_path, 'w') as f:
            for transaction in self.transactions:
                f.write(str(transaction))
                f.write('\n')

    def load_transactions(self):
        """ (TransactionManager) -> NoneType

        Load Transaction objects stored in the file specified by file_path.
        Create the file if it doesn't exist.
        """
        self.transactions = []

        if not os.path.isfile(file_path):
            with open(file_path, 'w') as f:
                pass
        else:
            with open(file_path, 'r') as f:
                lines = f.read().split('\n')

            # Each line has format '1234.56 on YYYY-MM-DD #tag' (0+ tags)
            for line in lines:
                # Ignore blank lines
                if line == '':
                    continue

                words = line.split(' ')

                amt = float(words.pop(0))       # Pop '1234.56'
                words.pop(0)                    # Pop 'on'

                tmp = words.pop(0).split('-')   # Pop 'YYYY-MM-DD'
                date = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))

                tags = []
                for word in words:              # Left with tags (if any)
                    tags.append(word[1:])       # Leave out preceeding '#'

                self.transactions.append(Transaction(amt, tags, date))

    def list_transactions(self, tag=None):
        """ (TransactionManager, str) -> str

        Return the string representation of all Transaction objects,
        each preceeded by an identification number and separated by
        newline characters. If a tag is provided, return only those
        objects with the given tag.
        """
        string = ''
        id_width = len(str(len(self.transactions) - 1))
        amt_width = 4   # Four characters in shortest amount ('0.00')

        # Adjust amt_width to be the size of the largest transaction amount
        for t in self.transactions:
            curr_width = len(str(t.dollars)) + (4 if t.is_negative else 3)
            if curr_width > amt_width:
                amt_width = curr_width

        t_id = 0        # Keep track of current Transaction ID
        for t in self.transactions:
            if tag is not None and tag not in t.tags:
                continue
            curr_width = len(str(t.dollars)) + (4 if t.is_negative else 3)
            string += ' #' + str(t_id).zfill(id_width)      # ID padded with 0s
            string += ' ' * (4 + amt_width - curr_width)    # Justification
            string += str(t) + '\n'
            t_id += 1

        # Trim newline character at end of string if it exists
        if string != '':
            string = string[:-1]

        return string

    def add_transaction(self, command):
        """ (TransactionManager, str) -> NoneType

        Parse command and add the result to the list of transactions.
        Raise InvalidInputError if given date is invalid.
        Raise ShortInputError if not enough information is provided.
        Raise UnrecognizedInputError if command cannot be parsed.
        """
        amt_regex = '^(spent|made)\s([0-9]+\.[0-9]+|[0-9]+)'
        date_regex = '\son\s[0-9]{4}-[0-1][0-9]-[0-3][0-9]'
        tags_regex = '\s#[A-Za-z]+'
        amounts = re.findall(amt_regex, command)
        dates = re.findall(date_regex, command)
        raw_tags = re.findall(tags_regex, command)

        if len(amounts) == 0:
            raise ShortInputError()
        elif len(amounts) > 1:
            raise UnrecognizedInputError(amounts[1])
        elif len(dates) > 1:
            raise UnrecognizedInputError(dates[1])
        else:
            amt = float(amounts[0][1])
            if amounts[0][0] == 'spent':
                amt *= -1

            tags = []
            for tag in raw_tags:
                tags.append(tag.strip()[1:].lower())    # Leave out leading '#'

            if len(dates) == 0:
                self.transactions.append(Transaction(amt, tags))
            else:
                tmp = dates[0].strip().split()[1]
                year = int(tmp.split('-')[0])
                month = int(tmp.split('-')[1])
                day = int(tmp.split('-')[2])
                date = datetime.date(year, month, day)
                self.transactions.append(Transaction(amt, tags, date))

    def remove_transaction(self, index):
        """ (TransactionManager, int) -> Transaction

        Remove and return the Transaction object at the given index.
        Raise IndexError if index is out of range.
        """
        if index in range(len(self.transactions)):
            return self.transactions.pop(index)
        else:
            raise IndexError()

    def total_transactions(self):   # TODO Test corner cases
        """ (TransactionManager) -> float

        Return the sum of all Transaction object amounts.
        """
        sum_dollars = 0
        sum_cents = 0
        for t in self.transactions:
            if t.is_negative:
                sum_dollars -= t.dollars
                sum_cents -= t.cents
            else:
                sum_dollars += t.dollars
                sum_cents += t.cents
        t.dollars += t.cents // 100
        t.cents = t.cents % 100

        return sum_dollars + sum_cents / 100

    def edit_transaction(self):
        pass    # TODO Implement me


def usage():
    print(' exit:          quit balance.py\n' +
          ' load:          load transactions saved to disk\n' +
          ' save:          save transactions to disk\n' +
          ' list/ls:       list transactions\n' +
          ' remove/rm n:   remove transaction at index n\n'
          ' total:         calculate overall balance\n' +
          'In order to record a credit/debit of 1234.56:\n' +
          ' spent/made 1234.56\n' +
          ' spent/made 1234.56 #tag #othertag\n' +
          ' spent/made 1234.56 on YYYY-MM-DD\n' +
          ' spent/made 1234.56 on YYYY-MM-DD #tag #othertag\n' +
          'In order to search for a tag:\n'
          ' #tag\n', end='')


def run():
    tm = TransactionManager()
    tm.load_transactions()

    # TODO Rewrite regular expressions to be more precise
    add_rx = ('^(spent|made)((\s\d+)|(\s\d+\.\d\d))' +
              '(\son\s\d{4}-\d\d-\d\d)?(\s#[a-zA-Z]+)*$')
    remove_rx = '(^(remove|rm)\s)(\d+)$'
    search_rx = '(?<=^#)[a-zA-Z]+$'

    while True:
        command = input('balance > ').strip()

        if command == 'exit':
            break
        elif command == 'load':
            tm.load_transactions()
        elif command == 'save':
            tm.save_transactions()
        elif command == 'list' or command == 'ls':
            print(tm.list_transactions())
        elif command == 'help':
            usage()
        elif command == 'total':
            print(' total: ' + str(tm.total_transactions()))
        elif re.search(add_rx, command) is not None:
            tm.add_transaction(command)
        elif re.search(remove_rx, command) is not None:
            tm.remove_transaction(int(re.search(remove_rx, command).group(3)))
        elif re.search(search_rx, command) is not None:
            print(tm.list_transactions(re.search(search_rx, command).group(0)))
        else:
            print(' Unrecognized input! Type help for usage details.')


if __name__ == '__main__':
    run()
