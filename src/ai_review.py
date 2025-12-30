from google import genai

# Opção A: Pega do sistema (Recomendado)
api_key = os.getenv("GEMINI_API_KEY") 

# Opção B: Se quiser que a pessoa escreva direto no código (Menos seguro, mas simples)
# api_key = "COLOQUE_SUA_CHAVE_AQUI"

client = genai.Client(api_key=api_key)

def ai_review(code, challenge):
    """
    Avalia o código do usuário usando Gemini 2.5
    Retorna feedback curto e direto da IA.
    """
    prompt = f"""
Você é um professor experiente de Python.
Analise este código do aluno com base em:
- Correção
- Clareza
- Boas práticas
- Eficiência

Desafio: {challenge['description']}

Código do aluno:
{code}

Fale brevemente se o aluno passou no teste ou não, se ele tiver passado, coloque um ✅ no começo da mensagem, caso o contrário coloque um ❌;
Dê um feedback objetivo e curto (3 linhas no máximo).
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
