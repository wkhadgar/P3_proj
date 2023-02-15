from datetime import datetime
import random


def generate_id():
    return random.randint(0, 10000)


class Account:
    def __init__(self, wallet_amount: float):
        """
        Descreve uma conta.
        A conta também contém um score agregado internamente.

        :param wallet_amount: Valor que a conta guarda no momento.
        """

        self.balance = wallet_amount
        self.score = 100  # Pontuação da conta.

    def deposit(self, amount):
        """
        Deposita nessa conta o valor dado.

        :param amount: Valor a ser depositado.
        :return: Valor total da conta.
        """

        self.balance += amount
        self.score += amount * 0.1

        print(f"Depositado R$ {amount:.2f} na conta, o novo total é de R${self.balance:.2f}")
        return self.balance

    def draw(self, amount):
        """
        Tenta sacar da conta o valor dado.

        :param amount: Valor a ser sacado.
        :return: True se o valor pode ser retirado, False se não.
        """

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
        """
        Descreve uma pessoa.

        :param name: Nome da pessoa.
        :param cpf: Identificador único dessa pessoa.
        """

        self.name = name.strip().capitalize()
        self.cpf = cpf
        self.accounts = {}

    def add_account(self, account_bank: str, *, value=0):
        """
        Cria uma conta para essa pessoa.

        :param account_bank: Banco responsável por essa conta.
        :param value: Valor inicial de abertura da conta, opcional.
        """

        self.accounts[account_bank] = Account(value)

    def remove_account(self, account_bank):
        """
        Exclui a conta dessa pessoa no banco dado.

        :param account_bank: Nome do banco onde essa pessoa contém conta.
        """

        self.accounts.pop(account_bank)


class Transaction:
    def __init__(self, value: float, origin_id: int, origin_bank: str, target_id: int, target_bank: str):
        """
        Descreve uma transação.
        Cada transação contém um identificador aleatório e uma data atualizável que pode ser associada a sua realização.

        :param value: Valor da transação.
        :param origin_id: Identificador da pessoa de origem da transação.
        :param origin_bank: Nome do banco onde a pessoa de origem deseja usar sua conta.
        :param target_id: Identificador da pessoa de destino da transação.
        :param target_bank: Nome do banco onde a pessoa de destino usará sua conta.
        """

        self.value = value
        self._id = generate_id()
        self.succeded = False

        self.origin_person = origin_id
        self.origin_bank = origin_bank

        self.target_person = target_id
        self.target_bank = target_bank

        self.date = ""


class Bank:
    def __init__(self, name, *, fee=0):
        """
        Descreve um banco.

        Os bancos contêm um cofre relacionado ao patrimônio do banco, somado ao capital de seus clientes.
        Além de opcionalmente conter uma taxa de transações.

        :param name: Nome do banco.
        :param fee: Taxa, opcional, que pode ser usada sobre as operações.
        """

        self.name = name
        self.clients = {}
        self.clients_ammount = 0
        self.vault = 10000
        self.fee = fee

    def open_account(self, client: Person):
        """
        Abre uma conta no banco
        :param client:
        :return:
        """

        self.clients[client.cpf] = client
        self.clients[client.cpf].add_account(self.name)
        self.clients_ammount += 1

    def close_account(self, client: Person):
        try:
            self.clients[client.cpf].accounts.pop(self.name)
            self.clients.pop(client.cpf)
            self.clients_ammount -= 1
        except ValueError:
            self.clients_ammount += 1


class System:
    def __init__(self):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """

        self.banks = {}
        self.people = {}

    def create_bank(self, *, name: str):
        """
        Cadastra um banco no sistema.

        :param name: Nome do banco.
        """

        self.banks[name] = Bank(name)

    def remove_bank(self, *, name: str):
        if self.banks[name].clients_ammount == 0:
            self.banks.pop(name)
        else:
            print(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")

    def create_person(self, *, name, cpf: int):
        """
        Cadastra uma pessoa no sistema.

        :param name: Nome da pessoa.
        :param cpf: Identificador único da pessoa.
        """

        self.people[cpf] = Person(name, cpf)

    def remove_person(self, cpf: int):
        try:
            for acc in self.people[cpf].accounts.keys():
                self.banks[acc].close_account(self.people[cpf])
            self.people.pop(cpf)
        except ValueError:
            print(f"A pessoa com o identificador {cpf} não foi encontrada no sistema.")

    def sys_open_account(self, owner_id: int, bank: str):
        """
        Cria uma conta para a pessoa indicada, no banco dado.

        :param owner_id: Identficador único do dono da conta.
        :param bank: Banco responsável pela conta criada.
        """

        self.banks[bank].open_account(self.people[owner_id])

    def sys_deposit(self, *, cpf: int, bank: str, value: float):
        """
        Deposita o valor dado na conta da pessoa indicado, em seu respectivo banco.

        :param cpf: Identificador único da pessoa.
        :param bank: Banco responsável pela conta da pessoa.
        :param value: Valor do depósito.
        :return: Valor total da conta dessa pessoa após o depósito.
        """

        total = 0
        print("________________________________________________________")
        try:
            print(f"{self.people[cpf].name} Realizou uma operação de depósito em {bank}")
            total = self.people[cpf].accounts[bank].deposit(value)
            self.banks[bank].vault += value
        except ValueError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")

        return total

    def sys_draw(self, *, cpf: int, bank: str, value: float):
        """
        Tenta sacar o valor dado da conta da pessoa indicada, em seu respectivo banco.

        :param cpf: Identificador único da pessoa.
        :param bank: Banco responsável pela conta da pessoa.
        :param value: Valor do saque.
        :return: Valor retirado, 0 se não foi possível sacar.
        """

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

    def make_transfer(self, *, value: float, origin_id: int, origin_bank: str, target_id: int, target_bank: str):
        """
        Realiza uma transferência no valor dado, entre duas pessoas, em seus respectivos bancos.

        :param value: Valor da transferência.
        :param origin_id: Idenficador único da pessoa a transferir o dinheiro.
        :param origin_bank: Nome do banco responsável pela conta da pessoa a transferir.
        :param target_id: Idenficador único da pessoa a receberr o dinheiro.
        :param target_bank: Nome do banco responsável pela conta da pessoa a receber.
        :return: A transação realizada.
        """

        new_transaction = Transaction(value, origin_id, origin_bank, target_id, target_bank)

        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")

        try:
            print(
                f"O sistema realizou uma transferência: {self.people[origin_id].name} em {origin_bank} para {self.people[target_id].name} em {target_bank}\n")
            done = self.sys_draw(cpf=origin_id, bank=origin_bank, value=value)
            if done != 0:
                new_transaction.succeded = True
                self.banks[origin_bank].vault -= value
                self.sys_deposit(cpf=target_id, bank=target_bank, value=value)
            else:
                pass
        except ValueError:
            print("Erro!!")

        return new_transaction


sys = System()

main_bank = input("Digite o nome do banco a ser criado: ").strip()
sys.create_bank(name=main_bank)

giver_name = input("Digite o nome da pessoa que vai realizar a transferencia: ")
giver_cpf = int(input("Digite o CPF dessa pessoa: "))

receiver_name = input("Digite o nome da pessoa que vai receber a transferencia: ")
receiver_cpf = int(input("Digite o CPF dessa pessoa: "))

sys.create_person(name=giver_name, cpf=giver_cpf)
sys.create_person(name=receiver_name, cpf=receiver_cpf)

sys.sys_open_account(giver_cpf, main_bank)
sys.sys_open_account(receiver_cpf, main_bank)

sys.sys_deposit(cpf=giver_cpf, bank=main_bank,
                value=float(input(f"Qual valor que será depositado inicialmente na conta do {giver_name}?\n-> R$ ")))
sys.make_transfer(value=float(input(f"Qual valor que será transferido para o {receiver_name}?\n-> R$ ")),
                  origin_id=giver_cpf, origin_bank=main_bank, target_id=receiver_cpf, target_bank=main_bank)