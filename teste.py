from datetime import datetime
import random

def generate_id():
    return random.randint(0, 10000)

class Account:
    def __init__(self, wallet_amount):
        self.balance = wallet_amount
        self.score = 100

    def deposit(self, amount):
        self.balance += amount
        self.score += amount*0.1

        print(f"Added {amount} to account, new balance is R${self.balance:.2f}\n")

    def draw(self, amount):
        curr = self.balance - amount
        if (curr >= 0):
            self.balance = curr
            self.score -= amount*0.1

            print(f"Drawed {amount} from account, new balance is R${self.balance:.2f}\n")
            return True
        else:
            print(f"Couldn't draw {amount}, the account balance wasn't enough. (R${self.balance:.2f})\n")
            return False

class Person:
    def __init__(self, name:str, id:int):
        self.name = name.strip().capitalize()
        self.id = id
        self.accounts = {}
        
    def add_account(self, account_name, value = 0):
        self.accounts[account_name] = Account(value)
    
    def remove_account(self, account_name):
        self.accounts.pop(account_name)

class Transaction:
    def __init__(self, value:float, origin:Person, origin_bank:str, target:Person, target_bank:str):
        self.value = value
        self.id = generate_id()
        self.succeded = False

        self.origin_person = origin
        self.origin_bank = origin_bank
        
        self.target_person = target
        self.target_bank = target_bank
        
        self.date = ""

class Bank:
    def __init__(self, name, fee = 0):
        self.name = name
        self.clients = []
        self.clients_ammount = 0
        self.vault = 10000
        self.fee = fee

    def open_account(self, person:Person):
        self.clients.append(person)
        self.clients[person].add_account(self.name, 0)
        self.clients_ammount += 1

    def close_account(self, person:Person):
        try:
            self.clients.remove(person)
            self.clients_ammount -= 1
        except ValueError:
            self.clients_ammount += 1
    


class System:
    def __init__(self):
        self.banks = {}
        self.people = {}

    def create_bank(self, name):
        self.banks[name] = Bank(name)

    def create_person(self, name, id):
        self.people[id] = Person(name, id)

    def deposit(self, person_id:int, bank:str, value:float):
        try:
            self.people[person_id].accounts[bank].deposit(value)
            self.banks[bank].vault += value
        except ValueError:
            print("O banco ou a pessoa não existe.\n")
            

    def make_transaction(self, value:float, origin_id:int, origin_bank:str, target_id:int, target_bank:str):
        
        new_transaction = Transaction(value, self.people[origin_id], origin_bank, self.people[target_id], target_bank)
    
        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")

        try: 
            done = self.people[origin_id].accounts[origin_bank].draw(value)
            if (done):
                self.banks[origin_bank].vault -= value
                self.deposit(target_id, target_bank, value)
            else:
                pass
        except:
            print("Erro")


sys = System()

sys.create_bank("Nu")
sys.create_person("Fulano", 10)
sys.create_person("Cicrano", 15)

sys.banks["Nu"].open_account(sys.people[10])
sys.banks["Nu"].open_account(sys.people[15])

sys.deposit(10, "Nu", 100)
sys.make_transaction(50, 10, "Nu", 15, "Nu")