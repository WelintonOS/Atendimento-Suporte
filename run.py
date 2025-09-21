#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Atendimento HUBGEO
Arquivo de inicialização simplificado
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
        print("❌ Dependências não encontradas:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n💡 Para instalar execute:")
        print("   pip install -r requirements.txt")
        return False

    return True

def main():
    """Função principal para iniciar o sistema"""
    print("🚀 Iniciando Sistema de Atendimento HUBGEO...")
    print("=" * 50)

    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)

    # Importar após verificar dependências
    try:
        from app import app, create_tables

        print("✅ Dependências verificadas")
        print("📦 Carregando aplicação...")

        # Inicializar banco de dados
        with app.app_context():
            print("🗄️  Inicializando banco de dados...")
            create_tables()
            print("✅ Banco de dados inicializado!")

        print("\n🎉 Sistema pronto!")
        print("=" * 50)
        print("🌐 URL: http://localhost:5000")
        print("👤 Login: admin@hubgeo.com")
        print("🔑 Senha: admin123")
        print("=" * 50)
        print("📋 Pressione Ctrl+C para parar o servidor")
        print()

        # Iniciar servidor
        app.run(
            debug=True,
            host='127.0.0.1',
            port=5000,
            use_reloader=False  # Evita problemas no Windows
        )

    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Verifique se todos os arquivos estão no local correto")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()