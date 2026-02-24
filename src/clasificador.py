import os
import glob
import random
import shutil
import numpy as np

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from astropy.io import fits
from datetime import datetime, timedelta
import tkinter as tk


VMIN = -1
VMAX = 5

RAW_DIR = "../raw_data"
CLASS_DIR = "../clas_data"

CLASSES = {
    "Tipo II": "Tipo_II",
    "Tipo III": "Tipo_III",
    "Tipo IV": "Tipo_IV",
    "Otros": "Otros",
    "Ruido": "Ruido"
}


def read_fits(file_path):
    with fits.open(file_path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
        freqs = hdul[1].data['Frequency'][0]
    return data, header, freqs


def get_time_range(header):
    y, m, d = map(int, header["DATE-OBS"].split("/"))

    hh_i, mm_i, ss_i = map(float, header["TIME-OBS"].split(":"))
    dt_start = datetime(y, m, d, int(hh_i), int(mm_i), int(ss_i))

    hh_f, mm_f, ss_f = map(float, header["TIME-END"].split(":"))

    if int(hh_f) == 24:
        dt_end = datetime(y, m, d, 0, int(mm_f), int(ss_f)) + timedelta(days=1)
    else:
        dt_end = datetime(y, m, d, int(hh_f), int(mm_f), int(ss_f))

    if dt_end < dt_start:
        dt_end += timedelta(days=1)

    return dt_start, dt_end


def preprocess_data(data):
    data = data - np.median(data, axis=1, keepdims=True)
    data = data.clip(-5, 120)
    data = data * 2500.0 / 255.0 / 25.4
    return data


class ClassifierApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Clasificador CALLISTO")

        self.files = glob.glob(os.path.join(RAW_DIR, "*.fit*"))
        self.current_file = None

        # Figura matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()

        # Botones de clasificación
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        for label in CLASSES:
            b = tk.Button(
                button_frame,
                text=label,
                width=10,
                command=lambda l=label: self.classify(l)
            )
            b.pack(side=tk.LEFT, padx=5)

        # Botón Subir datos
        upload_button = tk.Button(
            master,
            text="Subir datos",
            width=20,
            command=self.master.quit
        )
        upload_button.pack(pady=10)

        self.load_random_file()


    def load_random_file(self):
        if not self.files:
            print("No hay más archivos.")
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No more files",
                         ha='center', va='center',
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return

        self.current_file = random.choice(self.files)

        data, header, freqs = read_fits(self.current_file)
        data = preprocess_data(data)

        dt_start, dt_end = get_time_range(header)
        total_seconds = (dt_end - dt_start).total_seconds()

        time_minutes = np.linspace(
            0,
            total_seconds / 60.0,
            data.shape[1]
        )

        self.ax.clear()

        extent = (
            time_minutes[0],
            time_minutes[-1],
            freqs[-1],
            freqs[0]
        )

        self.ax.imshow(
            data,
            aspect="auto",
            extent=extent,
            vmin=VMIN,
            vmax=VMAX,
            cmap="jet"
        )

        self.ax.set_ylim(55, 85)
        self.ax.set_xlabel("Tiempo en minutos")
        self.ax.set_ylabel("Frecuencia [MHz]")

        self.canvas.draw()


    def classify(self, label):
        if not self.current_file:
            return

        class_folder = CLASSES[label]
        target_dir = os.path.join(CLASS_DIR, class_folder)
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(
            target_dir,
            os.path.basename(self.current_file)
        )

        shutil.move(self.current_file, target_path)
        print(f"Movido a {class_folder}")

        self.files.remove(self.current_file)
        self.load_random_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClassifierApp(root)
    root.mainloop()
