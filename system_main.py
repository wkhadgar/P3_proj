from interface import *
import SUB as sub

root = tk.Tk()
root.geometry("500x300")
style = ttk.Style(root)
style.theme_use("clam")  # ou "alt", "default", e "classic"

sys = sub.System(root)

# Montagem do menu principal
main_menu_buttons = [
    Button("Cadastro", lambda: signup_menu_state.show_state()),
    Button("Remoção", lambda: remove_menu_state.show_state()),
    Button("Financeiro", lambda: finances_menu_state.show_state()),
    Button("Informações", lambda: info_menu_state.show_state()),
    Button("Encerrar", lambda: root.destroy()),
]
main_menu_state = sys.add_state("SUB", "Bem vindo ao SUB - Sistema Único de Bancos. O que deseja fazer?",
                                main_menu_buttons)

# Montagem do menu de cadastro
signup_menu_buttons = [
    Button("Cadastro de Pessoa", lambda: sys.create_person()),  # TODO completar com os callbacks corretos
    Button("Cadastro de Banco", lambda: sys.create_bank()),
    Button("Criar conta em banco para pessoa", lambda: sys.sys_open_account()),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
signup_menu_state = sys.add_state("Cadastro", "Qual cadastro deseja realizar?", signup_menu_buttons)

# Montagem do menu de remoção
remove_menu_buttons = [
    Button("Remoção de Pessoa", lambda: print("RemPes")),
    Button("Remoção de Banco", lambda: print("RemBan")),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
remove_menu_state = sys.add_state("Remoção", "Qual remoção deseja realizar?", remove_menu_buttons)

# Montagem do menu de finanças
finances_menu_buttons = [
    Button("Depósito", lambda: print("Dep")),
    Button("Saque", lambda: print("Saq")),
    Button("Transferência", (lambda: sys.make_transfer())),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
finances_menu_state = sys.add_state("Finanças", "Qual operação deseja realizar?", finances_menu_buttons)

# Montagem do menu de informações
info_menu_buttons = [
    Button("Status do Sistema", lambda: print("Sta")),
    Button("Dados de uma Pesssoa", lambda: print("Dad")),
    Button("Voltar ao menu principal.", lambda: main_menu_state.show_state()),
]
info_menu_state = sys.add_state("Informações", "O que deseja obter?", info_menu_buttons)

# Run the interface
sys.run()
print("\n\n\n\n\n")

run = True
# while run:

# if ifc_handle.current_screen == 'main_menu':s
#     print("\n\n\nBem-vindo ao SUB, o que deseja fazer?")
#     print("[0] - Encerrar.")
#     print("[1] - Cadastro.")
#     print("[2] - Remoção.")
#     print("[3] - Financeiro.")
#     print("[4] - Informações.")
#
#     option = int(input("-> "))
#     if option == 0:
#         run = False
#         break
#     elif option == 1:
#         ifc_handle.current_screen = 'sign_menu'
#     elif option == 2:
#         ifc_handle.current_screen = 'delete_menu'
#     elif option == 3:
#         ifc_handle.current_screen = 'transactions_menu'
#     elif option == 4:
#         ifc_handle.current_screen = 'info_menu'
#
# elif ifc_handle.current_screen == 'sign_menu':
#     print()
#     print("[1] - Cadastrar nova pessoa.")
#     print("[2] - Cadastrar novo banco.")
#     print("[3] - Criar conta em banco para pessoa cadastrada.")
#     print("[4] - Voltar.")
#
#     option = int(input("-> "))
#
#     if option == 1:
#         name = input("Digite o nome da pessoa: ")
#         cpf = int(input("Digite o CPF dessa pessoa: "))
#         sys.create_person(name=name, cpf=cpf)
#
#     elif option == 2:
#         bank = input("Digite o nome do banco a ser criado: ").strip()
#         fee = float(int(input("Qual a taxa de transferência externa desse banco, em %: ")) / 100)
#
#         sys.create_bank(name=bank, bank_fee=fee)
#
#     elif option == 3:
#         cpf = int(input("Digite o CPF da pessoa que abrirá a conta: "))
#         bank = input("Digite o nome do banco onde a conta será criada: ").strip()
#         sys.sys_open_account(cpf, bank)
#
#     elif option == 4:
#         ifc_handle.current_screen = 'main_menu'
#
# elif ifc_handle.current_screen == 'delete_menu':
#     print()
#     print("[1] - Remover pessoa existente.")
#     print("[2] - Remover banco existente.")
#     print("[3] - Voltar.")
#
#     option = int(input("-> "))
#
#     if option == 1:
#         cpf = int(input("Digite o CPF dessa pessoa: "))
#         sys.remove_person(cpf)
#
#     elif option == 2:
#         bank = input("Digite o nome do banco a ser removido: ").strip()
#         sys.remove_bank(name=bank)
#
#     elif option == 3:
#         ifc_handle.current_screen = 'main_menu'
#
# elif ifc_handle.current_screen == 'transactions_menu':
#     print()
#     print("[1] - Realizar depósito em conta.")
#     print("[2] - Realizar saque de conta.")
#     print("[3] - Realizar transferência automatizada entre pessoas.")
#     print("[4] - Voltar.")
#
#     option = int(input("-> "))
#
#     if option == 1:
#         cpf = int(input("Digite o CPF dessa pessoa: "))
#         bank = input("Digite o banco no qual deve ser feito o depósito:").strip()
#         sys.make_deposit(cpf=cpf, bank=bank,
#                          value=float(input(f"Qual valor que será depositado na conta?\n"
#                                            f"-> R$ ")))
#     elif option == 2:
#         cpf = int(input("Digite o CPF dessa pessoa: "))
#         bank = input("Digite o banco no qual deve ser feito o saque:").strip()
#         do_limit = True if input("O saque deve ser limitado?\n"
#                                  "[s] - Sim\n"
#                                  "[n] - Não\n"
#                                  "-> ") == 's' else False
#         sys.make_draw(cpf=cpf, bank=bank,
#                       value=float(input(f"Qual valor que será reitrado da conta?\n"
#                                         f"-> R$ ")), has_time_limit=do_limit)
#     elif option == 3:
#         giver_cpf = int(input("Digite o cpf da pessoa que vai realizar a transferencia: "))
#         giver_bank = input("Digite o banco no qual deve ser feito o saque:").strip()
#
#         receiver_cpf = int(input("Digite o cpf da pessoa que vai receber a transferencia: "))
#         receiver_bank = input("Digite o banco no qual deve ser feito o depósito:").strip()
#
#         do_limit = True if input("A transferência deve ser limitada?\n"
#                                  "[s] - Sim\n"
#                                  "[n] - Não\n"
#                                  "-> ") == 's' else False
#
#         sys.make_transfer(
#                 value=float(input(f"Qual valor que será transferido?\n"
#                                   f"-> R$ ")),
#                 origin_id=giver_cpf, origin_bank=giver_bank, target_id=receiver_cpf, target_bank=receiver_bank,
#                 is_time_limited=do_limit)
#
#     elif option == 4:
#         ifc_handle.current_screen = 'main_menu'
#
# elif ifc_handle.current_screen == 'info_menu':
#     print()
#     print("[1] - Mostrar status do sistema.")
#     print("[2] - Mostrar dados de uma pessoa.")
#     print("[3] - Voltar.")
#
#     option = int(input("-> "))
#
#     if option == 1:
#         sys.show_status()
#     elif option == 2:
#         cpf = int(input("Digite o CPF dessa pessoa: "))
#         sys.get_person_data(cpf)
#     elif option == 3:
#         ifc_handle.current_screen = 'main_menu'