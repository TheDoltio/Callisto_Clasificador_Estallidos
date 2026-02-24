import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import sys

BASE_URL = "https://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto"
ESTACIONES = [
    "LANCE",
    "FCFM-UNACH",
    "UANL-INFIERNILLO",
    "ENSENADA-UNAM",
    "FCFM-UANL"
]


def guardar_fechas():
    try:
        fecha_ini = datetime(
            int(entry_ini_year.get()),
            int(entry_ini_month.get()),
            int(entry_ini_day.get())
        )

        fecha_fin = datetime(
            int(entry_fin_year.get()),
            int(entry_fin_month.get()),
            int(entry_fin_day.get())
        )

        if fecha_ini > fecha_fin:
            messagebox.showerror("Error", "La fecha inicial no puede ser mayor que la final.")
            return

        delta = fecha_fin - fecha_ini

        with open("wget_list.txt", "w") as f:
            for i in range(delta.days + 1):
                fecha = fecha_ini + timedelta(days=i)

                url = f"{BASE_URL}/{fecha.strftime('%Y/%m/%d')}/"
                f.write(url + "\n")

        root.destroy()
        sys.exit(0)

    except ValueError:
        messagebox.showerror("Error", "Fecha inválida. Verifica los valores ingresados.")

root = tk.Tk()
root.title("Selector de Rango de Fechas")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(root, text="Fecha Inicial (YYYY MM DD)").pack(pady=5)

frame_ini = tk.Frame(root)
frame_ini.pack()

entry_ini_year = tk.Entry(frame_ini, width=6)
entry_ini_year.pack(side="left", padx=2)
entry_ini_year.insert(0, "2026")

entry_ini_month = tk.Entry(frame_ini, width=4)
entry_ini_month.pack(side="left", padx=2)
entry_ini_month.insert(0, "01")

entry_ini_day = tk.Entry(frame_ini, width=4)
entry_ini_day.pack(side="left", padx=2)
entry_ini_day.insert(0, "01")

tk.Label(root, text="Fecha Final (YYYY MM DD)").pack(pady=10)

frame_fin = tk.Frame(root)
frame_fin.pack()

entry_fin_year = tk.Entry(frame_fin, width=6)
entry_fin_year.pack(side="left", padx=2)
entry_fin_year.insert(0, "2026")

entry_fin_month = tk.Entry(frame_fin, width=4)
entry_fin_month.pack(side="left", padx=2)
entry_fin_month.insert(0, "12")

entry_fin_day = tk.Entry(frame_fin, width=4)
entry_fin_day.pack(side="left", padx=2)
entry_fin_day.insert(0, "31")

tk.Button(
    root,
    text="Generar lista wget",
    command=guardar_fechas
).pack(pady=20)

root.mainloop()
