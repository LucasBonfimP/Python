import yfinance as yf
import time
import threading
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import winsound  # para Windows
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import pygame  # para outros sistemas operacionais

class MonitorAcoes:
    def __init__(self, root):
        self.root = root
        self.configurar_gui()

    def configurar_gui(self):
        self.root.title("Monitor de Ações B3")
        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Código da Ação:").grid(column=1, row=1, sticky=W)
        self.acao_entry = ttk.Entry(mainframe, width=15)
        self.acao_entry.grid(column=2, row=1, sticky=(W, E))

        ttk.Label(mainframe, text="Variação para Alerta (%):").grid(column=1, row=2, sticky=W)
        self.variacao_entry = ttk.Entry(mainframe, width=15)
        self.variacao_entry.grid(column=2, row=2, sticky=(W, E))

        self.start_button = ttk.Button(mainframe, text="Iniciar Monitoramento", command=self.iniciar_monitoramento)
        self.start_button.grid(column=2, row=3, sticky=W)

        self.log = Text(mainframe, width=50, height=10)
        self.log.grid(column=1, row=4, columnspan=2, sticky=(W, E))
        log_scrollbar = ttk.Scrollbar(mainframe, command=self.log.yview)
        log_scrollbar.grid(column=3, row=4, sticky=(N, S, W))
        self.log['yscrollcommand'] = log_scrollbar.set

        # Inicialização do gráfico
        self.figura, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figura, master=mainframe)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(column=1, row=5, columnspan=2, sticky=(W, E))

    def iniciar_monitoramento(self):
        acao = self.acao_entry.get()
        variacao = float(self.variacao_entry.get())
        threading.Thread(target=self.monitorar_acao, args=(acao, variacao), daemon=True).start()
        threading.Thread(target=self.atualizar_grafico, args=(acao,), daemon=True).start()
        self.start_button['state'] = 'disabled'

    def tocar_som_alerta(self):
        # Para Windows
        winsound.Beep(1000, 1000)  # frequência 1000 Hz, duração 1000 ms

    def mostrar_alerta_popup(self, mensagem):
        messagebox.showwarning("Alerta de Ação", mensagem)

    def atualizar_grafico(self, ticker):
        while True:
            dados = yf.download(ticker, period="7d", interval="1d")
            self.ax.clear()
            self.ax.plot(dados.index, dados['Close'])
            self.ax.set_title(f'Preço de Fechamento dos Últimos 7 Dias: {ticker}')
            self.ax.set_xlabel('Data')
            self.ax.set_ylabel('Preço de Fechamento')
            self.ax.tick_params(axis='x', rotation=45)
            self.canvas.draw()
            time.sleep(60 * 60)  # Atualiza o gráfico a cada hora

    def monitorar_acao(self, ticker, variacao_alerta):
        preco_inicial = None
        while True:
            try:
                dados = yf.download(ticker, period="1d", interval="1m")
                preco_atual = dados['Close'][-1]
                if preco_inicial is None:
                    preco_inicial = preco_atual

                variacao_percentual = ((preco_atual - preco_inicial) / preco_inicial) * 100

                self.log.insert(END, f"{datetime.now()}: {ticker} - Preço: {preco_atual:.2f}, Variação: {variacao_percentual:.2f}%\n")
                self.log.see(END)

                if abs(variacao_percentual) >= variacao_alerta:
                    mensagem = f"Alerta: Variação de {variacao_percentual:.2f}% para a ação {ticker}"
                    self.root.after(0, self.mostrar_alerta_popup, mensagem)
                    self.root.after(0, self.tocar_som_alerta)
                
                time.sleep(60)
            except Exception as e:
                self.log.insert(END, f"Erro: {e}\\n")
                self.log.see(END)
                time.sleep(60)

if __name__ == "__main__":
    root = Tk()
    app = MonitorAcoes(root)
    root.mainloop()
