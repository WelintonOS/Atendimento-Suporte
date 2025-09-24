#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para importar atendimentos do arquivo CSV para o banco de dados
"""

import pymysql
import csv
import sys
from datetime import datetime

def mapear_forma_contato(tipo_atendimento):
    """Mapear tipos do CSV para formas de contato do sistema"""
    mapeamento = {
        'Whatsapp': 'WhatsApp',
        'WhatsApp': 'WhatsApp',
        'Presencial': 'Presencial',
        'Virtual': 'Email'
    }
    return mapeamento.get(tipo_atendimento, 'WhatsApp')

def mapear_produto(produto_csv):
    """Mapear produtos do CSV para categorias do sistema"""
    produto_lower = produto_csv.lower()

    # Mapeamento de produtos
    if 'emlid' in produto_lower or 'rs3' in produto_lower:
        return 'GNSS'
    elif 'posição' in produto_lower or 'posicao' in produto_lower:
        return 'Software'
    elif 'geomate' in produto_lower:
        return 'Software'
    elif 'leica' in produto_lower or 'tc307' in produto_lower:
        return 'Estação Total'
    elif 'x-pad' in produto_lower:
        return 'Software'
    else:
        return 'Outros'

def mapear_marca(produto_csv):
    """Extrair marca do produto"""
    produto_lower = produto_csv.lower()

    if 'emlid' in produto_lower:
        return 'Emlid'
    elif 'leica' in produto_lower:
        return 'Leica'
    elif 'chcnav' in produto_lower or 'chc' in produto_lower:
        return 'CHCNAV'
    else:
        return None

def converter_data(data_str):
    """Converter data do formato DD/MM/YYYY para datetime"""
    try:
        return datetime.strptime(data_str, '%d/%m/%Y')
    except:
        return datetime.now()

def importar_csv():
    try:
        # Conectar ao banco
        connection = pymysql.connect(
            host='ballast.proxy.rlwy.net',
            port=20008,
            user='root',
            password='sIuTpZxKilayoTVOrFDnkOOqhYjAeoCe',
            database='railway',
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # Buscar ID do usuário Welinton Oliveira Silva
            cursor.execute("SELECT id FROM usuarios WHERE nome LIKE %s", ('%Welinton%',))
            usuario = cursor.fetchone()

            if not usuario:
                print("Usuário Welinton não encontrado. Criando usuário...")
                # Se não existir, criar o usuário
                from werkzeug.security import generate_password_hash
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, role, ativo, data_criacao)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    'Welinton Oliveira Silva',
                    'welinton@hubgeo.com',
                    generate_password_hash('123456'),
                    'admin',
                    True
                ))
                connection.commit()
                usuario_id = cursor.lastrowid
            else:
                usuario_id = usuario[0]

            print(f"Importando atendimentos para usuário ID: {usuario_id}")

            # Ler arquivo CSV
            csv_file = r"C:\Users\welin\OneDrive\Área de Trabalho\Welinton-Atividades.csv"

            atendimentos_importados = 0

            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file, delimiter=';')

                for linha in csv_reader:
                    # Pular linhas vazias
                    if not linha['Cliente '] or linha['Cliente '].strip() == '':
                        continue

                    cliente_nome = linha['Cliente '].strip()
                    tipo_atendimento = linha['Tipo de Atendimento'].strip()
                    contato = linha['Contato'].strip() if linha['Contato'].strip() != 'N/C' else None
                    produto_csv = linha['Produto'].strip()
                    data_str = linha['Data'].strip()
                    problema = linha['Problema'].strip()
                    solucao = linha['Solução'].strip()

                    # Mapear dados
                    forma_contato = mapear_forma_contato(tipo_atendimento)
                    produto = mapear_produto(produto_csv)
                    marca = mapear_marca(produto_csv)
                    data_inicio = converter_data(data_str)

                    # Status baseado na solução
                    status = 'concluido' if solucao == 'SIM' else 'cancelado'

                    # Inserir atendimento
                    cursor.execute("""
                        INSERT INTO atendimentos
                        (cliente_nome, cliente_contato, forma_contato, produto, marca, problema,
                         usuario_id, data_inicio, data_fim, status, observacoes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        cliente_nome,
                        contato,
                        forma_contato,
                        produto,
                        marca,
                        problema,
                        usuario_id,
                        data_inicio,
                        data_inicio if status == 'concluido' else None,  # data_fim igual a data_inicio se concluído
                        status,
                        f"Importado do CSV - Solução: {solucao}" if solucao else None
                    ))

                    atendimentos_importados += 1
                    print(f"   Importado: {cliente_nome} - {produto} - {data_str}")

            connection.commit()
            print(f"\nImportacao concluida!")
            print(f"   Total de atendimentos importados: {atendimentos_importados}")
            print(f"   Responsavel: Welinton Oliveira Silva (ID: {usuario_id})")

    except Exception as e:
        print(f"Erro ao importar CSV: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    confirmacao = input("Confirma a importação dos atendimentos do CSV? (digite 'SIM' para prosseguir): ")
    if confirmacao == 'SIM':
        importar_csv()
    else:
        print("Importação cancelada.")