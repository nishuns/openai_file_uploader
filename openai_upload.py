import os
import pyperclip  # For copying to clipboard
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Install pyperclip if needed: pip install pyperclip

# Default OpenAI API Key (you can replace this with your actual key)
DEFAULT_OPENAI_API_KEY = "your-default-openai-api-key"

selected_paths = []  # Variable to store the selected files or folders
vector_store_id_label = None  # Store the vector store label reference

# Function to copy text to clipboard
def copy_to_clipboard(text):
    pyperclip.copy(text)
    messagebox.showinfo("Copied", "Vector Store ID copied to clipboard!")

# Function to upload file to OpenAI and return the file ID
def upload_file_to_openai(client, file_path):
    try:
        with open(file_path, "rb") as f:
            response = client.files.create(
                file=f,
                purpose="assistants"  # Updated purpose to 'assistants'
            )
        file_id = response.id  # Access the 'id' attribute directly
        return file_id
    except Exception as e:
        raise e

# Function to create a new vector store
def create_vector_store(client):
    try:
        vector_store = client.beta.vector_stores.create(name="Support FAQ")
        vector_store_id = vector_store.id  # Access the 'id' attribute directly
        return vector_store_id
    except Exception as e:
        raise e

# Function to attach files to the vector store
def attach_files_to_vector_store(client, vector_store_id, file_ids):
    try:
        response = client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store_id,
            file_ids=file_ids
        )
        return response
    except Exception as e:
        raise e

# Function to upload files to OpenAI and either use a custom vector store or create a new one
def process_and_upload_files(paths, openai_key, custom_vector_store_id=None):
    file_ids = []

    # Create the OpenAI client instance with the provided API key
    client = OpenAI(api_key=openai_key)

    try:
        files = []

        # Collect all file paths from the selected items
        for path in paths:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                # If it's a folder, get all files in the folder
                for root, _, filenames in os.walk(path):
                    files.extend([os.path.join(root, f) for f in filenames])

        if not files:
            messagebox.showinfo("Info", "No files found in the selected files or folders.")
            return

        # Show the progress bar and configure it
        progress_bar.grid(row=8, column=0, columnspan=2, padx=20, pady=10)  # Show progress bar
        progress_bar["maximum"] = len(files)
        progress_bar["value"] = 0

        # Upload each file and get the file ID
        for index, file_path in enumerate(files):
            # Upload the file to OpenAI
            file_id = upload_file_to_openai(client, file_path)
            file_ids.append(file_id)

            # Update the progress bar
            progress_bar["value"] = index + 1
            root.update_idletasks()  # Allow the GUI to update

        # Check if a custom vector store ID was provided
        if custom_vector_store_id:
            vector_store_id = custom_vector_store_id
        else:
            # Create a new vector store
            vector_store_id = create_vector_store(client)

        # Attach uploaded files to the vector store
        attach_files_to_vector_store(client, vector_store_id, file_ids)

        # Update the vector store ID label
        vector_store_id_label.config(text=f"Vector Store ID: {vector_store_id}")
        copy_button.grid(row=9, column=1, sticky="w")  # Show the copy button

        messagebox.showinfo("Success", "Files uploaded and attached to vector store successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        progress_bar.grid_remove()  # Hide progress bar when done

# Function to open file/folder dialog and select items
def choose_files_and_folders():
    global selected_paths
    file_paths = filedialog.askopenfilenames(title="Select Files or Folders")
    folder_path = filedialog.askdirectory(title="Select Folder (Optional)")
    
    if file_paths:
        selected_paths = list(file_paths)
    if folder_path:
        selected_paths.append(folder_path)

    if selected_paths:
        display_paths = "\n".join([(path[:40] + '...' + path[-20:]) if len(path) > 60 else path for path in selected_paths])
        folder_label.config(text=f"Selected Files/Folders:\n{display_paths}")

# Function triggered by the upload button
def upload_files():
    if not selected_paths:
        messagebox.showerror("Error", "Please select files or folders first.")
        return
    
    # Get the OpenAI API key and custom vector store ID from the input fields
    openai_key = openai_key_entry.get().strip()
    custom_vector_store_id = custom_vector_store_entry.get().strip() or None

    if not openai_key:
        messagebox.showerror("Error", "Please enter the OpenAI API key.")
        return

    process_and_upload_files(selected_paths, openai_key, custom_vector_store_id)

# Setup the Tkinter window
root = tk.Tk()
root.title("Upload Files or Folders to OpenAI Vector Store")
root.geometry("600x500")

# Label and input field for OpenAI API Key (with default value)
openai_key_label = tk.Label(root, text="OpenAI API Key:", padx=10, pady=5)
openai_key_label.grid(row=0, column=0, sticky="w")
openai_key_entry = tk.Entry(root, width=50)
openai_key_entry.insert(0, DEFAULT_OPENAI_API_KEY)  # Set default value for OpenAI API Key
openai_key_entry.grid(row=0, column=1, padx=10, pady=5)

# Label and input field for Custom Vector Store ID (optional)
custom_vector_store_label = tk.Label(root, text="Custom Vector Store ID (Optional):", padx=10, pady=5)
custom_vector_store_label.grid(row=1, column=0, sticky="w")
custom_vector_store_entry = tk.Entry(root, width=50)
custom_vector_store_entry.grid(row=1, column=1, padx=10, pady=5)

# Label to display the chosen files/folders
folder_label = tk.Label(root, text="No files or folders selected", padx=10, pady=10, anchor="w", justify="left")
folder_label.grid(row=2, column=0, columnspan=2, sticky="w")

# Button to choose files and folders
choose_button = tk.Button(root, text="Choose Files/Folders", command=choose_files_and_folders, padx=10, pady=5)
choose_button.grid(row=3, column=0, sticky="w", padx=10, pady=10)

# Button to upload files
upload_button = tk.Button(root, text="Upload Files", command=upload_files, padx=10, pady=5)
upload_button.grid(row=3, column=1, sticky="w", padx=10, pady=10)

# Label to display the vector store ID (once available)
vector_store_id_label = tk.Label(root, text="Vector Store ID: Not available yet", padx=10, pady=10)
vector_store_id_label.grid(row=9, column=0, columnspan=2, sticky="w")

# Copy button to copy the vector store ID to the clipboard
copy_button = tk.Button(root, text="Copy", command=lambda: copy_to_clipboard(vector_store_id_label.cget("text").replace("Vector Store ID: ", "")))
copy_button.grid(row=9, column=1, sticky="e")
copy_button.grid_remove()  # Hide the copy button initially

# Progress bar (initially hidden)
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=400)
progress_bar.grid(row=8, column=0, columnspan=2, padx=20, pady=10)
progress_bar.grid_remove()  # Hide initially

# Start the Tkinter loop
root.mainloop()
