import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Function to remove spaces from file names
def remove_spaces_in_filenames(directory):
    try:
        # Get the list of files
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        # If no files found, show a message and return
        if not files:
            messagebox.showinfo("Info", "No files found in the selected folder.")
            return

        # Show the progress bar and configure it
        progress_bar.grid(row=3, column=0, padx=20, pady=10)  # Show progress bar
        progress_bar["maximum"] = len(files)
        progress_bar["value"] = 0

        # Iterate over all files in the given directory
        for index, filename in enumerate(files):
            old_file = os.path.join(directory, filename)
            new_filename = filename.replace(" ", "")
            new_file = os.path.join(directory, new_filename)

            # Rename the file
            os.rename(old_file, new_file)

            # Update the progress bar
            progress_bar["value"] = index + 1
            root.update_idletasks()  # Allow the GUI to update

        messagebox.showinfo("Success", "Files renamed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        progress_bar.grid_remove()  # Hide progress bar when done

# Function to open folder dialog and select a folder
def choose_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_label.config(text=f"Selected Folder: {folder_selected}")
        remove_spaces_in_filenames(folder_selected)

# Setup the Tkinter window
root = tk.Tk()
root.title("Remove Spaces from Filenames")
root.geometry("400x200")

# Label to display the chosen folder
folder_label = tk.Label(root, text="No folder selected", padx=20, pady=20)
folder_label.grid(row=0, column=0)

# Button to choose folder
choose_button = tk.Button(root, text="Choose Folder", command=choose_folder, padx=10, pady=10)
choose_button.grid(row=1, column=0)

# Progress bar (initially hidden)
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300)
progress_bar.grid(row=3, column=0, padx=20, pady=10)
progress_bar.grid_remove()  # Hide initially

# Start the Tkinter loop
root.mainloop()
