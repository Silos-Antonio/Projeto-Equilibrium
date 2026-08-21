from app.services.paciente_service import criar_paciente, listar_pacientes_do_terapeuta
from app.services.auth import verificar_credenciais

def rodar_teste_pacientes():
    print("--- Iniciando Diagnóstico de Pacientes (Modelo Relacional) ---")
    
    # 1. Autenticação para pegar o ID
    terapeuta_id = verificar_credenciais('admin@equilibrium.com', '123456')
    if not terapeuta_id:
        print("❌ ERRO: Terapeuta admin não encontrado.")
        return

    print(f"✅ Terapeuta identificado com ID: {terapeuta_id}")

    # 2. Testando a dupla inserção (Paciente + Vínculo)
    print("\n--- Testando Criação e Vínculo de Paciente ---")
    sucesso = criar_paciente(
        terapeuta_id=terapeuta_id, 
        nome="Ana Clara (Teste Relacional)", 
        email="ana@teste.com",
        telefone="11988887777",
        observacoes="Paciente de teste para validar chaves."
    )
    
    if sucesso:
        print("✅ SUCESSO: Paciente inserido E vinculado com sucesso!")
    else:
        print("❌ ERRO: Falha ao executar a transação de criação.")

    # 3. Validando a busca com INNER JOIN
    print("\n--- Testando Listagem (INNER JOIN) ---")
    pacientes = listar_pacientes_do_terapeuta(terapeuta_id)
    
    if pacientes:
        print(f"✅ SUCESSO: Encontrados {len(pacientes)} paciente(s) vinculado(s):")
        for p in pacientes:
            print(f"   -> ID: {p['id']} | {p['nome']} | Tel: {p['telefone']} | Obs: {p['observacoes']}")
    else:
        print("❌ ERRO: Nenhum paciente encontrado após o cruzamento de dados.")

if __name__ == "__main__":
    rodar_teste_pacientes()