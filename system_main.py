from datetime import datetime
import random


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
        self._id = 0
        self.succeded = False

        self.origin_person = origin_id
        self.origin_bank = origin_bank

        self.target_person = target_id
        self.target_bank = target_bank

        self.date = ""


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


class System:
    def __init__(self):
        """
        Descreve um sistema. É o ponto de entrada do sistema, todas as operações são realizados sob o esse escopo.

        Os sistemas armazenam as pessoas e os bancos, além de manusear as operações que as envolvem.
        """

        self.transactions = {}
        self.banks = {}
        self.people = {}

    def show_status(self):
        bank_amount = len(self.banks)
        people_amount = len(self.people)
        print(
            f"\nO sistema tem {people_amount} {'pessoa cadastrada' if people_amount == 1 else 'pessoas cadastradas'} e "
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

    def create_bank(self, *, name: str, bank_fee: float):
        """
        Cadastra um banco no sistema.

        :param name: Nome do banco.
        """

        self.banks[name] = Bank(name, fee=bank_fee)
        print(f"Banco {name} criado com sucesso.")

    def remove_bank(self, *, name: str):
        try:
            if self.banks[name].clients_ammount == 0:
                self.banks.pop(name)
                print(f"O banco '{name}' foi removido do sistema com sucesso!")
            else:
                print(f"Não foi possível excluir o banco, pois ainda há clientes cadastrados nele.")
        except KeyError:
            print("Banco não encontrado no sistema!")

    def create_person(self, *, name, cpf: int):
        """
        Cadastra uma pessoa no sistema.

        :param name: Nome da pessoa.
        :param cpf: Identificador único da pessoa.
        """

        self.people[cpf] = Person(name, cpf)
        print(f"A pessoa {name} cadastrada com sucesso.")

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
                    f"\tValor no banco {acc} R${self.people[cpf].accounts[acc].balance:.2f}; Score relacionado: {self.people[cpf].accounts[acc].score:}")
            print("\n")
        except KeyError:
            print("A pessoa não foi encontrada no sistema!")

    def sys_open_account(self, owner_id: int, bank: str):
        """
        Cria uma conta para a pessoa indicada, no banco dado.

        :param owner_id: Identficador único do dono da conta.
        :param bank: Banco responsável pela conta criada.
        """

        self.banks[bank].open_account(self.people[owner_id])
        print(f"A conta de {self.people[owner_id].name} foi criada em {bank} com sucesso!")

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
            print(f"{self.people[cpf].name} realizou uma operação de depósito em {bank}")
            total = self.people[cpf].accounts[bank].deposit(value)
            self.banks[bank].vault += value
        except KeyError:
            print("O banco ou a pessoa não existe.\n")
        print("________________________________________________________\n")

        return total

    def sys_draw(self, *, cpf: int, bank: str, value: float, has_time_limit=False):
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

    def generate_transaction_id(self, transaction: Transaction):
        new_id = random.randint(0, 999_999_999)

        while new_id in list(self.transactions.keys()):
            new_id = random.randint(0, 999_999_999)

        self.transactions[new_id] = transaction
        return new_id

    def make_transfer(self, *, value: float, origin_id: int, origin_bank: str, target_id: int, target_bank: str,
                      is_time_limited=False):
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

        new_transaction = Transaction(value, origin_id, origin_bank, target_id, target_bank)

        now = datetime.now()
        new_transaction.date = now.strftime("%d/%m/%Y %H:%M:%S")
        new_transaction._id = self.generate_transaction_id(new_transaction)

        try:
            taxed_value = value + self.banks[origin_bank].fee * value if origin_bank != target_bank else value
            print(
                f"\n\nO sistema automatizou a transferência: {self.people[origin_id].name} em {origin_bank} para "
                f"{self.people[target_id].name} em {target_bank}\n")
            done = self.sys_draw(cpf=origin_id, bank=origin_bank, value=taxed_value, has_time_limit=is_time_limited)
            if done != 0:
                new_transaction.succeded = True
                self.banks[origin_bank].vault += taxed_value - value
                self.sys_deposit(cpf=target_id, bank=target_bank, value=value)
            else:
                pass
        except KeyError:
            print("Erro!!")

        return new_transaction


sys = System()

do_demo = 0
if do_demo:
    print("\nDemo de utilização sistema:\n")
    main_bank = input("Digite o nome do primeiro banco a ser criado: ").strip()
    fee = 0.01

    sys.create_bank(name=main_bank, bank_fee=fee)

    other_bank = input("Digite o nome do segundo banco a ser criado: ").strip()
    sys.create_bank(name=other_bank, bank_fee=fee)

    giver_name = input("Digite o nome da pessoa que vai realizar a transferencia: ")
    giver_cpf = int(input("Digite o CPF dessa pessoa: "))
    sys.create_person(name=giver_name, cpf=giver_cpf)

    receiver_name = input("Digite o nome da pessoa que vai receber a transferencia: ")
    receiver_cpf = int(input("Digite o CPF dessa pessoa: "))
    sys.create_person(name=receiver_name, cpf=receiver_cpf)

    sys.show_status()

    sys.sys_open_account(giver_cpf, main_bank)
    sys.sys_open_account(receiver_cpf, main_bank)
    sys.sys_open_account(receiver_cpf, other_bank)

    sys.sys_deposit(cpf=giver_cpf, bank=main_bank,
                    value=float(input(f"Qual valor que será depositado inicialmente na conta do {giver_name}?\n"
                                      f"-> R$ ")))

    sys.make_transfer(value=float(input(f"Qual valor que será transferido para o {receiver_name} (mesmo banco)?\n"
                                        f"-> R$ ")),
                      origin_id=giver_cpf, origin_bank=main_bank, target_id=receiver_cpf, target_bank=main_bank)

    sys.make_transfer(
        value=float(input(f"Qual valor que será transferido para o {receiver_name} (bancos diferentes) ?\n"
                          f"-> R$ ")),
        origin_id=giver_cpf, origin_bank=main_bank, target_id=receiver_cpf, target_bank=other_bank)

    sys.get_person_data(receiver_cpf)
    sys.get_person_data(giver_cpf)

    sys.remove_person(giver_cpf)
    sys.remove_person(receiver_cpf)
    sys.remove_bank(name=main_bank)

    sys.show_status()

print("\n\n\n\n\n")

run = True
current_state = 'main_menu'
while run:

    if current_state == 'main_menu':
        print("\n\n\nBem-vindo ao SUB, o que deseja fazer?")
        print("[0] - Encerrar.")
        print("[1] - Cadastro.")
        print("[2] - Remoção.")
        print("[3] - Financeiro.")
        print("[4] - Informações.")

        option = int(input("-> "))
        if option == 0:
            run = False
            break
        elif option == 1:
            current_state = 'sign_menu'
        elif option == 2:
            current_state = 'delete_menu'
        elif option == 3:
            current_state = 'transactions_menu'
        elif option == 4:
            current_state = 'info_menu'

    elif current_state == 'sign_menu':
        print()
        print("[1] - Cadastrar nova pessoa.")
        print("[2] - Cadastrar novo banco.")
        print("[3] - Criar conta em banco para pessoa cadastrada.")
        print("[4] - Voltar.")

        option = int(input("-> "))

        if option == 1:
            name = input("Digite o nome da pessoa: ")
            cpf = int(input("Digite o CPF dessa pessoa: "))
            sys.create_person(name=name, cpf=cpf)

        elif option == 2:
            bank = input("Digite o nome do banco a ser criado: ").strip()
            fee = float(int(input("Qual a taxa de transferência externa desse banco, em %: ")) / 100)

            sys.create_bank(name=bank, bank_fee=fee)

        elif option == 3:
            cpf = int(input("Digite o CPF da pessoa que abrirá a conta: "))
            bank = input("Digite o nome do banco onde a conta será criada: ").strip()
            sys.sys_open_account(cpf, bank)

        elif option == 4:
            current_state = 'main_menu'

    elif current_state == 'delete_menu':
        print()
        print("[1] - Remover pessoa existente.")
        print("[2] - Remover banco existente.")
        print("[3] - Voltar.")

        option = int(input("-> "))

        if option == 1:
            cpf = int(input("Digite o CPF dessa pessoa: "))
            sys.remove_person(cpf)

        elif option == 2:
            bank = input("Digite o nome do banco a ser removido: ").strip()
            sys.remove_bank(name=bank)

        elif option == 3:
            current_state = 'main_menu'

    elif current_state == 'transactions_menu':
        print()
        print("[1] - Realizar depósito em conta.")
        print("[2] - Realizar saque de conta.")
        print("[3] - Realizar transferência automatizada entre pessoas.")
        print("[4] - Voltar.")

        option = int(input("-> "))

        if option == 1:
            cpf = int(input("Digite o CPF dessa pessoa: "))
            bank = input("Digite o banco no qual deve ser feito o depósito:").strip()
            sys.sys_deposit(cpf=cpf, bank=bank,
                            value=float(input(f"Qual valor que será depositado na conta?\n"
                                              f"-> R$ ")))
        elif option == 2:
            cpf = int(input("Digite o CPF dessa pessoa: "))
            bank = input("Digite o banco no qual deve ser feito o saque:").strip()
            do_limit = True if input("O saque deve ser limitado?\n"
                                     "[s] - Sim\n"
                                     "[n] - Não\n"
                                     "-> ") == 's' else False
            sys.sys_draw(cpf=cpf, bank=bank,
                         value=float(input(f"Qual valor que será reitrado da conta?\n"
                                           f"-> R$ ")), has_time_limit=do_limit)
        elif option == 3:
            giver_cpf = int(input("Digite o cpf da pessoa que vai realizar a transferencia: "))
            giver_bank = input("Digite o banco no qual deve ser feito o saque:").strip()

            receiver_cpf = int(input("Digite o cpf da pessoa que vai receber a transferencia: "))
            receiver_bank = input("Digite o banco no qual deve ser feito o depósito:").strip()

            do_limit = True if input("A transferência deve ser limitada?\n"
                                     "[s] - Sim\n"
                                     "[n] - Não\n"
                                     "-> ") == 's' else False

            sys.make_transfer(
                value=float(input(f"Qual valor que será transferido?\n"
                                  f"-> R$ ")),
                origin_id=giver_cpf, origin_bank=giver_bank, target_id=receiver_cpf, target_bank=receiver_bank,
                is_time_limited=do_limit)

        elif option == 4:
            current_state = 'main_menu'

    elif current_state == 'info_menu':
        print()
        print("[1] - Mostrar status do sistema.")
        print("[2] - Mostrar dados de uma pessoa.")
        print("[3] - Voltar.")

        option = int(input("-> "))

        if option == 1:
            sys.show_status()
        elif option == 2:
            cpf = int(input("Digite o CPF dessa pessoa: "))
            sys.get_person_data(cpf)
        elif option == 3:
            current_state = 'main_menu'