from __future__ import annotations
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from abc import ABC, abstractmethod


class PopUp:
    def __init__(self, description: str, title: str, alt_description: str = ""):
        self.title: str = title
        self.description: str = description
        self.alt_description: str = alt_description
        self.boolean: bool = False

    @abstractmethod
    def show(self):
        raise NotImplementedError("O método deve ser implementado na classe herdeira.")


class RetryCancelPopup(PopUp):
    def __init__(self, description: str, alt_description: str = ""):
        super().__init__(description, "Atenção!", alt_description)

    def show(self):
        self.boolean = tk.messagebox.askretrycancel(self.title, self.description + "\n" + self.alt_description)


class InfoPopup(PopUp):
    def __init__(self, description: str, alt_description: str = ""):
        super().__init__(description, "Informação:", alt_description)

    def show(self):
        self.boolean = tk.messagebox.showinfo(self.title, self.description + "\n" + self.alt_description)


class WarningPopup(PopUp):
    def __init__(self, description: str, alt_description: str = ""):
        super().__init__(description, "Atenção!", alt_description)

    def show(self):
        self.boolean = tk.messagebox.showwarning(self.title, self.description + "\n" + self.alt_description)


class ErrorPopup(PopUp):
    def __init__(self, description: str, alt_description: str = ""):
        super().__init__(description, "Erro crítico.", alt_description)

    def show(self):
        self.boolean = tk.messagebox.showerror(self.title, self.description + "\n" + self.alt_description)


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.title_label = tk.Label(self, text=title, font=("Arial", 12, "bold"))

        self.title_label.pack(side="top", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    @staticmethod
    def add_item(item: tk.Label):
        item.pack(side="top", padx=5, anchor="nw")


class Button:
    def __init__(self, label, command):
        self.label = label
        self.command = command


class AbstractState(ABC):
    def __init__(self, root, title: str, description: str = "", buttons: list["Button"] = None):
        self.root: tk.Tk | tk.Toplevel = root
        self.title: str = title
        self.description: str = description
        self.buttons: list["Button"] = buttons
        self.back_button: Button | None = None
        self.image: tk.PhotoImage | None = None

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

    def set_image(self, path: str):
        self.image = tk.PhotoImage(file=path)

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
            back_button_widget = ttk.Button(self.root, text=self.back_button.label,
                                            command=self.back_button.command)
            back_button_widget.pack(pady=5)

    def show_state(self):
        for child in self.root.winfo_children():
            child.destroy()

        self.create_widgets()


class Interface:
    def __init__(self, root):
        self.root: tk.Tk = root
        self.states: list[State] = []
        self.current_state = None

    def add_state(self, title, description, buttons):
        state = State(self.root, title, description, buttons)
        self.states.append(state)
        return state

    def run(self):
        self.states[0].show_state()
        self.root.mainloop()


def popup_retry(details: str = "") -> bool:
    """
    Emite um pop-up de nova tentativa.

    :param details: Detalhes do pop-up.
    :return bool: Se a pessoa deseja ou não tentar novamente.
    """

    rcb = RetryCancelPopup(details)
    rcb.show()
    return rcb.boolean


def popup_info(details: str = "", funnify: bool = False):
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