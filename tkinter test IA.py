import tkinter as tk
from idlelib.undo import Command
from struct import pack_into
from tkinter import Variable, Button

import option
from select import select

root = tk.Tk()
root.title("Ejercicio 1")
root.geometry("400x300")

tk.Label(root, text="Ingresa tu nombre").pack(pady=5)
entry_name = tk.Entry(root).pack(pady=5)

tk.Label(root, text="Ingresa tu correo").pack(pady=5)
entry_correo = tk.Entry(root).pack(pady=5)

opcion=tk.StringVar(value="")
rb1= tk.Radiobutton(root, text="Masculino", value="1", variable=opcion).pack()
rb2= tk.Radiobutton(root, text="Femenino", value="2", variable=opcion).pack()
rb3= tk.Radiobutton(root, text="Otro", value="3", variable=opcion).pack()

Button = tk.Button(root, text="Mostrar opcion").pack()


def datosRb():
    print("seleccionaste la opcion ", opcion.get())
    Button(root, text=opcion.get(), command=datosRb).pack()




root.mainloop()