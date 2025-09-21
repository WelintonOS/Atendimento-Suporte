#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Atendimento HUBGEO
Arquivo de inicialização simplificado (sem emojis)
"""

import sys
import os

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'pymysql',
        'werkzeug'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("ERRO: Dependencias nao encontradas:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nPara instalar execute:")
        print("   py -m pip install -r requirements.txt")
        return False

    return True

def main():
    """Função principal para iniciar o sistema"""
    print("Iniciando Sistema de Atendimento HUBGEO...")
    print("=" * 50)

    # Verificar dependências
    if not check_dependencies():
        input("Pressione Enter para sair...")
        sys.exit(1)

    # Importar após verificar dependências
    try:
        from app import app, create_tables

        print("Dependencias verificadas")
        print("Carregando aplicacao...")

        # Inicializar banco de dados
        with app.app_context():
            print("Inicializando banco de dados...")
            create_tables()
            print("Banco de dados inicializado!")

        print("\nSistema pronto!")
        print("=" * 50)
        print("URL: http://localhost:5000")
        print("Login: admin@hubgeo.com")
        print("Senha: admin123")
        print("=" * 50)
        print("Pressione Ctrl+C para parar o servidor")
        print()

        # Iniciar servidor
        app.run(
            debug=True,
            host='127.0.0.1',
            port=5000,
            use_reloader=False  # Evita problemas no Windows
        )

    except ImportError as e:
        print(f"ERRO ao importar modulos: {e}")
        print("Verifique se todos os arquivos estao no local correto")
        input("Pressione Enter para sair...")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)

if __name__ == '__main__':
    main()