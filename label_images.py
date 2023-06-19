import os
import tkinter as tk
from PIL import Image, ImageTk

# Verzeichnis mit den Bildern
image_directory = "./"

# Verzeichnis für die gelabelten Bilder
labeled_directory = "./"

# Liste der verfügbaren Labels
labels = ["cobblestone", "road"]


# Funktion zur Anzeige des Bilds und zum Labeln
def label_image(image_path):
    def on_button_click(label):
        nonlocal root
        nonlocal image_path

        # Benennen und Verschieben des gelabelten Bilds
        labeled_filename = (
            f"{os.path.basename(image_path).split('.')[0]}_{labels[label]}.jpg"
        )
        labeled_path = os.path.join(labeled_directory, labeled_filename)
        os.rename(image_path, labeled_path)

        root.quit()  # Schließen des Fensters

    # Initialisierung des Hauptfensters
    root = tk.Tk()
    root.title("Bild Labeln")

    img = Image.open(image_path)
    img.thumbnail((400, 400))  # Ändern Sie die Größe des Bildes, um es anzuzeigen
    img_tk = ImageTk.PhotoImage(img)
    # img_tk = tk.PhotoImage(img)

    # Anzeige des Bilds in einem Label
    label = tk.Label(root, image=img_tk)
    # label.image = img_tk
    label.pack()

    # Erstellung von Buttons für jedes Label
    for i, label_name in enumerate(labels):
        button = tk.Button(
            root, text=label_name, command=lambda i=i: on_button_click(i)
        )
        button.pack()

    root.mainloop()
    root.destroy()


# Schleife zum Labeln der Bilder im Verzeichnis
for filename in os.listdir(image_directory):
    if filename.endswith(
        ".jpg"
    ):  #  or filename.endswith('.png') # Nur Bilder berücksichtigen
        image_path = os.path.join(image_directory, filename)
        print(image_path)
        label_image(image_path)
