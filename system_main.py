import SUB as sub
from interface import tk, ttk, Button

root = tk.Tk()
root.geometry("500x310")
root.iconbitmap(default=r"assets/SUB_ico.ico")
root.wm_title("Sistema Único de Bancos")
style = ttk.Style(root)
style.theme_use("clam")  # ou "alt", "default", e "classic"

sys = sub.System(root)

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
    Button("Cadastro de Pessoa", sys.screen_create_person),
    Button("Cadastro de Banco", sys.screen_create_bank),
    Button("Criar conta em banco para pessoa", sys.screen_open_account),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
signup_menu_state = sys.add_state("Cadastro", "Qual cadastro deseja realizar?", signup_menu_buttons)

# Montagem do menu de remoção
remove_menu_buttons = [
    Button("Remoção de Pessoa", sys.screen_remove_person),
    Button("Remoção de Banco", sys.screen_remove_bank),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
remove_menu_state = sys.add_state("Remoção", "Qual remoção deseja realizar?", remove_menu_buttons)

# Montagem do menu de finanças
finances_menu_buttons = [
    Button("Depósito", sys.screen_make_deposit),
    Button("Saque", sys.screen_make_draw),
    Button("Transferência", sys.screen_make_transfer),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
finances_menu_state = sys.add_state("Finanças", "Qual operação deseja realizar?", finances_menu_buttons)

# Montagem do menu de informações
info_menu_buttons = [
    Button("Status do Sistema", sys.screen_show_status),
    Button("Dados de uma Pesssoa", sys.screen_get_person_data),
    Button("Dados de uma Transação", sys.screen_search_transaction),
    Button("Carregar um SYS", sys.screen_load_data),
    Button("Voltar ao menu principal.", main_menu_state.show_state),
]
info_menu_state = sys.add_state("Mais", "O que deseja obter?", info_menu_buttons)

# Run the interface
sys.run()
print("\n\n\n\n\n")

# Test IDs
# 901190711
# 916406097