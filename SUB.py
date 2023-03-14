import random
import pickle
import sys
import tkinter.filedialog
from datetime import datetime
from interface import *


def popup_retry_cancel(details: str = ""):
    rcb = RetryCancelPopup(details)
    rcb.show()
    return rcb.boolean


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
        self.is_limited = False

    def deposit(self, amount):
        """
        Deposita nessa conta o valor dado.

        :param amount: Valor a ser depositado.
        :return: Valor total da conta.
        """

        self.balance += amount
        self.score += amount * 0.1

        popup_success_info(f"Depositado R$ {amount:.2f} na conta, o novo total é de R${self.balance:.2f}")
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

            popup_success_info(f"Sacado R$ {amount:.2f} da conta, o novo total é de R${self.balance:.2f}")
            return True
        else:
            popup_error(
                    f"Não foi possível sacar R$ {amount:.2f}, o valor em conta não é suficiente. (R$"
                    f"{self.balance:.2f})")
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


class SysData:
    def __init__(self):
        self.transactions = {}
        self.banks = {}
        self.people = {}


class System(Interface):
    def __init__(self, root: tk.Tk):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """
        super().__init__(root)

        self.data = SysData()
        self.current_form: InputForm = None
        self.has_save = False
        self.save_name = ""

    def __save_sys(self):
        if not self.has_save:
            now = datetime.now().strftime("%d-%m-%Y_%H-%M")
            self.save_name = "SAVE_" + now + ".syss"
            self.has_save = True

        with open("saves/" + self.save_name, 'wb') as save:
            pickle.dump(self.data, save)

    def __load_sys(self, path: str):
        if path[-5:] == ".syss":
            with open(path, 'rb') as save:
                self.data = pickle.load(save)
            popup_success_info("Sistema recuperado.")

        else:
            if popup_retry_cancel("Selecione um arquivo válido."):
                self.screen_load_data()

    def __generate_transaction_id(self, transaction: Transfer):
        new_id = random.randint(0, 999_999_999)

        while new_id in list(self.data.transactions.keys()):
            new_id = random.randint(0, 999_999_999)

        self.data.transactions[new_id] = transaction
        return new_id

    def __create_bank(self):
        name = self.current_form.fields["Nome:"]
        bank_fee = self.current_form.fields["Taxa: (%)"]
        if name == "":
            if popup_retry_cancel("Nome inválido."):
                self.screen_create_bank()
        else:
            try:
                bank_fee = float(bank_fee) / 100
                self.data.banks[name] = Bank(name, fee=bank_fee)
                self.__save_sys()
                popup_success_info(f"Banco {name} criado com sucesso.")
            except ValueError:
                popup_warning("Taxa incorreta.")

    def __remove_bank(self):
        name = self.current_form.fields["Banco:"]
        try:
            if self.data.banks[name].clients_ammount == 0:
                self.data.banks.pop(name)
                self.__save_sys()
                popup_success_info(f"O banco '{name}' foi removido do sistema com sucesso!")
            else:
                popup_error(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")
        except KeyError:
            popup_warning("Banco não encontrado no sistema!")

    def __create_person(self):
        name = self.current_form.fields["Nome:"]
        cpf = int(self.current_form.fields["CPF:"])

        self.data.people[cpf] = Person(name, cpf)
        self.__save_sys()
        popup_success_info(f"A pessoa {name} cadastrada com sucesso.")

    def __remove_person(self):
        cpf = self.current_form.fields["CPF:"]
        name = self.current_form.fields["Pessoa:"]
        try:
            cpf = int(cpf)
        except ValueError:
            popup_warning("CPF inválido.")
            return

        try:
            if self.data.people[cpf].name == name:
                accounts = list(self.data.people[cpf].accounts.keys())
                for acc in accounts:
                    self.data.banks[acc].close_account(self.data.people[cpf])
                name = self.data.people[cpf].name
                self.data.people.pop(cpf)
                self.__save_sys()
                popup_success_info(f"A pessoa '{name}' foi removida do sistema com sucesso!")
            else:
                popup_warning("O CPF informado não corresponde a pessoa que deseja remover.")
        except KeyError:
            popup_warning(f"A pessoa com o identificador {cpf} não foi encontrada no sistema.")

    def __sys_open_account(self):
        try:
            owner_id = int(self.current_form.fields["CPF:"])
            bank = self.current_form.fields["Banco:"]

            if owner_id in list(self.data.people.keys()):
                self.data.banks[bank].open_account(self.data.people[owner_id])
                self.__save_sys()
                popup_success_info(f"A conta de {self.data.people[owner_id].name} foi criada em {bank} com sucesso!")
            else:
                popup_warning("O CPF informado não foi encontrado no sistema.")
        except ValueError:
            if popup_retry_cancel("Digite um CPF válido."):
                self.screen_open_account()

    def __make_deposit(self):
        try:
            cpf = int(self.current_form.fields["CPF:"])
        except ValueError:
            popup_warning("CPF inválido.")
            return
        bank = self.current_form.fields["Banco:"]
        try:
            value = float(self.current_form.fields["Valor: R$"])
        except ValueError:
            popup_warning("Valor inválido.")
            return

        try:
            self.data.people[cpf].accounts[bank].deposit(value)
            self.data.banks[bank].vault += value
            self.__save_sys()
            popup_success_info(f"{self.data.people[cpf].name} realizou uma operação de depósito em {bank}")
        except KeyError:
            popup_warning("O banco ou a pessoa não existe.\n")

    def __make_transfer(self):
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

        origin_bank = self.current_form.fields["🡐 Banco:"]
        target_bank = self.current_form.fields["🡒 Banco:"]

        try:
            value = float(self.current_form.fields["🡓 Valor: R$"])
        except ValueError:
            popup_warning("Valor inválido")
            return

        try:
            origin_id = int(self.current_form.fields["🡐 CPF:"])
        except ValueError:
            popup_warning("CPF de origem inválido.")
            return
        try:
            target_id = int(self.current_form.fields["🡒 CPF:"])
        except ValueError:
            popup_warning("CPF de destino inválido.")
            return

        try:
            if not (origin_bank in list(self.data.people[origin_id].accounts.keys())):
                popup_warning(f"{self.data.people[origin_id].name} não possui conta em {origin_bank}.")
                return
            elif not (target_bank in list(self.data.people[target_id].accounts.keys())):
                popup_warning(f"{self.data.people[target_id].name} não possui conta em {target_bank}.")
                return
            else:
                is_time_limited = self.data.people[origin_id].accounts[origin_bank].is_limited
        except KeyError:
            popup_warning("CPF não encontrado no sistema.")
            return

        new_transaction = Transfer(value, origin_id, origin_bank, target_id, target_bank)

        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")
        new_transaction._id = self.__generate_transaction_id(new_transaction)

        taxed_value = value + (self.data.banks[origin_bank].fee * value) if origin_bank != target_bank else value
        done = self.data.people[origin_id].accounts[origin_bank].draw(taxed_value, has_time_limit=is_time_limited)
        if done:
            self.data.banks[origin_bank].vault -= value
            self.data.banks[target_bank].vault += value
            self.data.people[target_id].accounts[target_bank].deposit(value)

            new_transaction.succeded = True
            self.__save_sys()
            popup_success_info(
                    f"\n\nO sistema automatizou a transferência: {self.data.people[origin_id].name} em {origin_bank} "
                    f"para "
                    f"{self.data.people[target_id].name} em {target_bank}\n")
        else:
            popup_error(f"Não há dinheiro suficiente na conta de origem. É nessessário ao menos R${taxed_value:.2f}")

        return new_transaction

    def screen_show_status(self):
        bank_amount = len(self.data.banks)
        people_amount = len(self.data.people)
        print(
                f"\nO sistema tem {people_amount} "
                f"{'pessoa cadastrada' if people_amount == 1 else 'pessoas cadastradas'} e "
                f"{bank_amount} {'banco cadrastado' if bank_amount == 1 else 'bancos cadrastados'}.\n")

        p_info = []
        for i, p in enumerate(list(self.data.people.values())):
            p_info.append(f"  {i + 1}. {p.name} - CPF: {p.cpf}")

        b_info = []
        for i, b in enumerate(list(self.data.banks.values())):
            b_info.append(f"  {i + 1}. {b.name} - Taxa de transferência externa: {b.fee * 100}%")

        window = tk.Toplevel()
        window.title("Status do Sistema")

        if people_amount != 0:
            left_frame = ScrollableFrame(window, title="Pessoas cadastradas:")
            left_frame.pack(side="top", fill="both", expand=True)

            for item in p_info:
                label = tk.Label(left_frame.scrollable_frame, text=item)
                left_frame.add_item(label)
        else:
            left_frame = ScrollableFrame(window, title="Não há pessoas cadastradas.")
            left_frame.pack(side="top", fill="both", expand=True)

        if bank_amount != 0:
            right_frame = ScrollableFrame(window, title="Bancos cadastrados:")
            right_frame.pack(side="top", fill="both", expand=True)

            for item in b_info:
                label = tk.Label(right_frame.scrollable_frame, text=item, font=("Segoe UI", 11))
                right_frame.add_item(label)
        else:
            right_frame = ScrollableFrame(window, title="Não há bancos cadastrados.")
            right_frame.pack(side="top", fill="both", expand=True)

        window.mainloop()

    def screen_create_bank(self):
        """
        Cadastra um banco no sistema.

        :param name: Nome do banco.
        """
        bnk = AddBankForm(tk.Toplevel(), self.__create_bank)
        bnk.show_form()
        self.current_form = bnk

    def screen_remove_bank(self):
        rm_bnk = RemoveBankForm(tk.Toplevel(), self.__remove_bank, list(self.data.banks.keys()))
        rm_bnk.show_form()
        self.current_form = rm_bnk

    def screen_create_person(self):
        """
        Cadastra uma pessoa no sistema.

        :param name: Nome da pessoa.
        :param cpf: Identificador único da pessoa.
        """
        prs = AddPersonForm(tk.Toplevel(), self.__create_person)
        prs.show_form()
        self.current_form = prs

    def screen_remove_person(self):
        rm_prs = RemovePersonForm(tk.Toplevel(), self.__remove_person,
                                  [p.name for p in list(self.data.people.values())])
        rm_prs.show_form()
        self.current_form = rm_prs

    def screen_get_person_data(self, cpf: int):
        try:
            print(f"\nDados da pessoa '{self.data.people[cpf].name}':")
            for acc in list(self.data.people[cpf].accounts.keys()):
                print(
                        f"\tValor no banco {acc} R${self.data.people[cpf].accounts[acc].balance:.2f}; Score "
                        f"relacionado: "
                        f"{self.data.people[cpf].accounts[acc].score:}")
            print("\n")
        except KeyError:
            print("A pessoa não foi encontrada no sistema!")

    def screen_open_account(self):
        """
        Cria uma conta para a pessoa indicada, no banco dado.
        """
        acc = OpenAccountForm(tk.Toplevel(), self.__sys_open_account, list(self.data.banks.keys()))
        acc.show_form()
        self.current_form = acc

    def screen_make_deposit(self):
        """
        Deposita o valor dado na conta da pessoa indicado, em seu respectivo banco.

        :param cpf: Identificador único da pessoa.
        :param bank: Banco responsável pela conta da pessoa.
        :param value: Valor do depósito.
        :return: Valor total da conta dessa pessoa após o depósito.
        """

        dpt = DepositForm(tk.Toplevel(), self.__make_deposit, list(self.data.banks.keys()))
        dpt.show_form()
        self.current_form = dpt

    def screen_make_draw(self, *, cpf: int, bank: str, value: float, has_time_limit=False):
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
            print(f"{self.data.people[cpf].name} realizou uma operação de saque em {bank}")

        except KeyError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")
        return drawed

    def screen_make_transfer(self):
        trf = TransferForm(tk.Toplevel(), self.__make_transfer, list(self.data.banks.keys()))
        trf.show_form()
        self.current_form = trf

    def screen_load_data(self):
        save_path = tkinter.filedialog.askopenfilename(defaultextension='syss', initialdir="/saves",
                                                       title="Selecione um SYS Save")
        self.__load_sys(save_path)