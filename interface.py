import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from abc import ABC, abstractmethod


# TODO usar menu do tkinter para mostrar as pessoas como uma lista
class PopUp:
    def __init__(self, description: str, title: str):
        self.title: str = title
        self.description: str = description
        self.boolean: bool = False

    @abstractmethod
    def show(self):
        raise NotImplementedError("O método deve ser implementado na classe herdeira.")


class RetryCancelPopup(PopUp):
    def __init__(self, description: str):
        super().__init__(description, "Atenção!")

    def show(self):
        self.boolean = tkinter.messagebox.askretrycancel(self.title, self.description)


class InputForm:
    def __init__(self, root: tk.Tk, title: str, fields: dict, callback):
        self.root: tk.Tk = root
        self.title: str = title
        self.fields: dict = fields
        self.inputs: list[tk.Entry] = []
        self.is_filled: bool = False
        self.icon_path: str = ""
        self.callback = callback

    def create_widgets(self, save_txt: str = "Salvar"):
        self.root.title(self.title.split(' ')[0])
        if self.icon_path:
            self.root.iconbitmap(self.icon_path)

        title_label = ttk.Label(self.root, text=self.title, font=("Arial", 16))
        title_label.pack(pady=10)

        for field in list(self.fields.keys()):
            frame = ttk.Frame(self.root)
            frame.pack(pady=5)
            label = ttk.Label(frame, text=field, font=("Arial", 12))
            label.pack(side="left", padx=10)
            input_field = ttk.Entry(frame, font=("Arial", 12))
            input_field.pack(side="right", padx=10)
            self.inputs.append(input_field)

        # Create save button
        save_button = ttk.Button(self.root, text=save_txt, command=self.save_inputs)
        save_button.pack(pady=10)

        self.inputs[0].focus()
        self.root.wm_attributes("-topmost", True)

    @abstractmethod
    def show_form(self):
        raise NotImplementedError("O método deve estar implementado na classe herdeira.")

    def save_inputs(self):
        for i, input_field in enumerate(list(self.fields.keys())):
            self.fields[input_field] = self.inputs[i].get()
        self.is_filled = True
        if self.callback is not None:
            self.callback()
        self.root.destroy()


class AddPersonForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "Nome:": "",
            "Idade:": "",
            "CPF:": "",
        }
        super().__init__(root, "Cadastro de Pessoa", fields, callback)

    def show_form(self):
        self.create_widgets()


class RemovePersonForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "CPF:": "",
        }
        super().__init__(root, "Remoção de Pessoa", fields, callback)

    def show_form(self):
        self.create_widgets()


class AddBankForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "Nome:": "",
        }
        super().__init__(root, "Cadastro de Banco", fields, callback)

    def show_form(self):
        self.create_widgets()


class RemoveBankForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "Nome:": "",
        }
        super().__init__(root, "Remoção de Banco", fields, callback)

    def show_form(self):
        self.create_widgets()


class OpenAccountForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "CPF:": "",
            "Banco:": "",
        }
        super().__init__(root, "Abertura de Conta", fields, callback)

    def show_form(self):
        self.create_widgets()


class CloseAccountForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "CPF:": "",
            "Banco:": "",
        }
        super().__init__(root, "Encerramento de Conta", fields, callback)

    def show_form(self):
        self.create_widgets()


class DepositForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "CPF:": "",
            "Banco:": "",
            "Valor: R$": "",
        }
        super().__init__(root, "Depósito em conta", fields, callback)

    def show_form(self):
        self.create_widgets()


class DrawForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "CPF:": "",
            "Banco:": "",
            "Valor: R$": "",
        }
        super().__init__(root, "Saque em conta", fields, callback)

    def show_form(self):
        self.create_widgets()


class TransferForm(InputForm):
    def __init__(self, root, callback=None):
        fields = {
            "🡐 CPF:": "",
            "🡐 Banco:": "",
            "🡓 Valor: R$": "",
            "🡒 CPF:": "",
            "🡒 Banco:": "",
        }
        super().__init__(root, "Transferência entre contas", fields, callback)

    def show_form(self):
        self.create_widgets()


class Button:
    def __init__(self, label, command):
        self.label = label
        self.command = command


class AbstractState(ABC):
    def __init__(self, root, title: str, description: str = "", buttons: list["Button"] = None):
        self.root = root
        self.title = title
        self.description = description
        self.buttons: list["Button"] = buttons
        self.back_button = None

    @abstractmethod
    def show_state(self):
        raise NotImplementedError("O método deve estar implementado na classe herdeira.")

    @abstractmethod
    def create_widgets(self):
        raise NotImplementedError("O método deve estar implementado na classe herdeira.")


class State(AbstractState):
    def __init__(self, root, title: str, description: str = "", buttons: list["Button"] = None):
        super().__init__(root, title, description, buttons)

    def set_back_button(self, label: str, command):
        self.back_button = Button(label, command)

    def create_widgets(self):
        # Create title label
        title_label = ttk.Label(self.root, text=self.title, font=("Segoe UI", 16))
        title_label.pack(pady=10)

        # Create description label
        desc_label = ttk.Label(self.root, text=self.description, font=("Segoe UI", 12))
        desc_label.pack(pady=5)

        # Create buttons
        for button in self.buttons:
            button_widget = ttk.Button(self.root, text=button.label, command=button.command)
            button_widget.pack(pady=5)

        # Create back button
        if self.back_button is not None:
            back_button_widget = ttk.Button(self.root, text=self.back_button.label, command=self.back_button.command)
            back_button_widget.pack(pady=5)

    def show_state(self):
        for child in self.root.winfo_children():
            child.destroy()

        self.create_widgets()


class Interface:
    def __init__(self, root):
        self.root = root
        self.states: list[State] = []
        self.current_state = None

    def add_state(self, title, description, buttons):
        state = State(self.root, title, description, buttons)
        self.states.append(state)
        return state

    def run(self):
        self.states[0].show_state()
        self.root.mainloop()