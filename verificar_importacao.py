#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar a importação e criar usuário Welinton se necessário
"""

import pymysql
import sys
from werkzeug.security import generate_password_hash

def verificar_importacao():
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
            # Verificar se usuário Welinton existe
            cursor.execute("SELECT id, nome FROM usuarios WHERE nome LIKE %s", ('%Welinton%',))
            usuario = cursor.fetchone()

            if not usuario:
                print("Criando usuario Welinton Oliveira Silva...")
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
                print(f"Usuario criado com ID: {usuario_id}")
            else:
                usuario_id = usuario[0]
                print(f"Usuario encontrado: {usuario[1]} (ID: {usuario_id})")

            # Verificar atendimentos importados
            cursor.execute("SELECT COUNT(*) FROM atendimentos WHERE usuario_id = %s", (usuario_id,))
            total_atendimentos = cursor.fetchone()[0]

            print(f"Total de atendimentos do Welinton: {total_atendimentos}")

            # Listar alguns atendimentos
            cursor.execute("""
                SELECT id, cliente_nome, produto, data_inicio, status
                FROM atendimentos
                WHERE usuario_id = %s
                ORDER BY data_inicio DESC
                LIMIT 5
            """, (usuario_id,))

            atendimentos = cursor.fetchall()

            if atendimentos:
                print("\nUltimos 5 atendimentos importados:")
                for at in atendimentos:
                    print(f"  #{at[0]} - {at[1]} - {at[2]} - {at[3]} - {at[4]}")
            else:
                print("Nenhum atendimento encontrado")

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    verificar_importacao()