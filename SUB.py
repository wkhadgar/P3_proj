from __future__ import annotations
import random
import pickle
import tkinter.filedialog
from datetime import datetime
from interface import *


def popup_retry_cancel(details: str = "") -> bool:
    """
    Emite um pop-up de nova tentativa.

    :param details: Detalhes do pop-up.
    :return bool: Se a pessoa deseja ou não tentar novamente.
    """

    rcb = RetryCancelPopup(details)
    rcb.show()
    return rcb.boolean


def popup_success_info(details: str = "", funnify: bool = False):
    """
    Emite um pop-up de informação do sistema.

    :param details: Detalhes da informação.
    :param funnify: Deixar a informação divertida.
    """

    rcb = InfoPopup("Operação realizada com sucesso! \nContinue um bom servidor!" if funnify else "", details)
    rcb.show()


def popup_error(details: str = "", funnify: bool = False):
    """
    Emite um pop-up de erro do sistema.

    :param details: Detalhes do erro.
    :param funnify: Deixar o erro divertido.
    """

    err = ErrorPopup("Um erro ocorreu do lado do sistema. Não pedimos perdão.\nSeus créditos socias "
                     "foram deduzidos em 100 pontos. \n(Use o sistema de forma a não ocorrerem falhas)" if funnify
                     else "", details)
    err.show()


def popup_warning(details: str = "", funnify: bool = False):
    """
    Emite um pop-up de aviso do sistema.

    :param details: Detalhes do aviso.
    :param funnify: Deixar o aviso divertido.
    """

    wrn = WarningPopup("Um erro ocorreu, mas não foi do meu lado. Verifique os dados inseridos.\nPor sua "
                       "incopetencia seus créditos socias foram deduzidos em 700 pontos. (Erros de servidores são "
                       "punidos com pena máxima. Não os cometa novamente.)" if funnify else "", details)
    wrn.show()


def cpf_string(cpf: int) -> str:
    converted = str(cpf)
    converted = "0" * (11 - len(converted)) + converted
    converted = converted[0:3] + "." + converted[3:6] + "." + converted[6:9] + "-" + converted[9:11]
    return converted


class PersonNonExistent(Exception):
    def __init__(self):
        self.message = "A pessoa não foi encontrada no sistema."
        super().__init__(self.message)


class AccountNonExistent(Exception):
    def __init__(self):
        self.message = "A conta não foi encontrada no sistema."
        super().__init__(self.message)


class Account:
    def __init__(self, wallet_amount: float):
        """
        Descreve uma conta.
        A conta também contém uma pontuação agregada internamente.

        :param wallet_amount: Valor que a conta guarda no momento.
        """

        self.balance: float = wallet_amount
        self.score: float = 100  # Pontuação da conta.
        self.max_day_draw: float = 100_000
        self.max_night_draw: float = self.max_day_draw / 2
        self.is_limited: bool = False

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

    def draw(self, amount: float, *, has_time_limit=True):
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
                    popup_error(
                            f"Não foi possível sacar R${amount:.2f}, sua conta está com limite de saque por horário.")
                    return False

                if amount > self.max_day_draw:
                    popup_error(
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

        self.name: str = name.strip().capitalize()
        self.cpf: int = cpf
        self.accounts: dict[str, Account] = {}

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


class Transaction(ABC):
    def __init__(self, value: float):
        """
        Define uma transação.

        :param value: Valor associado a essa transação.
        """
        self.value: float = value

        self.id_: int = 0
        self.date: str = ""
        self.succeded: bool = False
        self.info = ""

    @abstractmethod
    def make(self):
        raise NotImplementedError("O método deve ser implementado nas classes herdeiras.")


class Deposit(Transaction):
    def __init__(self, value: float, depositor: Person, target_bank: Bank):
        """
        Descreve um depósito.

        :param value: Valor da transação.
        :param depositor: Pessoa que depositará o valor.
        :param target_bank: Bbanco onde essa pessoa deseja realizar a operação.
        """

        if value < 0:
            value = 0
        super().__init__(value)

        self.depositor: Person = depositor
        self.bank: Bank = target_bank
        self.info = (f"\tTipo: Depósito",
                     f"\tDepositante: {self.depositor.name}",
                     f"\tCPF: {cpf_string(self.depositor.cpf)}",
                     f"\tBanco do depósito: {self.bank.name}")

    def make(self):
        now = datetime.now()
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")

        self.depositor.accounts[self.bank.name].deposit(self.value)
        self.bank.vault += self.value
        self.succeded = True
        return self.succeded


class Draw(Transaction):
    def __init__(self, value: float, withdrawer: Person, origin_bank: Bank):
        """
        Descreve um saque.

        :param value: Valor da transação.
        :param withdrawer: Pessoa que sacará o valor.
        :param origin_bank: Banco onde essa pessoa deseja realizar a operação.
        """

        if value < 0:
            value = 0
        super().__init__(value)
        self.withdrawer: Person = withdrawer
        self.bank: Bank = origin_bank
        self.has_limit: bool = withdrawer.accounts[origin_bank.name].is_limited
        self.info = (f"\tTipo: Saque",
                     f"\tSacador: {self.withdrawer.name}",
                     f"\tCPF: {cpf_string(self.withdrawer.cpf)}",
                     f"\tBanco do saque: {self.bank.name}")

    def make(self):
        self.succeded = self.withdrawer.accounts[self.bank.name].draw(self.value, has_time_limit=self.has_limit)
        if self.succeded:
            now = datetime.now()
            self.date = now.strftime("%d/%m/%Y %H:%M:%S")

            self.bank.vault -= self.value

        return self.succeded


class Transfer(Transaction):
    def __init__(self, value: float, withdrawer: Person, origin_bank: Bank, depositor: Person, target_bank: Bank):
        """
        É uma forma de transação de retirada e depósito em sequência, tratada como transferência.
        Cada transferência contém um identificador aleatório e uma data atualizável que pode ser associada a sua
        realização.

        :param value: Valor da transação.
        :param withdrawer: Pessoa de origem da transação.
        :param origin_bank: Banco onde a pessoa de origem deseja usar sua conta.
        :param depositor: Pessoa de destino da transação.
        :param target_bank: Banco onde a pessoa de destino usará sua conta.
        """

        super().__init__(value)

        self.withdrawer: Person = withdrawer
        self.origin_bank: Bank = origin_bank
        self.has_limit: bool = withdrawer.accounts[origin_bank.name].is_limited

        self.receiver: Person = depositor
        self.target_bank: Bank = target_bank
        self.info = (f"\tTipo: Transferência",
                     "\tOrigem:",
                     f"\t\tNome: {self.withdrawer.name}",
                     f"\t\tCPF: {cpf_string(self.withdrawer.cpf)}",
                     f"\t\tBanco: {self.origin_bank.name}",
                     "\tDestino:",
                     f"\t\tNome: {self.receiver.name}",
                     f"\t\tCPF: {cpf_string(self.receiver.cpf)}",
                     f"\t\tBanco: {self.target_bank.name}")

    def make(self):
        now = datetime.now()
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")

        taxed_value = self.value

        if self.origin_bank != self.target_bank:
            taxed_value += (self.origin_bank.fee * self.value)

        self.succeded = self.withdrawer.accounts[self.origin_bank.name].draw(taxed_value, has_time_limit=self.has_limit)
        if self.succeded:
            self.origin_bank.vault -= self.value
            self.target_bank.vault += self.value
            self.receiver.accounts[self.target_bank.name].deposit(self.value)

        return self.succeded


class Bank:
    def __init__(self, name: str, *, fee: float = 0):
        """
        Descreve um banco.

        Os bancos contêm um cofre relacionado ao patrimônio do banco, somado ao capital de seus clientes.
        Além de opcionalmente conter uma taxa de transações.

        :param name: Nome do banco.
        :param fee: Taxa, opcional, que pode ser usada sobre as operações.
        """

        self.name: str = name.strip()
        self.clients: dict[int, Person] = {}
        self.vault: float = 10000
        self.fee: float = fee
        self.clients_ammount: int = 0

    def open_account(self, client: Person):
        """
        Abre uma conta no banco
        :param client: Pessoa a ter uma conta nesse banco vinculada.
        """

        self.clients[client.cpf] = client
        self.clients[client.cpf].add_account(self.name)
        self.clients_ammount += 1

    def close_account(self, client: Person):
        """
        Fecha uma conta no banco
        :param client: Pessoa a ter sua conta nesse banco removida.
        """

        try:
            self.clients[client.cpf].accounts.pop(self.name)
            self.clients.pop(client.cpf)
            self.clients_ammount -= 1
        except KeyError:
            self.clients_ammount += 1


class SysData:
    def __init__(self):
        """
        Classe de encapsulamento de dados do sistema.
        """

        self.transactions: dict[int, Transaction] = {}
        self.banks: dict[str, Bank] = {}
        self.people: dict[int, Person] = {}

    def get_transaction_info(self, transaction_id: int) -> list:
        transaction_info = ["Informações:",
                            f'\tData da operação: '
                            f'{self.transactions[transaction_id].date if self.transactions[transaction_id].date != "" else "---"}',
                            f"\tValor da operação: R${self.transactions[transaction_id].value:.2f}"]

        transaction_info.extend(self.transactions[transaction_id].info)
        return transaction_info


class System(Interface):
    def __init__(self, root: tk.Tk):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """
        super().__init__(root)

        self.data: SysData = SysData()
        self.current_form: InputForm | None = None
        self.has_save: bool = False
        self.save_name: str = ""

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
            if popup_retry_cancel('Selecione um arquivo válido "SAVE_dd-mm-yyyy_hh-mm.syss".'):
                self.screen_load_data()

    def __generate_transaction_id(self, transaction: Transaction):
        new_id = random.randint(0, 999_999_999)

        while new_id in list(self.data.transactions.keys()):
            new_id = random.randint(0, 999_999_999)

        self.data.transactions[new_id] = transaction
        self.root.clipboard_clear()
        self.root.clipboard_append(str(new_id))
        return new_id

    def __create_person(self):
        try:
            name, cpf = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        if name == "":
            popup_warning("Nome inválido!")
            return

        try:
            cpf = int(cpf)
        except ValueError:
            popup_warning("CPF inválido.")
            return

        self.data.people[cpf] = Person(name, cpf)
        self.__save_sys()
        popup_success_info(f"A pessoa {name} cadastrada com sucesso.")

    def __remove_person(self):
        try:
            name, cpf = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        try:
            cpf = int(cpf)
        except ValueError:
            popup_warning("CPF inválido.")
            return

        try:
            self.__person_exists(cpf)
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return

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

    def __create_bank(self):
        try:
            name, bank_fee = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

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
        try:
            name, = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        if name == "":
            popup_warning("Selecione um banco!")
            return

        if self.data.banks[name].clients_ammount == 0:
            self.data.banks.pop(name)
            self.__save_sys()
            popup_success_info(f"O banco '{name}' foi removido do sistema com sucesso!")
        else:
            popup_error(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")

    def __show_person_data(self):
        try:
            cpf, = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        try:
            cpf = int(cpf)
        except ValueError:
            if popup_retry_cancel("CPF inválido."):
                self.screen_get_person_data()
            return

        try:
            self.__person_exists(cpf)
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return

        window = tk.Toplevel()
        window.wm_geometry("500x300")
        window.title(f"Dados Pessoais")
        window.lift()

        person_info = [f"\nInformações:"]
        mean_scr = 0
        funds = 0

        if len(self.data.people[cpf].accounts.keys()) > 0:
            person_info.append(f"\tCPF: {cpf_string(cpf)}\n")

            for acc in list(self.data.people[cpf].accounts.keys()):
                bnk_balance = self.data.people[cpf].accounts[acc].balance
                bnk_score = self.data.people[cpf].accounts[acc].score
                person_info.append(f"\tSaldo no banco {acc}: R${bnk_balance:.2f};  Score relacionado: {bnk_score:.2f}")

                funds += bnk_balance
                mean_scr += bnk_score

            mean_scr /= len(self.data.people[cpf].accounts.keys())

            person_info.append("\nResumo total:")
            person_info.append(f"\tFundos totais:  R${funds:.2f}")
            person_info.append(f"\tMédia de score: {mean_scr:.2f} pontos.")

            frame = ScrollableFrame(window, f"Dados de {self.data.people[cpf].name}")
            frame.pack(side="top", fill="both", expand=True)
            for item in person_info:
                label = tk.Label(frame.scrollable_frame, text=item)
                frame.add_item(label)
        else:
            frame = ScrollableFrame(window, f"{self.data.people[cpf].name} não possui contas.")
            frame.pack(side="top", fill="both", expand=True)

        window.mainloop()

    def __sys_open_account(self):
        try:
            owner_id, bank = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        if bank == "":
            popup_warning("Selecione um banco!")
            return

        try:
            owner_id = int(owner_id)
        except ValueError:
            if popup_retry_cancel("Digite um CPF válido."):
                self.screen_open_account()
            return

        try:
            self.__person_exists(owner_id)
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return

        self.data.banks[bank].open_account(self.data.people[owner_id])
        self.__save_sys()
        popup_success_info(f"A conta de {self.data.people[owner_id].name} foi criada em {bank} com sucesso!")

    def __make_deposit(self):
        try:
            cpf, bank, value = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        try:
            cpf = int(cpf)
        except ValueError:
            popup_warning("CPF inválido.")
            return

        bank = self.current_form.fields["Banco:"]
        if bank == "":
            popup_warning("Selecione um banco!")
            return

        try:
            value = float(value)
        except ValueError:
            popup_warning("Valor inválido.")
            return

        try:
            self.__person_and_account_exists(cpf, bank)
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return
        except AccountNonExistent:
            popup_warning(f"{self.data.people[cpf].name} não possui conta em {bank}.")
            return

        new_dpt = Deposit(value, self.data.people[cpf], self.data.banks[bank])
        new_dpt.make()
        new_dpt.id_ = self.__generate_transaction_id(new_dpt)

        self.__save_sys()
        popup_success_info(f"{self.data.people[cpf].name} realizou uma operação de depósito em {bank}\n"
                           f"ID: #{new_dpt.id_:09d}")

    def __make_draw(self):
        try:
            cpf, bank, value = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        try:
            cpf = int(cpf)
        except ValueError:
            if popup_retry_cancel("CPF inválido. Deseja tentar novamente?"):
                self.screen_make_draw()
            return

        try:
            value = float(value)
        except ValueError:
            if popup_retry_cancel("Valor inválido. Deseja tentar novamente?"):
                self.screen_make_draw()
            return

        try:
            self.__person_and_account_exists(cpf, bank)
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return
        except AccountNonExistent:
            popup_warning(f"{self.data.people[cpf].name} não possui conta em {bank}.")
            return

        new_drw = Draw(value, self.data.people[cpf], self.data.banks[bank])
        if new_drw.make():
            new_drw.id_ = self.__generate_transaction_id(new_drw)

            self.__save_sys()
            popup_success_info(f"{self.data.people[cpf].name} realizou uma operação de saque em {bank}\n"
                               f"ID: #{new_drw.id_:09d}")
        else:
            popup_error("Não foi possível realizar o saque.")

    def __make_transfer(self):
        try:
            origin_id, origin_bank, value, target_id, target_bank = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        if origin_bank == "" or target_bank == "":
            popup_warning("Selecione os bancos!")
            return

        try:
            value = float(value)
        except ValueError:
            popup_warning("Valor inválido")
            return

        try:
            origin_id = int(origin_id)
        except ValueError:
            popup_warning("CPF de origem inválido.")
            return

        try:
            target_id = int(target_id)
        except ValueError:
            popup_warning("CPF de destino inválido.")
            return

        try:
            self.__person_and_account_exists(origin_id, origin_bank)
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return
        except AccountNonExistent:
            popup_warning(f"{self.data.people[origin_id].name} não possui conta em {origin_bank}.")
            return

        try:
            self.__person_and_account_exists(target_id, target_bank)
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return
        except AccountNonExistent:
            popup_warning(f"{self.data.people[target_id].name} não possui conta em {target_bank}.")
            return

        new_trf = Transfer(value, self.data.people[origin_id], self.data.banks[origin_bank],
                           self.data.people[target_id], self.data.banks[target_bank])

        if new_trf.make():
            new_trf.id_ = self.__generate_transaction_id(new_trf)

            self.__save_sys()
            popup_success_info(
                    f"\n\nO sistema automatizou a transferência: {self.data.people[origin_id].name} em {origin_bank} "
                    f"para {self.data.people[target_id].name} em {target_bank}\n"
                    f"ID: #{new_trf.id_:09d}")
        else:
            popup_error(f"Não foi possível realizar a operação.")

        return new_trf

    def __person_exists(self, cpf: int):
        if cpf not in list(self.data.people.keys()):
            raise PersonNonExistent

    def __person_and_account_exists(self, cpf: int, bank: str):
        self.__person_exists(cpf)
        if bank not in list(self.data.people[cpf].accounts.keys()):
            raise AccountNonExistent

    def __show_transaction_info(self):
        try:
            tr_id, = self.current_form.get_fields()
        except ValueError:
            popup_error("Houve um erro interno do sistema.\nTente novamente.")
            return

        try:
            tr_id = int(tr_id)
        except ValueError:
            popup_warning("ID inválido.")
            return

        if tr_id not in list(self.data.transactions.keys()):
            popup_warning(f"Não existe transação com o ID {tr_id}")
            return

        this_transaction = self.data.transactions[tr_id]

        window = tk.Toplevel()
        window.title("Dados de Transação")
        window.geometry("300x300")
        descr = ttk.Label(window, text=f"Transação #{tr_id}", font=("Arial", 12, "bold"))
        descr.pack(anchor="n", side="top")
        canvas = tk.Frame(window)

        transaction_info = self.data.get_transaction_info(tr_id)

        for item in transaction_info:
            label = tk.Label(canvas, text=item)
            label.pack(side="top", anchor="nw", padx=5)

        canvas.pack(side="top", fill="both", expand=True)

        window.mainloop()

    def screen_show_status(self):
        bank_amount = len(self.data.banks)
        people_amount = len(self.data.people)

        p_info = []
        for i, p in enumerate(list(self.data.people.values())):
            p_info.append(f"  {i + 1}. {p.name} - CPF: {cpf_string(p.cpf)}")

        b_info = []
        for i, b in enumerate(list(self.data.banks.values())):
            b_info.append(f"  {i + 1}. {b.name} - Taxa de T.E.: {b.fee * 100}%")

        window = tk.Toplevel()
        window.title("Status do Sistema")
        window.geometry("400x700")

        if people_amount != 0:
            ending = '' if people_amount == 1 else 's'
            left_frame = ScrollableFrame(window, title=f"{people_amount} pessoa{ending} cadastrada{ending}:")
            left_frame.pack(side="top", fill="both", expand=True)

            for item in p_info:
                label = tk.Label(left_frame.scrollable_frame, text=item)
                left_frame.add_item(label)
        else:
            left_frame = ScrollableFrame(window, title="Não há pessoas cadastradas.")
            left_frame.pack(side="top", fill="both", expand=True)

        if bank_amount != 0:
            ending = '' if bank_amount == 1 else 's'
            right_frame = ScrollableFrame(window, title=f"{bank_amount} banco{ending} cadastrado{ending}:")
            right_frame.pack(side="top", fill="both", expand=True)

            for item in b_info:
                label = tk.Label(right_frame.scrollable_frame, text=item)
                right_frame.add_item(label)
        else:
            right_frame = ScrollableFrame(window, title="Não há bancos cadastrados.")
            right_frame.pack(side="top", fill="both", expand=True)

        window.mainloop()

    def screen_create_bank(self):
        bnk = AddBankForm(tk.Toplevel(), self.__create_bank)
        bnk.show_form()
        self.current_form = bnk

    def screen_remove_bank(self):
        rm_bnk = RemoveBankForm(tk.Toplevel(), self.__remove_bank, list(self.data.banks.keys()))
        rm_bnk.show_form()
        self.current_form = rm_bnk

    def screen_create_person(self):
        prs = AddPersonForm(tk.Toplevel(), self.__create_person)
        prs.show_form()
        self.current_form = prs

    def screen_remove_person(self):
        rm_prs = RemovePersonForm(tk.Toplevel(), self.__remove_person,
                                  [p.name for p in list(self.data.people.values())])
        rm_prs.show_form()
        self.current_form = rm_prs

    def screen_get_person_data(self):
        prs = CheckPersonForm(tk.Toplevel(), self.__show_person_data)
        prs.show_form()
        self.current_form = prs

    def screen_open_account(self):
        acc = OpenAccountForm(tk.Toplevel(), self.__sys_open_account, list(self.data.banks.keys()))
        acc.show_form()
        self.current_form = acc

    def screen_make_deposit(self):
        dpt = DepositForm(tk.Toplevel(), self.__make_deposit, list(self.data.banks.keys()))
        dpt.show_form()
        self.current_form = dpt

    def screen_make_draw(self):
        drf = DrawForm(tk.Toplevel(), self.__make_draw, list(self.data.banks.keys()))
        drf.show_form()
        self.current_form = drf

    def screen_make_transfer(self):
        trf = TransferForm(tk.Toplevel(), self.__make_transfer, list(self.data.banks.keys()))
        trf.show_form()
        self.current_form = trf

    def screen_search_transaction(self):

        stf = TransactionSearchForm(tk.Toplevel(), self.__show_transaction_info)
        stf.show_form()
        self.current_form = stf

    def screen_load_data(self):
        save_path = tkinter.filedialog.askopenfilename(defaultextension='syss', initialdir="/saves",
                                                       title="Selecione um SYS Save")
        self.__load_sys(save_path)