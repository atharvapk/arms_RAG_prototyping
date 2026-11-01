### Blurb:
To be fair, this a very rudimentary demo we produced to showcase scripts exploring systems of agents. The point of these was to setup auxiliary agents to perform checks and align progress on the project - feedback loop style.

In the videos below, agents programmatically extract details off the model and parse for relevant information through SQL + RAG to enforce verifiable manufacturing decision-making constraints. I feel like these kinds of agent applications will be a core part of autonomous processes for many of our tasks.

### Demo Videos:
**Color Extraction**

https://github.com/user-attachments/assets/77bca347-87e9-4de3-800d-68b39c46f835

https://drive.google.com/file/d/1XXKl4vG1p2seIUcdOAXpDsX4TbkDxkWf/view?usp=drive_link

**MBD Dimensioning**

https://github.com/user-attachments/assets/45de032b-0560-47ac-bec0-49c37eaa17cf

https://drive.google.com/file/d/1megNsks5UEWhEl-1jWSNBh-c3ln6weGP/view?usp=share_link

### IDE Setup:
cmd + shift + p
select interpreter
create venv - select python 3.12.10

### Terminal Setup
check:
which python
which pip
change wd:
cd ARMS_Co-design_Phase1

### Packages
macOS: source .venv/bin/activate
pip install 'vanna[ollama, chromadb]'
pip install pandas
pip install pdfplumber
pip install flask

### LLM
Install ollama model: llama3.1
