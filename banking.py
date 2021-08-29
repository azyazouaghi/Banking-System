import random
import sys
import sqlite3

# Printing the menu for the user
menu1 = ['0. Exit', '1. Create an account', '2. Log into account']
menu2 = ['0. Exit', '1. Balance', '2. Add income', '3. Do transfer',
         '4. Close account', '5. Log out']

# Creating the database where cards will be stored + connection

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# Creating the cards table
cur.execute("""
            CREATE TABLE IF NOT EXISTS card (
                                             id INTEGER,
                                             number TEXT,
                                             pin TEXT,
                                             balance INTEGER DEFAULT 0
                                            )
            """)

# A function that takes the user's choice and calls the right functions
global user_nb, user_pin


def start():
    global user_nb, user_pin
    while True:
        print(f'{menu1[1]}\n{menu1[2]}\n{menu1[0]}')
        i = int(input())
        print()

        while i not in [0, 1, 2]:
            i = int(input())

        if i == 0:
            print('Bye!')  # Stop code's execution
            sys.exit()
        elif i == 1:
            new_card = Card()
            print('Your card has been created')
            print(f'Your card number:\n{new_card.card_number}')
            print(f'Your card PIN:\n{new_card.pin}')
            print()
            start()
        elif i == 2:
            print('Enter your card number:')
            user_nb = input()
            print('Enter your PIN:')
            user_pin = input()
            log_in(user_nb, user_pin)


def other_menu():
    while True:
        print(f'{menu2[1]}\n{menu2[2]}\n{menu2[3]}\n{menu2[4]}\n{menu2[5]}\n{menu2[0]}')
        i = int(input())
        print()
        while i not in [0, 1, 2, 3, 4, 5]:
            i = int(input())
        if i == 0:
            print('Bye!\n')  # Stop code's execution
            sys.exit()

        elif i == 1:
            cur.execute(f"""SELECT card.balance FROM card WHERE card.number = {user_nb}""")
            print(f'Balance: {cur.fetchone()[0]}\n')

        elif i == 2:
            income = int(input('Enter income:\n'))
            cur.execute(f"""UPDATE card
                            SET balance = balance + {income}
                            WHERE card.number = {user_nb}
                        """)
            conn.commit()
            print("Income was added!\n")

        elif i == 3:
            print("\nTransfer\nEnter card number:")
            receiver_number = input()
            cur.execute(f"""SELECT card.number = {receiver_number} as Log
                            FROM card 
                            WHERE Log = 1""")

            if receiver_number == user_nb:
                print("You can't transfer money to the same account!\n")

            elif luhn_check(receiver_number) == 0:
                print("Probably you made a mistake in the card number. Please try again!\n")

            elif cur.fetchone() is None:
                print("Such a card does not exist.\n")

            else:
                to_transfer = int(input("Enter how much money you want to transfer:\n"))

                cur.execute(f"""SELECT balance FROM card WHERE card.number = {user_nb}""")
                balance_sender = cur.fetchone()[0]

                cur.execute(f"""SELECT balance FROM card WHERE card.number = {receiver_number}""")
                balance_receiver = cur.fetchone()[0]

                if to_transfer > balance_sender:
                    print("Not enough money!\n")
                else:
                    updated_balance_sender = balance_sender - to_transfer

                    cur.execute(f"""UPDATE card 
                                    SET balance = {updated_balance_sender}
                                    WHERE card.number = {user_nb}
                                """)
                    conn.commit()

                    updated_balance_receiver = balance_receiver + to_transfer

                    cur.execute(f"""UPDATE card 
                                    SET balance = {updated_balance_receiver}
                                    WHERE card.number = {receiver_number}
                                """)
                    conn.commit()
                    print("Success!\n")

        elif i == 4:
            cur.execute(f"""DELETE FROM card WHERE card.number = {user_nb}""")
            conn.commit()
            print("The account has been closed!\n")
            start()
        elif i == 5:
            print('\nYou have successfully logged out!\n')
            start()


class Card:

    def __init__(self):
        self.balance = 0
        self.card_number = None
        self.luhn_algorithm()
        self.pin = "%0.4d" % random.randrange(0, 9999)
        self.create_card()

    def create_card(self):
        CardID = "%0.4d" % random.randint(0, 9999)
        cur.execute(f"""INSERT INTO card (id, number, pin, balance)
                        VALUES({CardID},{self.card_number},{self.pin},{self.balance})
                    """)
        conn.commit()

    def luhn_algorithm(self):
        number = '400000' + str("%0.9d" % random.randint(0, 999999999))
        check = ''
        for i in range(0, len(number)):
            c = number[i]
            if (i + 1) % 2 != 0:
                c = str(int(c) * 2)
            if int(c) > 9:
                c = str(int(c) - 9)
            check = check + c
        som = sum(int(c) for c in check if c.isdigit())
        digit = (10 * round(som / 10) - som) % 10
        self.card_number = number + str(digit)


def log_in(card_nb, pin):
    cur.execute(f"""SELECT card.number = {card_nb}  AND card.pin = {pin} as Log
                    FROM card 
                    WHERE Log = 1
                 """)
    try:
        if cur.fetchone()[0] == 1:
            print('\nYou have successfully logged in!\n')
            other_menu()
        else:
            print('\nWrong card number or PIN!\n')
    except TypeError:
        print('\nWrong card number or PIN!\n')


def luhn_check(number):
    check = ''
    old_digit = number[-1]
    for i in range(0, len(number) - 1):
        c = number[i]
        if (i + 1) % 2 != 0:
            c = str(int(c) * 2)
        if int(c) > 9:
            c = str(int(c) - 9)
        check = check + c
    som = sum(int(c) for c in check if c.isdigit())
    new_digit = (10 * round(som / 10) - som) % 10
    if str(new_digit) == old_digit:
        return 1
    else:
        return 0


start()
