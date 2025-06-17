import tkinter as tk
from tkinter import scrolledtext, messagebox
from db_agent import criar_agente
import os

class ChatApp:
    def __init__(self, root, db_path):
        self.root = root
        self.root.title("Assistente IA de Dados")
        self.root.geometry("600x500")

        self.db_path = db_path

        try:
            self.agente = criar_agente(self.db_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar com o banco: {e}")
            self.root.destroy()

        # Caixa de chat (exibição)
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Arial", 11))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Caixa de entrada (pergunta)
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry.bind("<Return>", self.enviar_pergunta)

        # Botão enviar
        self.send_button = tk.Button(root, text="Enviar", command=self.enviar_pergunta)
        self.send_button.pack(padx=10, pady=(0, 10))

    def enviar_pergunta(self, event=None):
        pergunta = self.entry.get().strip()
        if not pergunta:
            return

        self.exibir_mensagem("Você", pergunta)
        self.entry.delete(0, tk.END)

        try:
            resposta = self.agente.invoke(pergunta)
            self.exibir_mensagem("IA", resposta.get('result'))
        except Exception as e:
            self.exibir_mensagem("Erro", str(e))

    def exibir_mensagem(self, remetente, mensagem):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{remetente}: {mensagem}\n\n")
        self.chat_display.yview(tk.END)
        self.chat_display.config(state='disabled')


if __name__ == "__main__":
    db_path = "sqlite/i2a2.db"
    if not os.path.exists(db_path):
        tk.messagebox.showerror("Erro", f"Banco de dados não encontrado em {db_path}. Execute 'main.py' primeiro.")
        exit()

    root = tk.Tk()
    app = ChatApp(root, db_path)
    root.mainloop()
