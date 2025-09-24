#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para limpar o banco de dados do sistema de atendimento
Remove todos os dados mas mantém a estrutura das tabelas
"""

import pymysql
import sys
from werkzeug.security import generate_password_hash

def limpar_banco():
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
            print("Iniciando limpeza do banco de dados...")

            # Desabilitar verificações de chave estrangeira temporariamente
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Listar todas as tabelas
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()

            # Limpar dados de todas as tabelas
            for (tabela,) in tabelas:
                print(f"   Limpando tabela: {tabela}")
                cursor.execute(f"DELETE FROM {tabela}")

            # Reabilitar verificações de chave estrangeira
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            # Resetar auto_increment das tabelas principais
            tabelas_com_id = [
                'usuarios', 'atendimentos', 'logs_atendimento', 'notificacoes'
            ]

            for tabela in tabelas_com_id:
                cursor.execute(f"ALTER TABLE {tabela} AUTO_INCREMENT = 1")

            connection.commit()
            print("Banco de dados limpo com sucesso!")

            # Recriar usuários padrão
            print("Criando usuarios padrao...")

            # Usuário admin
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, role, ativo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                'Administrador',
                'admin@hubgeo.com',
                generate_password_hash('admin123'),
                'admin',
                True
            ))

            # Usuários de teste
            usuarios_teste = [
                ('João Silva', 'joao@hubgeo.com', 'atendente'),
                ('Maria Santos', 'maria@hubgeo.com', 'atendente'),
                ('Pedro Costa', 'pedro@hubgeo.com', 'atendente'),
                ('Ana Oliveira', 'ana@hubgeo.com', 'atendente')
            ]

            for nome, email, role in usuarios_teste:
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, role, ativo, data_criacao)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    nome,
                    email,
                    generate_password_hash('123456'),
                    role,
                    True
                ))

            connection.commit()
            print("Usuarios padrao criados!")
            print()
            print("Credenciais criadas:")
            print("   Admin: admin@hubgeo.com / admin123")
            print("   Teste: joao@hubgeo.com / 123456")
            print("   Teste: maria@hubgeo.com / 123456")
            print("   Teste: pedro@hubgeo.com / 123456")
            print("   Teste: ana@hubgeo.com / 123456")
            print()
            print("Banco de dados limpo e pronto para uso!")

    except Exception as e:
        print(f"Erro ao limpar banco de dados: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    confirmacao = input("AVISO: Tem certeza que deseja limpar TODOS os dados do banco? (digite 'CONFIRMAR' para prosseguir): ")
    if confirmacao == 'CONFIRMAR':
        limpar_banco()
    else:
        print("Operacao cancelada.")