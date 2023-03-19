from interface import *
import SUB as sub

root = tk.Tk()
root.geometry("500x300")
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
    Button("Encerrar", lambda: root.destroy()),
]
main_menu_state = sys.add_state("SUB", "Bem vindo ao SUB - Sistema Único de Bancos. O que deseja fazer?",
                                main_menu_buttons)

# Montagem do menu de cadastro
signup_menu_buttons = [
    Button("Cadastro de Pessoa", lambda: sys.screen_create_person()),
    Button("Cadastro de Banco", lambda: sys.screen_create_bank()),
    Button("Criar conta em banco para pessoa", lambda: sys.screen_open_account()),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
signup_menu_state = sys.add_state("Cadastro", "Qual cadastro deseja realizar?", signup_menu_buttons)

# Montagem do menu de remoção
remove_menu_buttons = [
    Button("Remoção de Pessoa", lambda: sys.screen_remove_person()),
    Button("Remoção de Banco", lambda: sys.screen_remove_bank()),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
remove_menu_state = sys.add_state("Remoção", "Qual remoção deseja realizar?", remove_menu_buttons)

# Montagem do menu de finanças
finances_menu_buttons = [
    Button("Depósito", lambda: sys.screen_make_deposit()),
    Button("Saque", lambda: sys.screen_make_draw()),
    Button("Transferência", (lambda: sys.screen_make_transfer())),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
finances_menu_state = sys.add_state("Finanças", "Qual operação deseja realizar?", finances_menu_buttons)

# Montagem do menu de informações
info_menu_buttons = [
    Button("Status do Sistema", lambda: sys.screen_show_status()),
    Button("Dados de uma Pesssoa", lambda: sys.screen_get_person_data()),
    Button("Carregar um SYS", lambda: sys.screen_load_data()),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
info_menu_state = sys.add_state("Mais", "O que deseja obter?", info_menu_buttons)

# Run the interface
sys.run()
print("\n\n\n\n\n")