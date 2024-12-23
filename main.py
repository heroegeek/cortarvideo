import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
import ffmpeg
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage

class VideoCutterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("App para cortar videos - Hecho con 💗 por Héroe Geek")
        self.geometry("720x500")
        self.resizable(False, False) 

        # Variables
        self.video_path = None
        self.output_folder = None

        # Fondo y logo
        self.configure_fondo_logo()

        # Widgets de la interfaz
        self.label_title = ctk.CTkLabel(self, text="Cortar Video en Partes", font=("Arial", 20))
        self.label_title.pack(pady=20)

        self.button_select_video = ctk.CTkButton(self, text="Seleccionar Video", command=self.seleccionar_video)
        self.button_select_video.pack(pady=10)

        self.label_video = ctk.CTkLabel(self, text="No se ha seleccionado ningún video")
        self.label_video.pack(pady=5)

        self.button_select_folder = ctk.CTkButton(self, text="Seleccionar Carpeta de Destino", command=self.seleccionar_carpeta)
        self.button_select_folder.pack(pady=10)

        self.label_folder = ctk.CTkLabel(self, text="No se ha seleccionado ninguna carpeta")
        self.label_folder.pack(pady=5)

        self.entry_intervalo = ctk.CTkEntry(self, placeholder_text="Duración en segundo de cada segmento")
        self.entry_intervalo.pack(pady=10)

        self.entry_steps = ctk.CTkEntry(self, placeholder_text="Cantidad de cortes")
        self.entry_steps.pack(pady=10)

        self.button_cut_video = ctk.CTkButton(self, text="Cortar Video", command=self.cortar_video)
        self.button_cut_video.pack(pady=20)

    def configure_fondo_logo(self):
        self.background_frame = ctk.CTkFrame(self, width=720, height=500)
        self.background_frame.place(relx=0, rely=0, anchor="nw")

        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        logo_path = os.path.join(base_path, "logo.png")

        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            self.logo_photo = CTkImage(logo_image, size=(100, 100)) 

            self.logo_label = ctk.CTkLabel(self.background_frame, image=self.logo_photo, text="")
            self.logo_label.place(x=10, y=10)  
        else:
            print(f"Logo no encontrado en: {logo_path}")

    def seleccionar_video(self):
        self.video_path = filedialog.askopenfilename(title="Seleccionar un video", filetypes=[("Archivos de video", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            self.label_video.configure(text=f"Video seleccionado: {os.path.basename(self.video_path)}")
        else:
            self.label_video.configure(text="No se ha seleccionado ningún video")

    def seleccionar_carpeta(self):
        self.output_folder = filedialog.askdirectory(title="Seleccionar una carpeta para guardar los videos cortados")
        if self.output_folder:
            self.label_folder.configure(text=f"Carpeta seleccionada: {self.output_folder}")
        else:
            self.label_folder.configure(text="No se ha seleccionado ninguna carpeta")

    def cortar_video(self):
        if not self.video_path:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ningún video.")
            return

        if not self.output_folder:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carpeta de destino.")
            return

        intervalo_segundos = self.entry_intervalo.get()
        if not intervalo_segundos.isdigit() or int(intervalo_segundos) <= 0:
            messagebox.showwarning("Advertencia", "Debe ingresar un valor válido para la duración del segmento.")
            return

        steps = self.entry_steps.get()
        if steps and (not steps.isdigit() or int(steps) <= 0):
            messagebox.showwarning("Advertencia", "Debe ingresar un valor válido para la cantidad de pasos.")
            return

        intervalo_segundos = int(intervalo_segundos)
        steps = int(steps) if steps else None

        try:
            # Definir rutas de FFmpeg y FFprobe
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            ffmpeg_path = os.path.join(base_path, "ffmpeg/bin/ffmpeg.exe")
            ffprobe_path = os.path.join(base_path, "ffmpeg/bin/ffprobe.exe")

            print(f"Usando FFmpeg en: {ffmpeg_path}")
            print(f"Usando FFprobe en: {ffprobe_path}")
            print(f"Procesando archivo: {self.video_path}")
            
            # Obtener duración total del video
            probe = ffmpeg.probe(self.video_path, cmd=ffprobe_path)
            duracion_total = float(probe['format']['duration'])
            print(f"Duración total del video: {duracion_total} segundos.")

            nombre_base = os.path.splitext(os.path.basename(self.video_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
            start_time = 0
            part = 1

            while start_time < duracion_total:
                end_time = min(start_time + intervalo_segundos, duracion_total)
                output_path = os.path.join(self.output_folder, f"{nombre_base}_{timestamp}_parte_{part}.mp4")

                print(f"Creando segmento {part}: {start_time} - {end_time}")
                ffmpeg.input(self.video_path, ss=start_time, to=end_time).output(output_path, vcodec="copy", acodec="copy").run(cmd=ffmpeg_path)

                start_time += intervalo_segundos
                part += 1

                if steps and part > steps:
                    break

            messagebox.showinfo("Éxito", "El video ha sido cortado y guardado exitosamente.")
        except ffmpeg.Error as e:
            error_msg = f"Error de FFmpeg:\n{e.stderr.decode('utf-8')}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"Ocurrió un error inesperado:\n{e}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)

if __name__ == "__main__":
    app = VideoCutterApp()
    app.mainloop()