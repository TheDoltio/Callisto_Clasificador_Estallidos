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
TIME_TOLERANCE_MINUTES = 5

CLASSES = {
    "Tipo II": "Tipo_II",
    "Tipo III": "Tipo_III",
    "Tipo IV": "Tipo_IV",
    "Otros": "Otros",
    "Ruido": "Ruido",
    "No estoy seguro": "No_estoy_seguro"
}


def parse_filename(filepath):
    basename = os.path.basename(filepath)
    name = basename.replace(".fit.gz", "").replace(".fit", "")
    parts = name.split("_")

    if len(parts) < 4:
        return None

    station = parts[0]
    date_str = parts[1]
    time_str = parts[2]

    try:
        dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
    except ValueError:
        return None

    return station, dt


def find_companion(primary_file, all_files, tolerance_minutes=TIME_TOLERANCE_MINUTES):
    result = parse_filename(primary_file)
    if result is None:
        return None

    primary_station, primary_dt = result
    tolerance = timedelta(minutes=tolerance_minutes)

    candidates = []
    for f in all_files:
        if f == primary_file:
            continue

        res = parse_filename(f)
        if res is None:
            continue

        station, dt = res

        if station == primary_station:
            continue

        # Deben ser del mismo día
        if dt.date() != primary_dt.date():
            continue

        # Diferencia de tiempo simple, sin ajuste de medianoche
        time_diff = abs(dt - primary_dt)

        if time_diff <= tolerance:
            candidates.append(f)

    if not candidates:
        return None

    return random.choice(candidates)


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


def plot_spectrogram(ax, filepath, global_start, global_end):

    data, header, freqs = read_fits(filepath)
    data = preprocess_data(data)

    dt_start, dt_end = get_time_range(header)


    global_duration = (global_end - global_start).total_seconds() / 60.0

    offset_start = (dt_start - global_start).total_seconds() / 60.0
    offset_end   = (dt_end   - global_start).total_seconds() / 60.0

    extent = (
        offset_start,
        offset_end,
        freqs[-1],
        freqs[0]
    )

    ax.imshow(
        data,
        aspect="auto",
        extent=extent,
        vmin=VMIN,
        vmax=VMAX,
        cmap="jet"
    )


    ax.set_xlim(0, global_duration)
    ax.set_ylim(55, 85)
    ax.set_xlabel("Tiempo en minutos")
    ax.set_ylabel("Frecuencia [MHz]")



class ClassifierApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Clasificador CALLISTO")

        self.files = glob.glob(os.path.join(RAW_DIR, "*.fit*"))
        self.current_file = None
        self.companion_file = None


        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()


        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        for label in CLASSES:
            b = tk.Button(
                button_frame,
                text=label,
                width=15,
                command=lambda l=label: self.classify(l)
            )
            b.pack(side=tk.LEFT, padx=5)


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
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.text(0.5, 0.5, "No more files",
                          ha='center', va='center',
                          transform=self.ax1.transAxes)
            self.canvas.draw()
            return

        shuffled = random.sample(self.files, len(self.files))

        for candidate in shuffled:

            if candidate == self.current_file:
                continue
            companion = find_companion(candidate, self.files)
            if companion is not None:
                self.current_file = candidate
                self.companion_file = companion
                self._render()
                return


        print("Ningún archivo tiene compañero. Eliminando archivos sin par...")
        for f in list(self.files):
            print(f"Eliminando: {f}")
            os.remove(f)
        self.files.clear()
        self.load_random_file()

    def _render(self):
        self.ax1.clear()
        self.ax2.clear()

        try:

            _, header1, _ = read_fits(self.current_file)
            _, header2, _ = read_fits(self.companion_file)

            start1, end1 = get_time_range(header1)
            start2, end2 = get_time_range(header2)


            global_start = min(start1, start2)
            global_end   = max(end1,   end2)

        except Exception as e:
            print(f"Error calculando el marco de tiempo global: {e}")
            return

        try:
            plot_spectrogram(self.ax1, self.current_file, global_start, global_end)
        except Exception as e:
            print(f"Error leyendo {self.current_file}: {e}")
            self.ax1.text(0.5, 0.5, "Error al leer archivo",
                          ha='center', va='center',
                          transform=self.ax1.transAxes)

        try:
            plot_spectrogram(self.ax2, self.companion_file, global_start, global_end)
        except Exception as e:
            print(f"Error leyendo {self.companion_file}: {e}")
            self.ax2.text(0.5, 0.5, "Error al leer archivo",
                          ha='center', va='center',
                          transform=self.ax2.transAxes)

        self.fig.tight_layout()
        self.canvas.draw()

    def classify(self, label):
        if not self.current_file:
            return


        if label == "No estoy seguro":
            self.load_random_file()
            return

        class_folder = CLASSES[label]
        target_dir = os.path.join(CLASS_DIR, class_folder)
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(
            target_dir,
            os.path.basename(self.current_file)
        )
        shutil.move(self.current_file, target_path)
        print(f"Movido '{os.path.basename(self.current_file)}' a '{class_folder}'")
        self.files.remove(self.current_file)


        if self.companion_file and self.companion_file in self.files:
            companion_path = os.path.join(
                target_dir,
                os.path.basename(self.companion_file)
            )
            shutil.move(self.companion_file, companion_path)
            print(f"Movido '{os.path.basename(self.companion_file)}' a '{class_folder}'")
            self.files.remove(self.companion_file)

        self.current_file = None
        self.companion_file = None

        self.load_random_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClassifierApp(root)
    root.mainloop()
