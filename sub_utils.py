from datetime import datetime
import bz2
import _pickle as pickle


class PersonNonExistent(Exception):
    def __init__(self):
        self.message = "A pessoa não foi encontrada no sistema."
        super().__init__(self.message)


class BankNonExistent(Exception):
    def __init__(self):
        self.message = "O Banco não foi encontrado no sistema."
        super().__init__(self.message)


class AccountNonExistent(Exception):
    def __init__(self):
        self.message = "A conta não foi encontrada no sistema."
        super().__init__(self.message)


class EmptyField(Exception):
    def __init__(self):
        self.message = "Campo não preenchido."
        super().__init__(self.message)


def cpf_string(cpf: int) -> str:
    converted = str(cpf)
    converted = "0" * (11 - len(converted)) + converted
    converted = converted[0:3] + "." + converted[3:6] + "." + converted[6:9] + "-" + converted[9:11]
    return converted


def save_sys(system_data):
    if not system_data.has_save:
        now = datetime.now().strftime("%d-%m-%Y_%H-%M")
        system_data.save_name = "SAVE_" + now + ".syss"
        system_data.has_save = True

    with bz2.BZ2File("saves/" + system_data.save_name, 'w') as save:
        pickle.dump(system_data, save)