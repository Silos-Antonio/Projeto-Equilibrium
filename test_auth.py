from app.services.auth import verificar_credenciais

def rodar_testes():
    print("--- Iniciando Diagnóstico de Autenticação ---\n")

    # Teste 1 - Credenciais corretas 
    print("Teste 1: Login Válido (Esperado: ID do usuário)")
    id_valido = verificar_credenciais('admin2@equilibrium.com', '123456')
    if id_valido:
        print(f"✅SUCESSO: Acesso liberado. ID retornado: {id_valido}")
    else:
        print("❌ Erro: O usuário correto não foi autenticado.")

    # Teste 2 - Senha errada 
    print("\nTeste 2: Senha incorreta. (Esperado: None)")
    id_senha_errada = verificar_credenciais('admin2@equilibrium.com', 'senha_falsa_123')
    if id_senha_errada is None:
        print("✅Sucesso: Acesso negado corretamente pela senha")
    else:
        print("❌ERRO GRAVE: O sistema aceitou o acesso com senha inválida")

    # Teste 3 - Usuário inexistente
    print("\nTeste 3: E-mail não cadastrado. (Eperado: None)")
    id_email_falso = verificar_credenciais('email@falso.com', '123456')
    if id_email_falso is None:
        print("✅Sucesso: Acesso negado corretamente pelo e-mail.")
    else: 
        print("❌ERRO GRAVE: Acesso concedido com e-mail não cadastrado")

    print("\n--- Fim do diagnóstico ---")

if __name__ == "__main__":
    rodar_testes()
