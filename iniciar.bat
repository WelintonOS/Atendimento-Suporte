@echo off
chcp 65001 >nul
title Sistema de Atendimento HUBGEO

echo.
echo ╔══════════════════════════════════════════╗
echo ║        Sistema de Atendimento HUBGEO     ║
echo ║          30 Anos de Experiência          ║
echo ╚══════════════════════════════════════════╝
echo.

echo 🔍 Verificando Python...

:: Verificar se Python está instalado
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo 💡 Instale o Python em: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

:: Verificar se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PIP não encontrado!
    echo 💡 Reinstale o Python com PIP incluído
    pause
    exit /b 1
)

echo ✅ PIP encontrado

:: Instalar dependências
echo.
echo 📦 Instalando dependências...
py -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências!
    echo 💡 Verifique sua conexão com a internet
    pause
    exit /b 1
)

echo ✅ Dependências instaladas

:: Executar sistema
echo.
echo 🚀 Iniciando sistema...
py run.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao iniciar o sistema!
    echo 💡 Verifique os logs acima para mais detalhes
    pause
    exit /b 1
)

pause