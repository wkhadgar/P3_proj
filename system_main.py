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
        self.score += amount * 0.1

        print(f"Depositado R$ {amount:.2f} na conta, o novo total é de R${self.balance:.2f}")

    def draw(self, amount):
        curr = self.balance - amount
        if curr >= 0:
            self.balance = curr
            self.score -= amount * 0.1

            print(f"Sacado R$ {amount:.2f} da conta, o novo total é de R${self.balance:.2f}")
            return True
        else:
            print(
                f"Não foi possível sacar R$ {amount:.2f}, o valor em conta não é suficiente. (R${self.balance:.2f})")
            return False


class Person:
    def __init__(self, name: str, cpf: int):
        self.name = name.strip().capitalize()
        self.cpf = cpf
        self.accounts = {}

    def add_account(self, account_bank: str, *, value=0):
        self.accounts[account_bank] = Account(value)

    def remove_account(self, account_name):
        self.accounts.pop(account_name)


class Transaction:
    def __init__(self, value: float, origin: Person, origin_bank: str, target: Person, target_bank: str):
        self.value = value
        self.cpf = generate_id()
        self.succeded = False

        self.origin_person = origin
        self.origin_bank = origin_bank

        self.target_person = target
        self.target_bank = target_bank

        self.date = ""


class Bank:
    def __init__(self, name, *, fee=0):
        self.name = name
        self.clients = {}
        self.clients_ammount = 0
        self.vault = 10000
        self.fee = fee

    def open_account(self, client: Person):
        self.clients[client.cpf] = client
        self.clients[client.cpf].add_account(self.name)
        self.clients_ammount += 1

    def close_account(self, person: Person):
        try:
            self.clients.remove(person)
            self.clients_ammount -= 1
        except ValueError:
            self.clients_ammount += 1


class System:
    def __init__(self):
        self.banks = {}
        self.people = {}

    def create_bank(self, *, name):
        self.banks[name] = Bank(name)

    def create_person(self, *, name, cpf: int):
        self.people[cpf] = Person(name, cpf)

    def sys_deposit(self, *, cpf: int, bank: str, value: float):
        print("________________________________________________________")
        try:
            print(f"{self.people[cpf].name} Realizou uma operação de depósito em {bank}")
            self.people[cpf].accounts[bank].deposit(value)
            self.banks[bank].vault += value
        except ValueError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")

    def sys_draw(self, *, cpf: int, bank: str, value: float):
        drawed = 0
        print("________________________________________________________")
        try:
            print(f"{self.people[cpf].name} Realizou uma operação de saque em {bank}")
            done = self.people[cpf].accounts[bank].draw(value)
            if done:
                self.banks[bank].vault -= value
                drawed = value
            else:
                pass
        except ValueError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")
        return drawed

    def make_transaction(self, *, value: float, origin_id: int, origin_bank: str, target_id: int, target_bank: str):

        new_transaction = Transaction(value, self.people[origin_id], origin_bank, self.people[target_id], target_bank)

        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")

        try:
            print(
                f"O sistema realizou uma transferência: {self.people[origin_id].name} em {origin_bank} para {self.people[target_id].name} em {target_bank}\n")
            done = self.sys_draw(cpf=origin_id, bank=origin_bank, value=value)
            if done != 0:
                self.banks[origin_bank].vault -= value
                self.sys_deposit(cpf=target_id, bank=target_bank, value=value)
            else:
                pass
        except ValueError:
            print("Erro")


sys = System()

main_bank = input("Digite o nome do banco a ser criado: ").strip()
sys.create_bank(name=main_bank)

giver_name = input("Digite o nome da pessoa que vai realizar a transferencia: ")
giver_cpf = int(input("Digite o CPF dessa pessoa: "))

receiver_name = input("Digite o nome da pessoa que vai receber a transferencia: ")
receiver_cpf = int(input("Digite o CPF dessa pessoa: "))

sys.create_person(name=giver_name, cpf=giver_cpf)
sys.create_person(name=receiver_name, cpf=receiver_cpf)

sys.banks[main_bank].open_account(sys.people[giver_cpf])
sys.banks[main_bank].open_account(sys.people[receiver_cpf])

sys.sys_deposit(cpf=giver_cpf, bank=main_bank,
                value=float(input(f"Qual valor que será depositado inicialmente na conta do {giver_name}?\n-> R$ ")))
sys.make_transaction(value=float(input(f"Qual valor que será transferido para o {receiver_name}?\n-> R$ ")),
                     origin_id=giver_cpf, origin_bank=main_bank, target_id=receiver_cpf, target_bank=main_bank)