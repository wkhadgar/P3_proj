import SUB as sub
from interface import tk, ttk, Button

root = tk.Tk()
root.geometry("500x310")
root.iconbitmap(default=r"assets/SUB_ico.ico")
root.wm_title("Sistema Único de Bancos")
style = ttk.Style(root)
style.theme_use("clam")  # ou "alt", "default", e "classic"

sys = sub.System(root)

# TODO Criar o sub-estado de halt com transição automática.

# Montagem do menu principal
main_menu_buttons = [
    Button("Cadastro", lambda: signup_menu_state.show_state()),
    Button("Remoção", lambda: remove_menu_state.show_state()),
    Button("Financeiro", lambda: finances_menu_state.show_state()),
    Button("Mais", lambda: info_menu_state.show_state()),
    Button("Encerrar", root.destroy),
]
main_menu_state = sys.add_state("SUB", "Bem vindo ao SUB - Sistema Único de Bancos. O que deseja fazer?",
                                main_menu_buttons)

# Montagem do menu de cadastro
signup_menu_buttons = [
    Button("Cadastro de Pessoa", sys.create_person),
    Button("Cadastro de Banco", sys.create_bank),
    Button("Criar conta em banco para pessoa", sys.open_account),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
signup_menu_state = sys.add_state("Cadastro", "Qual cadastro deseja realizar?", signup_menu_buttons)

# Montagem do menu de remoção
remove_menu_buttons = [
    Button("Remoção de Pessoa", sys.remove_person),
    Button("Remoção de Banco", sys.remove_bank),
    Button("Fechamento de conta", sys.close_account),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
remove_menu_state = sys.add_state("Remoção", "Qual remoção deseja realizar?", remove_menu_buttons)

# Montagem do menu de finanças
finances_menu_buttons = [
    Button("Depósito", sys.make_deposit),
    Button("Saque", sys.make_draw),
    Button("Transferência", sys.make_transfer),
    Button("Pedido de crédito", sys.ask_overdraft),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
finances_menu_state = sys.add_state("Finanças", "Qual operação deseja realizar?", finances_menu_buttons)

# Montagem do menu de informações
info_menu_buttons = [
    Button("Status do Sistema", sys.show_status),
    Button("Dados de uma Pessoa", sys.get_person_data),
    Button("Dados de uma Transação", sys.search_transaction),
    Button("Carregar um SYS", sys.load_data),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
info_menu_state = sys.add_state("Mais", "O que deseja obter?", info_menu_buttons)

# Run the interface
sys.run()
print("\n"*10)