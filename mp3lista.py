import os
import tkinter as tk
import datetime
import eyed3
import logging
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font
from typing import List, Tuple
from tinytag import TinyTag

logging.basicConfig(level=logging.ERROR)
logging.basicConfig(level=logging.CRITICAL)

def main():
    app = ZeneListaKeszito()
    app.run()

class ZeneListaKeszito:
    def run(self):
        self.root.mainloop()
        
    def create_txt_report(self, subdir: str, files: List[str], root_directory: str):
        report_name = os.path.basename(subdir) + ".txt"
        report_path = os.path.join(subdir, report_name)
        try:
            with open(report_path, "w", encoding="utf-8") as report_file:
                total_size = 0
                total_files = len(files)

                for index, file in enumerate(files, start=1):
                    self.current_file_label.config(text=f"Feldolgozás alatt: {file}")
                    self.root.update_idletasks()

                    file_path = os.path.join(subdir, file)
                    file_size = os.path.getsize(file_path)
                    file_size_formatted = self.format_file_size(file_size)
                    total_size += file_size

                    # ID3 címkék kinyerése
                    audiofile = eyed3.load(file_path)
                    if audiofile is not None:
                        title = audiofile.tag.title or "N/A"
                        artist = audiofile.tag.artist or "N/A"
                        album = audiofile.tag.album or "N/A"
                        year = audiofile.tag.getBestDate() or "N/A"
                        genre = audiofile.tag.genre or "N/A"
                        composer = audiofile.tag.composer or "N/A"
                    else:
                        title = "N/A"
                        artist = "N/A"
                        album = "N/A"
                        year = "N/A"
                        genre = "N/A"
                        composer = "N/A"

                    report_file.write(
                        f"{index}. {file} ({file_path}) - {file_size_formatted}\n"
                        f"  Cím: {title}\n"
                        f"  Előadó: {artist}\n"
                        f"  Album: {album}\n"
                        f"  Kiadás éve: {year}\n"
                        f"  Műfaj: {genre}\n"
                        f"  Dal szövegírója: {composer}\n\n"
                    )

                report_file.write(f"\nÖsszesítés:\n")
                report_file.write(f"Fájlok összmérete: {self.format_file_size(total_size)}\n")
                report_file.write(f"Zeneszámok száma: {total_files}\n")
        except PermissionError:
            with open(os.path.join(root_directory, "hibak.txt"), "a", encoding="utf-8") as error_file:
                error_file.write(f"PermissionError: nem sikerült írni a {report_path} fájlt\n")


    def process_directory(self, directory):
        all_files = self.get_all_files(directory)
        self.create_combined_playlist(directory, all_files)
        self.create_summary_txt_file(directory, all_files)  # Hozzáadva itt
        
    def create_summary_txt_file(self, directory, all_files):
        summary_file_path = os.path.join(directory, "osszesito_zene_lista.txt")
        total_files = 0
        total_size = 0

        with open(summary_file_path, "w", encoding="utf-8") as summary_file:
            for file_path in all_files:
                if file_path.lower().endswith(".mp3"):
                    total_files += 1
                    total_size += os.path.getsize(file_path)
                    summary_file.write(f"{os.path.relpath(file_path, directory)}\n")

            summary_file.write(f"\nÖsszes zenei fájl: {total_files}\n")
            summary_file.write(f"Összes méret: {self.format_file_size(total_size)}\n")

     
    def get_tags(self, file_path: str) -> dict:
        try:
            tag = TinyTag.get(file_path)
            return {
                "title": tag.title or "",
                "artist": tag.artist or "",
                "album": tag.album or "",
                "year": tag.year or "",
                "genre": tag.genre or "",
                "composer": tag.composer or "",
            }
        except Exception:  # itt cseréld le a TinyTagException-t Exception-re
            return {
                "title": "",
                "artist": "",
                "album": "",
                "year": "",
                "genre": "",
                "composer": "",
            }

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x400")
        self.root.title("Zene lista készítő program")
        self.init_widgets()
        
    
    def create_combined_playlist(self, root_directory: str, all_files: List[str], output_directory: str):
        playlist = []

        for file_path in all_files:
            file_relative_path = os.path.relpath(file_path, root_directory)
            playlist.append(file_relative_path)

        output_file_path = os.path.join(root_directory, "teljes_zene_lista.m3u")

        with open(output_file_path, "w", encoding="utf-8") as f:
            for file in playlist:
                f.write(f'#EXTINF:-1,{os.path.basename(file)}\n')
                f.write(file + "\n")

        print(f"Combined playlist created at: {output_file_path}")
        # Bezárja az ablakot a feldolgozás befejezése után
        self.root.quit()

        
    def format_file_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KBytes"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MBytes"
        elif size < 1024 * 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GBytes"
        else:
            return f"{size / (1024 * 1024 * 1024 * 1024):.2f} TBytes"

    def update_date_time(self):
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_time_label.config(text=current_date_time)
        self.root.after(1000, self.update_date_time)
    def init_widgets(self):
        arial_20 = Font(family="Arial", size=20)
        arial_30 = Font(family="Arial", size=30)
        arial_16 = Font(family="Arial", size=16)

        label1 = tk.Label(self.root, text="Zene lista készítő program", font=arial_30)
        label1.pack(pady=10)

        label2 = tk.Label(self.root, text="© 2023 - Bölöni Csaba", font=arial_20, fg="red")
        label2.pack(pady=10)

        button = tk.Button(self.root, text="Válassz kezdő mappa helyet", command=self.select_directory)
        button.pack(pady=10)
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100, mode="determinate")
        progress_bar.pack(pady=10, padx=10, fill=tk.X)

        self.current_file_label = tk.Label(self.root, text="")
        self.current_file_label.pack(pady=10)
        self.date_time_label = tk.Label(self.root, text="", fg="green", font=arial_30)
        self.date_time_label.pack(pady=10, anchor='s', side='bottom')

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.process_directory(directory)
            
    def process_directory(self, directory: str):
        all_files = []
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.mp3'):
                    file_path = os.path.join(subdir, file)
                    all_files.append(file_path)
                    self.create_txt_report(subdir, [file_path], directory)
        self.create_combined_playlist(directory, all_files, directory)

        
        
    def find_music_files(self, directory: str) -> List[Tuple[str, List[str]]]:
        music_files = []

        total_subdirs = sum([len(dirs) for _, dirs, _ in os.walk(directory)])
        processed_subdirs = 0

        for subdir, dirs, files in os.walk(directory):
            files_in_subdir = []
            for file in files:
                if file.endswith(".mp3") or file.endswith(".flac"):
                    files_in_subdir.append(file)
            if files_in_subdir:
                music_files.append((subdir, sorted(files_in_subdir)))

            processed_subdirs += 1
            self.progress_var.set((processed_subdirs / total_subdirs) * 100)
            self.root.update_idletasks()

        return music_files
    
                
    def collect_files_with_extension(extensions, start_folder):
        all_files = []
        for root, dirs, files in os.walk(start_folder):
            for file in files:
                file_path = os.path.join(root, file)
                _, file_extension = os.path.splitext(file_path)
                if file_extension.lower() in extensions:
                    try:
                        tag = TinyTag.get(file_path)
                    except TinyTagException as e:
                        logging.error(f"Error processing {file_path}: {str(e)}")
                    else:
                        all_files.append(file_path)
        return all_files

def format_file_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"

def create_summary_txt_file(self, directory, all_files):
    summary_file_path = os.path.join(directory, "osszesito_zene_lista.txt")
    total_files = 0
    total_size = 0  # Új változó a fájlok méretének összegzéséhez

    with open(summary_file_path, "w", encoding="utf-8") as summary_file:
        for file_path in all_files:
            if file_path.lower().endswith(".mp3"):
                total_files += 1
                total_size += os.path.getsize(file_path)  # Hozzáadjuk a fájl méretét
                summary_file.write(f"{os.path.relpath(file_path, directory)}\n")

        summary_file.write(f"\nÖsszes zenei fájl: {total_files}\n")
        summary_file.write(f"Összes méret: {format_file_size(total_size)}\n")  # Hozzáadjuk az összes méretet

            
    def create_playlist(self, subdir: str, files: List[str], root_directory: str):
    
        playlist_name = os.path.basename(subdir) + ".m3u"
        playlist_path = os.path.join(subdir, playlist_name)

        try:
            with open(playlist_path, "w", encoding="utf-8") as playlist_file:
 
                playlist_file.write("#EXTM3U\n")
                for file in files:
                    self.current_file_label.config(text=f"Feldolgozás alatt: {file}")
                    self.root.update_idletasks()
                    file_path = os.path.join(subdir, file)
                    relative_path = os.path.relpath(file_path, subdir)
                    playlist_file.write(f"#EXTINF:-1,{file}\n{relative_path}\n")
        except PermissionError:
            with open(os.path.join(root_directory, "hibak.txt"), "a", encoding="utf-8") as error_file:
                error_file.write(f"PermissionError: nem sikerült írni a {playlist_path} fájlt\n")
    
 
   
    def run(self):
        self.update_date_time()
        self.root.mainloop()

if __name__ == "__main__":
    main()