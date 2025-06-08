import customtkinter as ctk
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image
import sys
import os


# ----- Função principal -----
def baixar_dados():
    api_key = entry_api.get()
    phantom_id = entry_phantom.get()

    if not api_key or not phantom_id:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
        return

    url = f'https://api.phantombuster.com/api/v2/agents/fetch?id={phantom_id}'
    headers = {
        'Content-Type': 'application/json',
        'x-phantombuster-key': api_key,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        org_folder = data.get('orgS3Folder')
        s3_folder = data.get('s3Folder')

        if not org_folder or not s3_folder:
            messagebox.showerror("Erro", "Não foi possível encontrar os diretórios.")
            return

        csv_url = f"https://phantombuster.s3.amazonaws.com/{org_folder}/{s3_folder}/result.csv"
        csv_response = requests.get(csv_url)
        csv_response.raise_for_status()

        df = pd.read_csv(StringIO(csv_response.content.decode('utf-8')))
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"resultado_{timestamp}.xlsx"
        )

        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

# ----- Configuração do Tema -----
ctk.set_appearance_mode("system")  # ou "dark", "light"
ctk.set_default_color_theme("blue")

# ----- Interface Gráfica -----
app = ctk.CTk()
app.title("📥 PhantomBuster Downloader")
app.geometry("500x400")
app.resizable(False, False)

ctk.set_appearance_mode("dark")


# Função que garante o caminho certo no .exe e no .py
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller usa isso no modo --onefile
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Caminho da imagem de ícone
icon_path = resource_path("icon_download.ico")
img = Image.open(icon_path)

#Titulo
label_titulo = ctk.CTkLabel(app, text="PhantomBuster Downloader", font=("Poppins", 20, "bold"))
label_titulo.pack(pady=(50, 40))


entry_api = ctk.CTkEntry(app, placeholder_text="API Key", show="*", width=300)
entry_api.pack(pady=10)

entry_phantom = ctk.CTkEntry(app, placeholder_text="Phantom ID", width=300)
entry_phantom.pack(pady=10)

btn_baixar = ctk.CTkButton(
    app, text="Baixar Dados", corner_radius=32,
    fg_color='#4158D0', hover_color="#DFB25D",
    border_color='#FFCC70', border_width=2,
    image=ctk.CTkImage(dark_image=img),
    command=baixar_dados, width=200
)



btn_baixar.pack(pady=(30, 10))

app.mainloop()
