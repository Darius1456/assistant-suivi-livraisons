@echo off
chcp 65001 >nul
echo ===================================================================
echo   Assistant de Suivi Prédictif - Publication Automatique GitHub
echo   Darius Kabore · Master 1 Finance d'Entreprise, INSEEC Paris
echo ===================================================================
echo.

set PATH=C:\Users\kabor\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin;C:\Users\kabor\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd;%PATH%

echo [1/3] Vérification de l'authentification GitHub...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo.
    echo Vous n'êtes pas encore connecté à GitHub sur cette machine.
    echo Une page va s'ouvrir dans votre navigateur pour autoriser la connexion en 1 clic.
    echo.
    gh auth login --web -h github.com -p https -w
    if errorlevel 1 (
        echo Erreur de connexion GitHub.
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Authentification GitHub validée !
echo.

set REPO_NAME=assistant-suivi-livraisons
echo [3/3] Création automatique du dépôt distant '%REPO_NAME%' et envoi des fichiers...
gh repo create %REPO_NAME% --public --source=. --remote=origin --push

if errorlevel 0 (
    echo.
    echo ===================================================================
    echo   SUCCÈS TOTAL : Votre projet est en ligne sur GitHub !
    echo ===================================================================
    echo Vous pouvez le consulter directement sur votre compte GitHub.
) else (
    echo.
    echo Note : Si le dépôt existait déjà, tentative de push direct...
    git push -u origin main
)

echo.
pause
