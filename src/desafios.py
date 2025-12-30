# ESSE ARQUIVO PODE SER ALTERADO PARA GERAR DESAFIOS MELHORES OU QUE SE ADEQUAM MAIS AO USUÁRIO
# ALTERE ESSE ARQUIVO COMO DESEJAR, APAGUE OS DESAFIOS ANTERIORES DO "challenges.json" E RODE O CÓDIGO.

import json
import random

setores = ["Ecommerce", "Fintech", "RH", "Logistica", "HealthTech", "EdTech", 
           "CyberSecurity", "AgroTech", "RealEstate", "LegalTech", "InsurTech", "GovTech"]
entidades = ["Produto", "Transacao", "Colaborador", "Entrega", "Paciente", "Aluno",
             "Contrato", "Imovel", "Apolice", "Insumo", "Ticket", "Processo"]
campos_valor = ["preco", "valor", "salario", "frete", "custo", "nota", "taxa", "comissao"]
status_lista = ["ativo", "pendente", "cancelado", "concluido", "em_analise", "aprovado"]

def gerar_mil_desafios_unicos():
    desafios = []
    assinaturas_vistas = set()

    for i in range(1, 1001):
        tentativas = 0
        desafio_gerado = None
        
        while tentativas < 20:
            setor = random.choice(setores)
            entidade = random.choice(entidades)
            campo = random.choice(campos_valor)
            tipo_logica = random.randint(1, 6)
            
            if tipo_logica == 1: 
                limite = random.choice([100, 500, 1000])
                log_id = f"FILT_{entidade}_{campo}_{limite}"
                desc = f"[{setor}] Filtre {entidade}s onde o '{campo}' multiplicado por 1.1 seja maior que {limite}."
                func = f"filtrar_complexo_{entidade.lower()}_{i}"
                tests = [[f"{func}([{{'{campo}': {limite}}}])", []], [f"{func}([{{'{campo}': {limite+100}}}])", [{campo: limite+100}]]]
                level = "medium"

            elif tipo_logica == 2:
                perc = random.choice([7, 13, 21])
                log_id = f"ADJ_{entidade}_{campo}_{perc}"
                desc = f"[{setor}] Aplique aumento de {perc}% em '{campo}' e retorne o valor arredondado para 2 casas decimais."
                func = f"ajustar_valor_{entidade.lower()}_{i}"
                val = 150.0
                esperado = round(val * (1 + perc/100), 2)
                tests = [[f"{func}({val})", esperado]]
                level = "medium"

            elif tipo_logica == 3:
                log_id = f"FIND_{entidade}_{i}" 
                desc = f"[{setor}] Busque o {entidade} com id 'REF-{i}' e retorne apenas o nome em letras maiúsculas."
                func = f"buscar_nome_{entidade.lower()}_{i}"
                tests = [[f"{func}([{{'id': 'REF-{i}', 'nome': 'alvo'}}, {{'id': '0', 'nome': 'n'}}])", "ALVO"]]
                level = "medium"

            elif tipo_logica == 4: 
                st = random.choice(status_lista)
                log_id = f"COUNT_{entidade}_{st}_{campo}"
                desc = f"[{setor}] Conte quantos {entidade}s possuem status '{st}' E {campo} > 0."
                func = f"contar_especifico_{entidade.lower()}_{i}"
                tests = [[f"{func}([{{'status': '{st}', '{campo}': 10}}, {{'status': 'off', '{campo}': 10}}])", 1]]
                level = "medium"

            elif tipo_logica == 5: 
                prefixo = setor[:2].upper()
                log_id = f"AUTH_{entidade}_{prefixo}"
                desc = f"[{setor}] Valide se o código do {entidade} segue o padrão: '{prefixo}' + 4 números + 'X'."
                func = f"validar_padrao_{entidade.lower()}_{i}"
                tests = [[f"{func}('{prefixo}1234X')", True], [f"{func}('INVALIDO')", False]]
                level = "hard"
            
            else: 
                log_id = f"MEAN_{entidade}_{campo}"
                desc = f"[{setor}] Calcule a média aritmética do campo '{campo}' de uma lista de {entidade}s."
                func = f"calcular_media_{entidade.lower()}_{i}"
                tests = [[f"{func}([{{'{campo}': 10}}, {{'{campo}': 20}}, {{'{campo}': 30}}])", 20.0]]
                level = "medium"

            if log_id not in assinaturas_vistas:
                assinaturas_vistas.add(log_id)
                desafio_gerado = {
                    "id": i,
                    "level": level,
                    "title": f"{setor}: Desafio {entidade}",
                    "description": desc,
                    "function_name": func,
                    "tests": tests
                }
                break
            else:
                tentativas += 1

        if desafio_gerado:
            desafios.append(desafio_gerado)
        else:
            print(f"ALERTA: ID {i} pulado após 20 tentativas de evitar duplicatas.")

    return desafios

if __name__ == "__main__":
    data = gerar_mil_desafios_unicos()
    with open("challenges.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Finalizado: {len(data)} desafios originais gerados em 'challenges.json'.")