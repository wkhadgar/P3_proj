from __future__ import annotations
import random
import tkinter.filedialog
from interface import *
from sub_utils import *


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

        popup_info(f"Depositado R$ {amount:.2f} na conta, o novo total é de R${self.balance:.2f}")
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

            popup_info(f"Sacado R$ {amount:.2f} da conta, o novo total é de R${self.balance:.2f}")
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

        self.name: str = name.strip().title()
        self.cpf: int = cpf
        self.accounts: dict[str, Account] = {}

    def add_account(self, account_bank: str, *, value=0):
        """
        Cria uma conta para essa pessoa.

        :param account_bank: Banco responsável por essa conta.
        :param value: Valor inicial de abertura da conta, opcional.
        """

        if not (account_bank in self.accounts.keys()):
            self.accounts[account_bank] = Account(value)
        else:
            raise PermissionError

    def remove_account(self, account_bank):
        """
        Exclui a conta dessa pessoa no banco dado.

        :param account_bank: Nome do banco onde essa pessoa contém conta.
        """

        try:
            self.accounts.pop(account_bank)
        except KeyError:
            raise AccountNonExistent


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


class DepositAct(Transaction):
    def __init__(self, value: float, depositor: Person, target_bank: str):
        """
        Descreve um depósito.

        :param value: Valor da transação.
        :param depositor: Pessoa que depositará o valor.
        :param target_bank: Bbanco onde essa pessoa deseja realizar a operação.
        """

        if value < 0:
            value = 0
        super().__init__(value)

        try:
            self.depositor_acc: Account = depositor.accounts[target_bank]
        except KeyError:
            raise AccountNonExistent

        self.bank: str = target_bank
        self.info = (f"\tTipo: Depósito",
                     f"\tDepositante: {depositor.name}",
                     f"\tCPF: {cpf_string(depositor.cpf)}",
                     f"\tBanco do depósito: {target_bank}")

    def make(self):
        now = datetime.now()
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")

        self.depositor_acc.deposit(self.value)
        self.succeded = True
        return self.succeded


class DrawAct(Transaction):
    def __init__(self, value: float, withdrawer: Person, origin_bank: str):
        """
        Descreve um saque.

        :param value: Valor da transação.
        :param withdrawer: Pessoa que sacará o valor.
        :param origin_bank: Banco onde essa pessoa deseja realizar a operação.
        """

        if value < 0:
            value = 0
        super().__init__(value)

        try:
            self.withdrawer_acc: Account = withdrawer.accounts[origin_bank]
        except KeyError:
            raise AccountNonExistent

        self.bank: str = origin_bank
        self.has_limit: bool = self.withdrawer_acc.is_limited
        self.info = (f"\tTipo: Saque",
                     f"\tSacador: {withdrawer.name}",
                     f"\tCPF: {cpf_string(withdrawer.cpf)}",
                     f"\tBanco do saque: {origin_bank}")

    def make(self):
        self.succeded = self.withdrawer_acc.draw(self.value, has_time_limit=self.has_limit)
        if self.succeded:
            now = datetime.now()
            self.date = now.strftime("%d/%m/%Y %H:%M:%S")
        return self.succeded


class TransferAct(Transaction):
    def __init__(self, value: float, withdrawer: Person, origin_bank: str, depositor: Person, target_bank: str, fee=0):
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

        try:
            self.withdrawer_acc: Account = withdrawer.accounts[origin_bank]
            self.receiver_acc: Account = depositor.accounts[target_bank]
        except KeyError:
            raise AccountNonExistent

        self.origin_bank: str = origin_bank
        self.target_bank: str = target_bank

        self.has_limit: bool = self.withdrawer_acc.is_limited
        self.fee = fee

        self.info = (f"\tTipo: Transferência",
                     "\tOrigem:",
                     f"\t\tNome: {withdrawer.name}",
                     f"\t\tCPF: {cpf_string(withdrawer.cpf)}",
                     f"\t\tBanco: {origin_bank}",
                     "\tDestino:",
                     f"\t\tNome: {depositor.name}",
                     f"\t\tCPF: {cpf_string(depositor.cpf)}",
                     f"\t\tBanco: {target_bank}")

    def make(self):
        now = datetime.now()
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")

        taxed_value = self.value

        if self.origin_bank != self.target_bank:
            taxed_value += (self.fee * self.value)

        self.succeded = self.withdrawer_acc.draw(taxed_value, has_time_limit=self.has_limit)
        if self.succeded:
            self.receiver_acc.deposit(self.value)

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

        self.clients.pop(client.cpf).remove_account(self.name)
        self.clients_ammount -= 1


class SysData:
    def __init__(self):
        """
        Classe de encapsulamento de dados do sistema.
        """

        self.__transactions: dict[int, Transaction] = {}
        self.__banks: dict[str, Bank] = {}
        self.__people: dict[int, Person] = {}
        self.has_save: bool = False
        self.save_name: str = ""

    def add_person(self, name: str, cpf: int):
        if cpf in self.__people.keys():
            raise PermissionError

        self.__people[cpf] = Person(name, cpf)

    def remove_person(self, cpf):
        for acc in list(self.get_people(cpf).accounts.keys()):
            self.__banks[acc].close_account(self.__people[cpf])
        self.__people.pop(cpf)

    def get_people(self, cpf: int = None):
        if cpf is None:
            return self.__people

        if cpf not in self.__people.keys():
            raise PersonNonExistent

        return self.__people[cpf]

    def add_bank(self, bank: str, fee: float):
        if bank in self.__banks.keys():
            raise PermissionError

        self.__banks[bank] = Bank(bank, fee=fee)

    def remove_bank(self, bank: str):

        if self.get_banks(bank).clients_ammount != 0:
            raise PermissionError

        self.__banks.pop(bank)

    def get_banks(self, bank: str = None):
        if bank is None:
            return self.__banks

        if bank not in self.__banks.keys():
            raise BankNonExistent

        return self.__banks[bank]

    def add_transaction(self, transaction: Transaction):
        new_id = random.randint(0, 999_999_999)

        while new_id in tuple(self.__transactions.keys()):
            new_id = random.randint(0, 999_999_999_999)

        self.__transactions[new_id] = transaction
        return new_id

    def get_transactions(self, transaction_id: int = None):
        return self.__transactions if transaction_id is None else self.__transactions[transaction_id]

    def get_transaction_info(self, transaction_id: int) -> list:
        try:
            tr = self.get_transactions(transaction_id)
        except KeyError:
            return ["----Transação inválida----"]

        transaction_info = ["Informações:",
                            f'\tData da operação: {tr.date if tr.date != "" else "---"}',
                            f"\tValor da operação: R${tr.value:.2f}"]

        transaction_info.extend(tr.info)
        return transaction_info


class InputForm:
    def __init__(self, w_root: tk.Toplevel | tk.Tk, d_root: SysData, title: str, fields: dict, callback):
        self.window_root: tk.Toplevel | tk.Tk = w_root
        self.data_root: SysData = d_root
        self.title: str = title
        self.fields: dict[str, str] = fields
        self.inputs: list[tk.Entry] = []
        self.is_filled: bool = False
        self.icon_path: str = ""
        self.callback = callback

    def create_widgets(self, save_txt: str = "Salvar"):
        self.window_root.title(self.title.split(' ')[0])

        if self.icon_path:
            self.window_root.iconbitmap(self.icon_path)

        title_label = ttk.Label(self.window_root, text=self.title, font=("Arial", 16))
        title_label.pack(pady=10)

        for field_name, field_value in self.fields.items():
            frame = ttk.Frame(self.window_root)
            frame.pack(pady=5)
            label = ttk.Label(frame, text=field_name, font=("Arial", 12))
            label.pack(side="left", padx=10)
            if isinstance(field_value, list):
                input_field = ttk.Combobox(frame, font=("Arial", 12), values=field_value, state="readonly")
            else:
                input_field = ttk.Entry(frame, font=("Arial", 12))
            input_field.pack(side="right", padx=10)
            self.inputs.append(input_field)

        # Create save button
        save_button = ttk.Button(self.window_root, text=save_txt, command=self.save_inputs)
        save_button.pack(pady=10)

        self.inputs[0].focus()
        self.window_root.update()

    @abstractmethod
    def show_form(self):
        raise NotImplementedError("O método deve estar implementado na classe herdeira.")

    def get_fields(self) -> list[str]:
        fields = []
        if self.is_filled:
            for field_data in tuple(self.fields.values()):
                if field_data == "":
                    raise EmptyField
                else:
                    fields.append(field_data)

        return fields

    def save_inputs(self):
        for i, input_field in enumerate(list(self.fields.keys())):
            self.fields[input_field] = self.inputs[i].get()
        self.is_filled = True
        if self.callback is not None:
            self.callback()

        try:
            self.window_root.destroy()
            return 0
        except tk.TclError:
            return -1


class AddPerson(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "Nome:": "",
            "CPF:": "",
        }
        super().__init__(window_root, data_root, "Cadastro de Pessoa", fields, self.add)

    def show_form(self):
        self.create_widgets()

    def add(self):
        try:
            name, cpf = self.get_fields()
            cpf = int(cpf)
            self.data_root.add_person(name, cpf)
        except EmptyField:
            popup_warning("Dados inválidos!")
            return
        except ValueError:
            popup_warning("CPF inválido!")
            return
        except PermissionError:
            popup_error("Já existe uma pessoa com o CPF informado no sistema.")
            return

        save_sys(self.data_root)
        popup_info(f"A pessoa {name} foi cadastrada com sucesso.")


class RemovePerson(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "Pessoa:": [prs.name for prs in tuple(data_root.get_people().values())],
            "CPF:": "",
        }
        super().__init__(window_root, data_root, "Remoção de Pessoa", fields, self.remove)

    def show_form(self):
        self.create_widgets(save_txt="Remover")

    def remove(self):
        try:
            name, cpf = self.get_fields()
            cpf = int(cpf)
            if self.data_root.get_people(cpf).name == name:
                self.data_root.remove_person(cpf)
            else:
                popup_warning("O CPF informado não corresponde a pessoa que deseja remover.")
        except EmptyField:
            popup_warning("Preencha os dados corretamente!")
            return
        except ValueError:
            popup_error("CPF inválido!")
            return
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return

        save_sys(self.data_root)
        popup_info(f"A pessoa '{name}' foi removida do sistema com sucesso!")


class AddBank(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "Nome:": "",
            "Taxa: (%)": "0"
        }
        super().__init__(window_root, data_root, "Cadastro de Banco", fields, self.add)

    def show_form(self):
        self.create_widgets()

    def add(self):
        try:
            name, bank_fee = self.get_fields()
            bank_fee = float(bank_fee) / 100
            self.data_root.add_bank(name, bank_fee)
        except EmptyField:
            popup_warning("Preencha os dados corretamente!")
            return
        except ValueError:
            popup_error("Taxa incorreta!")
            return
        except PermissionError:
            popup_error("Banco já cadastrado no sistema.")
            return

        save_sys(self.data_root)
        popup_info(f"Banco {name} criado com sucesso.")


class RemoveBank(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "Banco:": list(self.data_root.get_banks().keys()),
        }
        super().__init__(window_root, data_root, "Remoção de Banco", fields, self.remove)

    def show_form(self):
        self.create_widgets(save_txt="Remover")

    def remove(self):
        try:
            name, = self.get_fields()
            self.data_root.remove_bank(name)
        except EmptyField:
            popup_warning("Selecione um banco!")
            return
        except PermissionError:
            popup_error(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")
            return

        save_sys(self.data_root)
        popup_info(f"O banco '{name}' foi removido do sistema com sucesso!")


class CheckPerson(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "CPF:": "",
        }
        super().__init__(window_root, data_root, "Pesquisa de Pessoa", fields, self.show_info)

    def show_form(self):
        self.create_widgets(save_txt="Pesquisar")

    def show_info(self):
        try:
            cpf, = self.get_fields()
            cpf = int(cpf)
            person = self.data_root.get_people(cpf)
        except ValueError:
            popup_warning("CPF inválido.")
            return
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

        if len(person.accounts.keys()) > 0:
            person_info.append(f"\tCPF: {cpf_string(cpf)}\n")

            for acc in list(person.accounts.keys()):
                bnk_balance = person.accounts[acc].balance
                bnk_score = person.accounts[acc].score
                person_info.append(f"\tSaldo no banco {acc}: R${bnk_balance:.2f};  Score relacionado: {bnk_score:.2f}")

                funds += bnk_balance
                mean_scr += bnk_score

            mean_scr /= len(person.accounts.keys())

            person_info.append("\nResumo total:")
            person_info.append(f"\tFundos totais:  R${funds:.2f}")
            person_info.append(f"\tMédia de score: {mean_scr:.2f} pontos.")

            frame = ScrollableFrame(window, f"Dados de {person.name}")
            frame.pack(side="top", fill="both", expand=True)
            for item in person_info:
                label = tk.Label(frame.scrollable_frame, text=item)
                frame.add_item(label)
        else:
            frame = ScrollableFrame(window, f"{person.name} não possui contas.")
            frame.pack(side="top", fill="both", expand=True)

        window.mainloop()


class OpenAccount(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "CPF:": "",
            "Banco:": [bank for bank in self.data_root.get_banks().keys()]
        }
        super().__init__(window_root, data_root, "Abertura de Conta", fields, self.open)

    def show_form(self):
        self.create_widgets(save_txt="Abrir")

    def open(self):
        try:
            owner_id, bank = self.get_fields()
            owner_id = int(owner_id)
            person = self.data_root.get_people(owner_id)
            self.data_root.get_banks(bank).open_account(person)
        except EmptyField:
            popup_warning("Preencha os campos corretamente!")
            return
        except ValueError:
            popup_warning("Digite um CPF válido!")
            return
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return
        except PermissionError:
            popup_error(f"{person.name} já possui conta em {bank}.")
            return

        save_sys(self.data_root)
        popup_info(f"A conta de {person.name} foi criada em {bank} com sucesso!")


class CloseAccount(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "CPF:": "",
            "Banco:": list(self.data_root.get_banks().keys()),
        }
        super().__init__(window_root, data_root, "Encerramento de Conta", fields, self.close)

    def show_form(self):
        self.create_widgets("Fechar")

    def close(self):
        try:
            cpf, bank = self.get_fields()
            cpf = int(cpf)
            person = self.data_root.get_people(cpf)
            self.data_root.get_banks(bank).close_account(person)
        except EmptyField:
            popup_warning("Preencha os campos corretamente!")
            return
        except ValueError:
            popup_warning("CPF inválido!")
            return
        except PersonNonExistent:
            popup_warning("O CPF informado não está cadastrado no sistema.")
            return
        except KeyError | AccountNonExistent:
            popup_warning("O cliente não contém conta neste banco.")
            return

        save_sys(self.data_root)
        popup_info(f"A conta de {person.name} em {bank} foi removida com sucesso!")


class Deposit(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "CPF:": "",
            "Banco:": list(self.data_root.get_banks().keys()),
            "Valor: R$": "",
        }
        super().__init__(window_root, data_root, "Depósito em conta", fields, self.make)

    def show_form(self):
        self.create_widgets(save_txt="Depositar")

    def make(self):
        try:
            cpf, bank, value = self.get_fields()
            cpf = int(cpf)
            person = self.data_root.get_people(cpf)
            bank = self.data_root.get_banks(bank)
        except EmptyField:
            popup_warning("Preencha os campos corretamente!")
            return
        except ValueError:
            popup_warning("CPF inválido!")
            return
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return

        try:
            value = float(value)
            new_dpt = DepositAct(value, person, bank.name)
        except ValueError:
            popup_warning("Valor inválido.")
            return
        except AccountNonExistent:
            popup_warning(f"{person.name} não possui conta em {bank}.")
            return

        new_dpt.make()
        bank.vault += value
        new_dpt.id_ = self.data_root.add_transaction(new_dpt)
        self.window_root.clipboard_clear()
        self.window_root.clipboard_append(str(new_dpt.id_))

        save_sys(self.data_root)
        popup_info(f"{person.name} realizou uma operação de depósito em {bank.name}\n"
                   f"ID: #{new_dpt.id_:09d}")


class Draw(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "CPF:": "",
            "Banco:": list(self.data_root.get_banks().keys()),
            "Valor: R$": "",
        }
        super().__init__(window_root, data_root, "Saque em conta", fields, self.make)

    def show_form(self):
        self.create_widgets(save_txt="Sacar")

    def make(self):
        try:
            cpf, bank, value = self.get_fields()
            cpf = int(cpf)
            withdrawer = self.data_root.get_people(cpf)
            bank = self.data_root.get_banks(bank)
        except EmptyField:
            popup_warning("Preencha os dados corretamente!")
        except ValueError:
            popup_warning("CPF inválido!")
            return
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return

        try:
            value = float(value)
            new_drw = DrawAct(value, withdrawer, bank.name)
        except ValueError:
            popup_warning("Valor inválido!")
            return
        except AccountNonExistent:
            popup_warning(f"{withdrawer.name} não possui conta em {bank.name}.")
            return

        if not new_drw.make():
            popup_error("Não foi possível realizar o saque.")

        new_drw.id_ = self.data_root.add_transaction(new_drw)
        bank.vault -= value
        self.window_root.clipboard_clear()
        self.window_root.clipboard_append(str(new_drw.id_))
        save_sys(self.data_root)
        popup_info(f"{withdrawer.name} realizou uma operação de saque em {bank.name}\n"
                   f"ID: #{new_drw.id_:09d}")


class Transfer(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "🡐 CPF:": "",
            "🡐 Banco:": list(self.data_root.get_banks().keys()),
            "🡓 Valor: R$": "",
            "🡒 CPF:": "",
            "🡒 Banco:": list(self.data_root.get_banks().keys()),
        }
        super().__init__(window_root, data_root, "Transferência entre contas", fields, self.make)

    def show_form(self):
        self.create_widgets(save_txt="Transferir")

    def make(self):
        try:
            origin_id, origin_bank, value, target_id, target_bank = self.get_fields()
            origin_id = int(origin_id)
            target_id = int(target_id)
            withdrawer = self.data_root.get_people(origin_id)
            depositor = self.data_root.get_people(target_id)
            origin_bank = self.data_root.get_banks(origin_bank)
            target_bank = self.data_root.get_banks(target_bank)
        except EmptyField:
            popup_warning("Preencha os dados corretamente!")
            return
        except ValueError:
            popup_warning("Confira os CPF's informados e tente novamente.")
            return
        except PersonNonExistent:
            popup_warning("A pessoa com o CPF informado não existe no sistema.")
            return

        try:
            value = float(value)
            new_trf = TransferAct(value, withdrawer, origin_bank.name,
                                  depositor, target_bank.name)
        except ValueError:
            popup_warning("Valor inválido")
            return
        except AccountNonExistent:
            popup_warning("Confira as contas informadas e tente novamente.")
            return

        if not new_trf.make():
            popup_error(f"Não foi possível realizar a operação.")

        new_trf.id_ = self.data_root.add_transaction(new_trf)

        save_sys(self.data_root)
        popup_info(
                f"\n\nO sistema automatizou a transferência: {withdrawer.name} em {origin_bank.name} "
                f"para {depositor.name} em {target_bank.name}\n"
                f"ID: #{new_trf.id_:09d}")


class TransactionSearch(InputForm):
    def __init__(self, window_root: tk.Toplevel, data_root: SysData):
        fields = {
            "ID #:": ""
        }
        super().__init__(window_root, data_root, "Pesquisa de Transação", fields, self.show)

    def show_form(self):
        self.create_widgets(save_txt="Pesquisar")

    def show(self):
        try:
            tr_id, = self.get_fields()
            tr_id = int(tr_id)
        except ValueError:
            popup_warning("ID inválido.")
            return

        window = tk.Toplevel()
        window.title("Dados de Transação")
        window.geometry("300x300")
        descr = ttk.Label(window, text=f"Transação #{tr_id}", font=("Arial", 12, "bold"))
        descr.pack(anchor="n", side="top")
        canvas = tk.Frame(window)

        transaction_info = self.data_root.get_transaction_info(tr_id)

        for item in transaction_info:
            label = tk.Label(canvas, text=item)
            label.pack(side="top", anchor="nw", padx=5)

        canvas.pack(side="top", fill="both", expand=True)

        window.mainloop()


class System(Interface):
    def __init__(self, root: tk.Tk):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """
        super().__init__(root)

        self.data: SysData = SysData()

    def screen_show_status(self):
        bank_amount = len(self.data.get_banks())
        people_amount = len(self.data.get_people())

        p_info = []
        for i, p in enumerate(list(self.data.get_people().values())):
            p_info.append(f"  {i + 1}. {p.name} - CPF: {cpf_string(p.cpf)}")

        b_info = []
        for i, b in enumerate(list(self.data.get_banks().values())):
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

    def create_person(self):
        AddPerson(tk.Toplevel(), self.data).show_form()

    def remove_person(self):
        RemovePerson(tk.Toplevel(), self.data).show_form()

    def create_bank(self):
        AddBank(tk.Toplevel(), self.data).show_form()

    def remove_bank(self):
        RemoveBank(tk.Toplevel(), self.data).show_form()

    def get_person_data(self):
        CheckPerson(tk.Toplevel(), self.data).show_form()

    def open_account(self):
        OpenAccount(tk.Toplevel(), self.data).show_form()

    def screen_make_deposit(self):
        Deposit(tk.Toplevel(), self.data).show_form()

    def screen_make_draw(self):
        Draw(tk.Toplevel(), self.data).show_form()

    def screen_make_transfer(self):
        trf = Transfer(tk.Toplevel(), self.data)
        trf.show_form()
        self.current_form = trf

    def screen_search_transaction(self):
        TransactionSearch(tk.Toplevel(), self.data).show_form()

    def load_data(self):
        save_path = tkinter.filedialog.askopenfilename(defaultextension='syss', initialdir="/saves",
                                                       title="Selecione um SYS Save")
        if save_path[-5:] == ".syss":
            save = bz2.BZ2File(save_path, 'rb')
            self.data = pickle.load(save)
            popup_info("Sistema recuperado.")
        else:
            if popup_retry('Selecione um arquivo válido "SAVE_dd-mm-yyyy_hh-mm.syss".'):
                self.load_data()