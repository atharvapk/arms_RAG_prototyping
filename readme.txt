cmd + shift + p
select interpreter
create venv - select python 3.12.10

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