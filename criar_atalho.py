import os
import sys
from pathlib import Path
import win32com.client

def criar_atalho(nome_atalho, caminho_alvo, caminho_icone=None):
    desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
    atalho_path = desktop / f"{nome_atalho}.lnk"

    shell = win32com.client.Dispatch("WScript.Shell")
    atalho = shell.CreateShortCut(str(atalho_path))
    atalho.TargetPath = str(caminho_alvo)
    atalho.WorkingDirectory = str(Path(caminho_alvo).parent)
    if caminho_icone:
        atalho.IconLocation = str(caminho_icone)
    atalho.save()

# Use o caminho real do .exe gerado na pasta "dist"
caminho_exe = Path(__file__).parent / "dist" / "Bot.exe"
caminho_icone = Path(__file__).parent / "icon_download.ico"

criar_atalho("PhantomBuster Downloader", caminho_exe, caminho_icone)
