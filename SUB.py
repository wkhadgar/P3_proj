import random
from datetime import datetime
from interface import *


def popup_rc_bank_exists():
    rcb = RetryCancelPopup("O banco já existe no sistema. Tente novamente.")
    rcb.show()


def popup_success_info(details: str = ""):
    rcb = InfoPopup("Operação realizada com sucesso! \nContinue um bom servidor!", details)
    rcb.show()


def popup_error(details: str = ""):
    err = ErrorPopup("Um erro ocorreu do lado do sistema. Não pedimos perdão.\nSeus créditos socias "
                     "foram deduzidos em 100 pontos. \n(Use o sistema de forma a não ocorrerem falhas)", details)
    err.show()


def popup_warning(details: str = ""):
    wrn = WarningPopup("Um erro ocorreu, mas não foi do meu lado. Verifique os dados inseridos.\nPor sua "
                       "incopetencia seus créditos socias foram deduzidos em 700 pontos. (Erros de servidores são "
                       "punidos com pena máxima. Não os cometa novamente.)", details)
    wrn.show()


class Account:
    def __init__(self, wallet_amount: float):
        """
        Descreve uma conta.
        A conta também contém um score agregado internamente.

        :param wallet_amount: Valor que a conta guarda no momento.
        """

        self.balance = wallet_amount
        self.score = 100  # Pontuação da conta.
        self.max_day_draw = 100_000
        self.max_night_draw = self.max_day_draw / 2

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

    def draw(self, amount: int, *, has_time_limit=False):
        """
        Tenta sacar da conta o valor dado.

        :param amount: Valor a ser sacado.
        :param has_time_limit: Opcional, se verdadeiro limita o saque por horário.
        :return: True se o valor pode ser retirado, False se não.
        """

        curr = self.balance - amount
        if curr >= 0:

            now = datetime.now().time()
            limit_start_time = datetime.strptime("21:00", "%H:%M").time()
            limit_end_time = datetime.strptime("4:00", "%H:%M").time()

            if has_time_limit:
                if ((now < limit_end_time) or (now > limit_start_time)) and (amount > self.max_night_draw):
                    print(f"Não foi possível sacar R${amount:.2f}, sua conta está com limite de saque por horário.")
                    return False

                if amount > self.max_day_draw:
                    print(
                            f"Não foi possível sacar R${amount:.2f}, o limite de saque (R${self.max_day_draw:.2f}) é "
                            f"inferior ao valor desejado.")
                    return False

            self.balance = curr
            self.score -= amount * 0.15

            print(f"Sacado R$ {amount:.2f} da conta, o novo total é de R${self.balance:.2f}")
            return True
        else:
            print(
                    f"Não foi possível sacar R$ {amount:.2f}, o valor em conta não é suficiente. (R$"
                    f"{self.balance:.2f})")
            return False


class Person:
    def __init__(self, name: str, cpf: int, age: int = 18):
        """
        Descreve uma pessoa.

        :param name: Nome da pessoa.
        :param cpf: Identificador único dessa pessoa.
        """

        self.name = name.strip().capitalize()
        self.cpf = cpf
        self.age = age
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
    def __init__(self, value: float):
        self.value = value

        self._id = 0
        self.date = ""
        self.succeded = False


class Transfer(Transaction):
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

        super().__init__(value)

        self.origin_person = origin_id
        self.origin_bank = origin_bank

        self.target_person = target_id
        self.target_bank = target_bank


class Deposit(Transaction):
    def __init__(self, value: float, target_id: int, target_bank: str):
        if value < 0:
            value = 0
        super().__init__(value)

        self.tgt_id = target_id
        self.tgt_bnk = target_bank


class Draw(Transaction):
    def __init__(self, value: float, origin_id: int, origin_bank: str):
        if value > 0:
            value = 0
        super().__init__(value)
        self.origin_id = origin_id
        self.origin_bnk = origin_bank


class Bank:
    def __init__(self, name: str, *, fee: float = 0):
        """
        Descreve um banco.

        Os bancos contêm um cofre relacionado ao patrimônio do banco, somado ao capital de seus clientes.
        Além de opcionalmente conter uma taxa de transações.

        :param name: Nome do banco.
        :param fee: Taxa, opcional, que pode ser usada sobre as operações.
        """

        self.name = name.strip()
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
        except KeyError:
            self.clients_ammount += 1


class System(Interface):
    def __init__(self, root: tk.Tk):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """
        super().__init__(root)
        self.transactions = {}
        self.banks = {}
        self.people = {}
        self.current_form: InputForm = None

    def show_status(self):
        bank_amount = len(self.banks)
        people_amount = len(self.people)
        print(
                f"\nO sistema tem {people_amount} "
                f"{'pessoa cadastrada' if people_amount == 1 else 'pessoas cadastradas'} e "
                f"{bank_amount} {'banco cadrastado' if bank_amount == 1 else 'bancos cadrastados'}.\n")

        print("Pessoas:")
        for p in list(self.people.values()):
            try:
                print(f"\t {p.name} - CPF: {p.cpf};")
            except:
                continue

        print("\nBancos:")
        for b in list(self.banks.values()):
            try:
                print(f"\t {b.name}.")
            except:
                continue
        print()

    def __create_bank(self):
        name = self.current_form.fields["Nome:"]
        bank_fee = self.current_form.fields["Taxa de transferência externa: (%)"]

        self.banks[name] = Bank(name, fee=bank_fee)
        popup_success_info(f"Banco {name} criado com sucesso.")

    def create_bank(self):
        """
        Cadastra um banco no sistema.

        :param name: Nome do banco.
        """
        bnk = AddBankForm(tk.Tk(), self.__create_bank)
        bnk.show_form()
        self.current_form = bnk

    def remove_bank(self, *, name: str):
        try:
            if self.banks[name].clients_ammount == 0:
                self.banks.pop(name)
                popup_success_info(f"O banco '{name}' foi removido do sistema com sucesso!")
            else:
                popup_error(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")
        except KeyError:
            popup_warning("Banco não encontrado no sistema!")

    def __create_person(self):
        name = self.current_form.fields["Nome:"]
        cpf = int(self.current_form.fields["CPF:"])

        self.people[cpf] = Person(name, cpf)
        popup_success_info(f"A pessoa {name} cadastrada com sucesso.")

    def create_person(self):
        """
        Cadastra uma pessoa no sistema.

        :param name: Nome da pessoa.
        :param cpf: Identificador único da pessoa.
        """
        prs = AddPersonForm(tk.Tk(), self.__create_person)
        prs.show_form()
        self.current_form = prs

    def remove_person(self, cpf: int):
        try:
            accounts = list(self.people[cpf].accounts.keys())
            for acc in accounts:
                self.banks[acc].close_account(self.people[cpf])
            name = self.people[cpf].name
            self.people.pop(cpf)
            print(f"A pessoa '{name}' foi removida do sistema com sucesso!")
        except KeyError:
            print(f"A pessoa com o identificador {cpf} não foi encontrada no sistema.")

    def get_person_data(self, cpf: int):
        try:
            print(f"\nDados da pessoa '{self.people[cpf].name}':")
            for acc in list(self.people[cpf].accounts.keys()):
                print(
                        f"\tValor no banco {acc} R${self.people[cpf].accounts[acc].balance:.2f}; Score relacionado: "
                        f"{self.people[cpf].accounts[acc].score:}")
            print("\n")
        except KeyError:
            print("A pessoa não foi encontrada no sistema!")

    def __sys_open_account(self):
        owner_id = int(self.current_form.fields["CPF:"])
        bank = self.current_form.fields["Banco:"]

        self.banks[bank].open_account(self.people[owner_id])
        popup_success_info(f"A conta de {self.people[owner_id].name} foi criada em {bank} com sucesso!")

    def sys_open_account(self):
        """
        Cria uma conta para a pessoa indicada, no banco dado.
        """
        acc = OpenAccountForm(tk.Tk(), self.__sys_open_account)
        acc.show_form()
        self.current_form = acc

    def make_deposit(self, *, cpf: int, bank: str, value: float):
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
            print(f"{self.people[cpf].name} realizou uma operação de depósito em {bank}")
            total = self.people[cpf].accounts[bank].deposit(value)
            self.banks[bank].vault += value
        except KeyError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")

        return total

    def make_draw(self, *, cpf: int, bank: str, value: float, has_time_limit=False):
        """
        Tenta sacar o valor dado da conta da pessoa indicada, em seu respectivo banco.

        :param cpf: Identificador único da pessoa.
        :param bank: Banco responsável pela conta da pessoa.
        :param value: Valor do saque.
        :param has_time_limit: Opcional, se verdadeiro o saque usará os limites da conta.
        :return: Valor retirado, 0 se não foi possível sacar.
        """

        drawed = 0
        print("________________________________________________________")
        try:
            print(f"{self.people[cpf].name} realizou uma operação de saque em {bank}")
            done = self.people[cpf].accounts[bank].draw(value, has_time_limit=has_time_limit)
            if done:
                self.banks[bank].vault -= value
                drawed = value
            else:
                pass
        except KeyError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")
        return drawed

    def generate_transaction_id(self, transaction: Transfer):
        new_id = random.randint(0, 999_999_999)

        while new_id in list(self.transactions.keys()):
            new_id = random.randint(0, 999_999_999)

        self.transactions[new_id] = transaction
        return new_id

    def __make_transfer(self, is_time_limited: bool = False):
        """
        Realiza uma transferência no valor dado, entre duas pessoas, em seus respectivos bancos.

        :param value: Valor da transferência.
        :param origin_id: Idenficador único da pessoa a transferir o dinheiro.
        :param origin_bank: Nome do banco responsável pela conta da pessoa a transferir.
        :param target_id: Idenficador único da pessoa a receberr o dinheiro.
        :param target_bank: Nome do banco responsável pela conta da pessoa a receber.
        :param is_time_limited: Opcional, se verdadeiro a transferencia usará os limites da conta.
        :return: A transação realizada.
        """

        value = int(self.current_form.fields["🡓 Valor: R$"])
        origin_id = int(self.current_form.fields["🡐 CPF:"])
        origin_bank = self.current_form.fields["🡐 Banco:"]
        target_id = int(self.current_form.fields["🡒 CPF:"])
        target_bank = self.current_form.fields["🡒 Banco:"]

        new_transaction = Transfer(value, origin_id, origin_bank, target_id, target_bank)

        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")
        new_transaction._id = self.generate_transaction_id(new_transaction)

        try:
            taxed_value = value + self.banks[origin_bank].fee * value if origin_bank != target_bank else value
            done = self.make_draw(cpf=origin_id, bank=origin_bank, value=taxed_value, has_time_limit=is_time_limited)
            if done != 0:
                new_transaction.succeded = True
                self.banks[origin_bank].vault += taxed_value - value
                self.make_deposit(cpf=target_id, bank=target_bank, value=value)

                popup_success_info(
                        f"\n\nO sistema automatizou a transferência: {self.people[origin_id].name} em {origin_bank} "
                        f"para "
                        f"{self.people[target_id].name} em {target_bank}\n")
            else:
                popup_warning("Não há dinheiro suficiente na conta de origem.")
        except KeyError:
            popup_warning()

        return new_transaction

    def make_transfer(self, *, is_time_limited: bool = False):
        trf = TransferForm(tk.Tk(), self.__make_transfer)
        trf.show_form()
        self.current_form = trf