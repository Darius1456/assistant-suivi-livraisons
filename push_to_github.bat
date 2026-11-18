@echo off
chcp 65001 >nul
echo ===================================================================
echo   Assistant de Suivi Prédictif - Publication sur GitHub
echo   Darius Kabore · Master 1 Finance d'Entreprise, INSEEC Paris
echo ===================================================================
echo.

set PATH=C:\Users\kabor\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd;%PATH%

echo Vérification de Git...
git --version
if errorlevel 1 (
    echo Erreur : Git n'est pas détecté.
    pause
    exit /b 1
)

echo.
echo Entrez l'URL de votre dépôt GitHub (ex: https://github.com/votre-nom/votre-repo.git) :
set /p REPO_URL="URL GitHub : "

if "%REPO_URL%"=="" (
    echo Erreur : Aucune URL renseignée.
    pause
    exit /b 1
)

echo.
echo Configuration du dépôt distant origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Envoi des fichiers sur GitHub (branche main)...
git push -u origin main

if errorlevel 0 (
    echo.
    echo ===================================================================
    echo   SUCCÈS : Votre projet est maintenant en ligne sur GitHub !
    echo ===================================================================
) else (
    echo.
    echo Erreur lors du push. Vérifiez vos identifiants GitHub ou vos permissions.
)

pause
