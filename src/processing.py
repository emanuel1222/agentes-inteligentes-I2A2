import ast
import pandas as pd


# ---------- Construção do sind_dict ----------

def construir_sind_dict(agent):
    """Cria o dicionário de sindicatos com dias úteis inicializados."""
    sind_days = agent.invoke('Quantos dias uteis cada sindicato trabalha?')
    print(sind_days)
    tuplas = ast.literal_eval(sind_days["result"])
    return {
        nome: {"dias_uteis": dias, "valor": None}
        for nome, dias in tuplas
    }


def adicionar_estados_ao_sind_dict(sind_dict):
    """Adiciona o estado correspondente ao nome do sindicato no dicionário."""
    estados_brasil = {
        "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
        "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF",
        "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA",
        "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
        "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE",
        "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
        "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
        "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"
    }
    siglas = set(estados_brasil.values())

    for nome, dados in sind_dict.items():
        for sigla in siglas:
            if f" {sigla} " in nome:
                estado = [k for k, v in estados_brasil.items() if v == sigla][0]
                dados["estado"] = estado
                break

    return sind_dict


def preencher_valores_sind_dict(agent, sind_dict):
    """Atualiza o valor do dia de trabalho no sind_dict."""
    day_work_price = agent.invoke('Qual o valor do dia de trabalho para os estados?')
    tuplas = ast.literal_eval(day_work_price["result"])
    tuplas = list(filter(lambda x: x[1] is not None, tuplas))

    for nome, dados in sind_dict.items():
        for estado, valor in tuplas:
            if estado == dados.get('estado'):
                dados["valor"] = valor
                break

    return sind_dict


# ---------- Coleta de Dados Auxiliares ----------

def obter_listas_auxiliares(agent):
    """Busca desligados, estágio, aprendiz, exterior, férias e afastamentos."""
    desligados_result = agent.invoke("Me informe todos os dados dos funcionarios demitidos")
    desligados_raw = ast.literal_eval(desligados_result['result'])
    desligados_dict = {}
    for matricula, data_demissao, comunicado in desligados_raw:
        try:
            dia_demissao = pd.to_datetime(data_demissao).day
            desligados_dict[matricula] = [dia_demissao, comunicado]
        except (ValueError, TypeError):
            print(f"Aviso: Não foi possível processar a data de demissão '{data_demissao}' para a matrícula {matricula}.")

    estagio_list = [item[0] for item in ast.literal_eval(agent.invoke("Selecione todos os dados dos estagiarios")['result'])]
    aprendiz_list = [item[0] for item in ast.literal_eval(agent.invoke("Selecione todos os dados de menor aprendiz")['result'])]
    exterior_list = [item[0] for item in ast.literal_eval(agent.invoke("Selecione todos os dados de funcionarios do exterior")['result'])]
    ferias_result = agent.invoke("Selecione a matricula e os dias de ferias de todos os funcionários de férias")
    ferias_list = ast.literal_eval(ferias_result['result'])
    ferias_dict = {matricula: dias for matricula, dias in ferias_list}
    afastamentos_dict = dict(ast.literal_eval(agent.invoke("SELECT MATRICULA, `Unnamed: 3` FROM AFASTAMENTOS_Planilha1")['result']))
    admitidos_dict = {
        matricula: pd.to_datetime(data_admissao).day
        for matricula, data_admissao in ast.literal_eval(agent.invoke(
            "SELECT MATRICULA, `Admissão` FROM ADMISSÃO_ABRIL_Planilha1 WHERE `Unnamed: 3` NOT LIKE '%não recebe VR'"
        )['result'])
    }

    return {
        "desligados": desligados_dict,
        "estagio": estagio_list,
        "aprendiz": aprendiz_list,
        "exterior": exterior_list,
        "ferias": ferias_dict,
        "afastamentos": afastamentos_dict,
        "admitidos": admitidos_dict
    }


# ---------- Processamento Final ----------

def calcular_vr(agent, sind_dict, listas_auxiliares, competencia="05/2025"):
    """Calcula os valores de VR para cada funcionário ativo."""
    func_ativos_list = ast.literal_eval(agent.invoke('Me mostre todos os dados da tabela de ativos')['result'])
    resultado = []

    matriculas_a_excluir = set(listas_auxiliares["estagio"] + listas_auxiliares["aprendiz"] + listas_auxiliares["exterior"] + list(listas_auxiliares["afastamentos"].keys()))

    for funcionario in func_ativos_list:
        matricula, cod, cargo, status, sindicato = funcionario
        if matricula in matriculas_a_excluir:
            continue

        dias_a_pagar = 0
        if sindicato in sind_dict:
            dados_sindicato = sind_dict[sindicato]
            dias_uteis = dados_sindicato.get("dias_uteis", 0)
            valor_diario = dados_sindicato.get("valor")

            # Regra de desligamento
            if matricula in listas_auxiliares["desligados"]:
                dia_demissao, comunicado = listas_auxiliares["desligados"][matricula]
                if dia_demissao <= 15 and comunicado is not None:
                    continue

            # Regra de admissão
            if matricula in listas_auxiliares["admitidos"]:
                dia_admissao = listas_auxiliares["admitidos"][matricula]
                if dia_admissao > 15:
                    dias_a_pagar = dias_uteis - (dia_admissao - 15)
                else:
                    dias_a_pagar = dias_uteis
            else:
                dias_ferias = listas_auxiliares["ferias"].get(matricula, 0)
                dias_a_pagar = dias_uteis - dias_ferias

            dias_a_pagar = max(0, dias_a_pagar)
            valor_total = dias_a_pagar * valor_diario if valor_diario else 0

            resultado.append({
                "matricula": matricula,
                "Sindicato do Colaborador": sindicato,
                "Competência": competencia,
                "Dias": dias_a_pagar,
                "VALOR DIÁRIO VR": valor_diario,
                "VALOR TOTAL VR": valor_total,
                "OBS GERAL": ""
            })

    return pd.DataFrame(resultado, columns=["matricula", "Sindicato do Colaborador", "Competência", "Dias", "VALOR DIÁRIO VR", "VALOR TOTAL VR", "OBS GERAL"])


def salvar_resultado(df, output_filename="VR MENSAL 05.2025.xlsx"):
    df.to_excel(output_filename, index=False)
    print(f"Resultado salvo em {output_filename}")
