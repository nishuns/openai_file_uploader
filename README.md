
# Python Virtual Environment Setup Guide

## 1. Creating a Virtual Environment

### macOS/Linux
1. **Open a terminal**.
2. Navigate to your project directory.
3. Run the following command to create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
   This will create a virtual environment named `venv` in your current directory.

### Windows
1. **Open a command prompt or PowerShell**.
2. Navigate to your project directory.
3. Run the following command to create a virtual environment:
   ```bash
   python -m venv venv
   ```
   This will create a virtual environment named `venv` in your current directory.

## 2. Activating the Virtual Environment

### macOS/Linux
In the terminal, run the following command:
```bash
source venv/bin/activate
```

### Windows (Command Prompt)
In the Command Prompt, run the following command:
```cmd
venv\Scripts\activate
```

### Windows (PowerShell)
In PowerShell, run the following command:
```powershell
venv\Scripts\Activate.ps1
```

> **Note:** If you're using PowerShell, you may need to change the execution policy to allow script running by using:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## 3. Installing Dependencies from `requirements.txt`

Once your virtual environment is activated, you can install all the dependencies listed in `requirements.txt` by running:

```bash
pip install -r requirements.txt
```

> **Note:** Make sure the virtual environment is activated before running this command to ensure that the packages are installed within the environment.

## 4. Running the `openai_upload.py` Script

### macOS/Linux
- If your system defaults to Python 3:
  ```bash
  python openai_upload.py
  ```
- If your system still defaults to Python 2, use:
  ```bash
  python3 openai_upload.py
  ```

### Windows
- You can typically run Python with:
  ```cmd
  python openai_upload.py
  ```
