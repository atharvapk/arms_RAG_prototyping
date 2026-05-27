cmd + shift + p
select interpreter
create venv - select python 3.12.10

Install ollama model: llama3.1

macOS: source .venv/bin/activate
pip install 'vanna[ollama, chromadb]'
pip install pandas
pip install pdfplumber
pip install flask

check:
which python
which pip

change wd:
cd ARMS_Co-design_Phase1

demo video
https://drive.google.com/file/d/1XXKl4vG1p2seIUcdOAXpDsX4TbkDxkWf/view?usp=drive_link