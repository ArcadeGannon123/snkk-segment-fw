import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.func_image_processing import cargar_icono

class GraphWindow:
    def __init__(self, master,data):
        self.master = master
        self.master.title("Gráficos")
        self.master.geometry("1280x720")
        self.master.configure(bg="#2b2b2b")
        self.icono_app = cargar_icono("./icons/conexiones.png")
        self.master.iconphoto(False, self.icono_app)

        self.figura = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figura.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figura, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        self.selector_frame = tk.Frame(self.master, bg="#2b2b2b")
        self.selector_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.label = tk.Label(self.selector_frame, text="Seleccionar gráfico:", bg="#2b2b2b", fg="white")
        self.label.pack(pady=10)
        
        self.graficos = data
        self.lista_graficos = tk.Listbox(self.selector_frame, bg="#3c3c3c", fg="white", selectbackground="#5e5e5e")
        for grafico in self.graficos.keys():
            if grafico != "Timeline":
                self.lista_graficos.insert(tk.END, grafico)
        self.lista_graficos.pack(pady=10,padx=10)
        self.lista_graficos.bind("<<ListboxSelect>>", self.mostrar_grafico)

        # Seleccionar automáticamente el primer ítem (o el que desees) y disparar el evento
        self.lista_graficos.select_set(0)  # Selecciona el primer ítem (índice 0)
        self.lista_graficos.event_generate("<<ListboxSelect>>")  # Genera el evento de selección automáticamente
        
        self.cerrar_boton = tk.Button(self.selector_frame, text="Cerrar", command=self.master.destroy, bg="#4c4c4c", fg="white")
        self.cerrar_boton.pack(pady=20)

    def mostrar_grafico(self, event):
        seleccion = self.lista_graficos.curselection()
        if seleccion:
            grafico_seleccionado = list(self.graficos.keys())[seleccion[0]]
            self.ax.clear()
            
            x = self.graficos["Timeline"]
            y = self.graficos[grafico_seleccionado][0]
            
            self.ax.fill_between(x, y, color="skyblue", alpha=0.5)
            self.ax.plot(x, y, color="Slateblue", alpha=0.6)
            self.ax.set_title(f'Gráfico de {grafico_seleccionado}')
            self.ax.grid(True)
            self.ax.set_xlabel(self.graficos[grafico_seleccionado][1][0])
            self.ax.set_ylabel(self.graficos[grafico_seleccionado][1][1])

            self.mostrar_valores(x, y)
            
            self.canvas.draw()

    def mostrar_valores(self, x, y):
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                                  bbox=dict(boxstyle="round", fc="w"),
                                  arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        self.figura.canvas.mpl_connect("motion_notify_event", self.actualizar_anotacion)

    def actualizar_anotacion(self, event):
        if not event.inaxes:
            return
        
        x, y = event.xdata, event.ydata
        self.annot.xy = (x, y)
        texto = f'x={x:.2f}, y={y:.2f}'
        self.annot.set_text(texto)
        self.annot.set_visible(True)
        self.figura.canvas.draw()
        
        
