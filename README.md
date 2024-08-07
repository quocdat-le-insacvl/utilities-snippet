# utilities-snippet
random snippets

# Windows Shortcut
------------------
**Screenshorts**:
- Greenshot : Last region -> Shift + PrtScn

# Git snippets
--------------
```
git config --global credential.helper store
```

# Powershell shortcut alias
---------------------------
Open Admin Powershell.
Create PROFILE:
```
code $PROFILE
```
Copy & Paste this -> then save: 
```
function Run-UnfoldScript {
    python C:\Users\quocd\Coding\unfold_claude\script.py
}

New-Alias -Name unfold -Value Run-UnfoldScript
```
Then,
```
. $PROFILE
```
Enable running script : 
```
Set-ExecutionPolicy RemoteSigned
```


_*Option Delete:*_
```
Remove-Item -Path Alias:unfold
```
# Find path to a python library
-------------------------
```python 
import sys

# First, ensure the library is available (you can replace 'numpy' with the library you're interested in)
library_name = 'langchain_experimental.tabular_synthetic_data.base'

if library_name in sys.modules:
    # If the library is already imported, find its path
    print(sys.modules[library_name].__file__)
else:
    # If not imported, import it and then find its path
    import importlib
    library = importlib.import_module(library_name)
    print(library.__file__)
```


# Google Drive download:
-----------------------
1. Curl Wget Extension: https://chromewebstore.google.com/detail/curlwget/dgcfkhmmpcmkikfmonjcalnjcmjcjjdn

2. Click download in the local browser

3. Click to get Wget link

# HuggingFace Login Notebook
-----------------------
```
from huggingface_hub import notebook_login
notebook_login()
```
# Clone HF model to local
-----------------------
```
apt-get install lfs-git
git init   
git lfs install   
git clone <https://huggingface.co/meta-llama/Llama-2-7b-chat-hf>
```
#Bash Utilities
---------------
```
# storage check
du -sh
```

# SSH
-----------------
It is required that your private key files are NOT accessible by others.

```
cp .ssh to ~/.ssh
chmod 600
```

# SSH - Auto install Vscode extension Remote
--------------------------------------------
https://stackoverflow.com/questions/70380724/vscode-remote-ssh-how-to-automatically-install-extensions
```
PS C:\Users\quocd> code --list-extensions
```

```
    "remote.SSH.defaultExtensions": [
        "github.copilot",
        "github.copilot-chat",
        "ms-python.debugpy",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "ms-toolsai.jupyter-keymap",
        "ms-toolsai.jupyter-renderers",
        "ms-toolsai.vscode-jupyter-cell-tags",
        "ms-toolsai.vscode-jupyter-slideshow",
        "vscodevim.vim",
    ],
```

# Newly installed Windows
-------------------------
App to install :
- Use Edge instead of Chrome
- Driver Booster (search serail key on youtube comment, don't download patch -> 
 virus)
- Buy a good Mouse (important for productivity)
- Wox (quick, custom search) https://www.youtube.com/watch?v=USFf2CCJEMg&ab_channel=TobieBi%E1%BA%BFtTu%E1%BB%91t
- Install WSL Ubuntu (Microsoft Store)
- Obsidian

**Good extensions**:
- Tab suspender (multi-tabs RAM optimal) 
- Winscribe (VPN)
- Dark reader
- Ads block
- Youtube Adblock
- Edge Translate

**Use Winget to install software :**  
```
winget install foxit 
winget install dropbox.dropbox 
winget install vim.vim
winget install git.git
```

**Activate script running .ps1**
(Powershell admin)
```
set-executionpolicy RemoteSigned
```

# WSL fix bugs
--------------
```
Installing, this may take a few minutes...
WslRegisterDistribution failed with error: 0x800701bc
Error: 0x800701bc WSL 2 requires an update to its kernel component. For information please visit https://aka.ms/wsl2kernel

Press any key to continue...
```
1. Search : Windows features ON/OFF
2. Enable VM, WSL
3. Restart
4. wsl.exe --update
5. Open Ubuntu WSL again => good
6.

```
sudo apt-get update && sudo apt-get upgrade
```

# WSL newly installed
---------------------
```
sudo apt-get update & sudo apt-get upgrade -y
#sudo apt install nodejs npm -y
cd
git clone https://github.com/karlin/mintty-colors-solarized.git
mv mintty-colors-solarized/ .mintty-colors-solarized/
wget https://raw.githubusercontent.com/seebi/dircolors-solarized/master/dircolors.256dark
mv dircolors.256dark .dir_colors
```
(Remember to Enter for the next command)
```
sudo apt-add-repository ppa:fish-shell/release-2
```
```
sudo apt-get update
sudo apt-get install -y fish

cat << 'EOF' >> ~/.bashrc

# Launch Fish
if [ -t 1 ]; then
  exec fish
fi

EOF

cat << 'EOF' >> ~/.config/fish/conf.d/omf.fish

# Set up colors
source ~/.mintty-colors-solarized/mintty-solarized-light.sh
eval (dircolors -c ~/.dir_colors | sed 's/>&\/dev\/null$//')

# Aliases
alias night "source ~/.mintty-colors-solarized/mintty-solarized-dark.sh"
alias day "source ~/.mintty-colors-solarized/mintty-solarized-light.sh"
EOF
```

```
curl -L http://get.oh-my.fish | fish

omf install pure
```

- Change cursor to Box:
![image](https://github.com/user-attachments/assets/d1990e5c-e131-4416-828b-4fad959c9fd2)

Final step: restart the WSL

# Vim Configuration
-------------------
1. Install `:PlugInstall`:
```
sudo apt  install cmake -y
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```
2. Open config .vimrc , paste the content of this file to it
```
vim ~/.vimrc
```
[https://github.com/quocdat-le-insacvl/mydotfiles/blob/master/.vimrc](https://github.com/quocdat-le-insacvl/mydotfiles/blob/master/.vimrc)

3. Type in (in vim),
Make changes
```
:source $MYVIMRC
```
Install
```
:PlugInstall
```





