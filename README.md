# Introduction

This RC bootcamp is designed to help you learn reservoir computing (RC).
In particular, it is aimed at beginners who want to quickly grasp important concepts and techniques.

## Jupyter Notebook

In this material, we will use Python, a programming language.
Additionally, in the long run, we aim to master an interactive experimentation approach using Jupyter Notebooks.
Below are some representative setup and execution methods in order of difficulty for saving results.
Please set it up using your preferred method.

### Method 1. Google Colaboratory + Google Drive (beginner)

Google Colaboratory is a browser-based Jupyter Notebook frontend suited for beginners.
No additional setup is required beyond a Google account, as core packages (e.g., `numpy`, `matplotlib`) are preinstalled.
Unlike the read-only link on https://rc-bootcamp.github.io/, this method allows you to place notebooks directly on Google Drive for editing and preserving results.
Note that free-tier resources are limited and sessions time out after periods of inactivity, so we recommend transitioning to a local environment once you are familiar with the basics.

0. Create or sign into your Google account.
1. Download and extract the RC bootcamp materials (zip file).
2. Upload the entire folder containing this notebook to Google Drive.
3. Open the notebook file with a .ipynb extension.
4. Start the kernel and run cells with Shift+Enter.
5. In the cell that mounts Drive (`drive.mount("/content/gdrive")`), change `if False:` to `if True:`, and adjust the Google Drive path (e.g., `%cd /content/gdrive/My Drive/...`) if needed.
6. Run that cell and authenticate when prompted to grant access to your Google Drive.

Step 5 is required to run the notebook on Google Drive; do not skip it.

---

### Method 2. uv + VSCode (competent)

This method uses the package management tool `uv` to create a virtual environment and run it on VSCode. It is highly recommended for anyone engaging in serious research and development.
Its versatility and the robust support provided by VSCode extensions make it suitable even for beginners (it really isn’t that difficult once you get used to it).

#### Step 1. Installing uv

[`uv`](https://github.com/astral-sh/uv) is a tool for managing Python packages.
Not only can you install packages on a per-project basis, but it can also be used for distributing projects by recording the version of each package (similar to conda, but uv operates extremely fast). Please follow the steps in the [documentation](https://docs.astral.sh/uv/getting-started/installation) to install it.
Below are the minimum steps.

##### Linux and MacOS

Open your terminal and install it using the following command:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then, check if it has been installed by executing:
```sh
uv help
```

##### Windows

Open PowerShell (open the Start Menu, type "Windows PowerShell", and launch the Windows PowerShell application) and install using the following command:
```sh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, check if it has been installed by executing:
```sh
uv help
```

#### Step 2. Configuring VSCode

[Visual Studio Code (VSCode)](https://code.visualstudio.com/) is a cross-platform IDE developed by Microsoft.
Download and run the [installer](https://code.visualstudio.com/download).
Once installed, the `code` command becomes available, so either drag the target folder into VSCode or open the desired directory from your terminal using the following command (for Windows, please use PowerShell):

```sh
code PATH_TO_DIR
```

One of the standout features of VSCode is its wide range of extensions.
Extensions can be installed via the `Extensions` tab on the left.
The minimum recommended packages are listed in `.vscode/extensions.json`. When you open the Extensions tab in VSCode, those packages will appear in the recommendations; just click on them to install.

#### Step 3. Creating the virtual environment

When you open the material's folder in VSCode, a list of the folder's contents will appear on the left side.
Press `Ctrl+Shift+@` to open the terminal at the bottom of the screen.
Then, enter the following command to set up the virtual environment:

```sh
uv sync
```

Based on the information in uv.lock, a folder named .venv will be created in the same directory.
The virtual environment will then be set up.
At the same time, the Python kernel and Python packages used in this material will be automatically installed.
This process may take a few minutes. Once the installation is complete, launch the environment, press `Ctrl+Shift+P`, and select `Python: Select Interpreter` to specify the kernel to use (in this case, .venv).
For `.ipynb` files, similarly, select the target Python kernel from `Select Kernel` displayed in the upper right corner.

Additionally, if you are using Linux or macOS, you can enter the virtual environment by running the following command:

```sh
source .venv/bin/activate
```

For Windows, run the following command:

```powershell
.venv\Scripts\activate
```

#### Step 4. Additional VSCode configuration (Optional)

`Ruff` is a linting tool for Python that automatically formats your code.
By adding the following settings to `.vscode/settings.json`, they will be automatically applied whenever you save the file.

```javascript
{
    "notebook.output.wordWrap": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        },
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "notebook.formatOnSave.enabled": true,
    "notebook.codeActionsOnSave": {
        "notebook.source.fixAll": "explicit",
        "notebook.source.organizeImports": "explicit",
    },
    "jupyter.notebookFileRoot": "${fileDirname}",
}
```
