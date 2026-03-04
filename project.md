# 🛸 Directives for Building the project 

## 1. Executive summary & Core mission
**Project Name:**  multi-agent-pdf-digest
**Mission:** Aplicatia proceseaza documente PDF incarcate de user, cu ajutorul Agentilor AI, conform instructiunilor, verifica acuratetea informatiilor si genereaza raport. In desfasurarea procesului Agentii se vor folosi de tools, mcp si skills.

## 2. Project description 
**Project structure**
multi-agent-pdf-digest/
├── user/
│   ├── upload_file.py
├── agents/
│   ├── formatter/
│   │   ├── __init__.py
│   │   ├── formatter_agent.py
│   │   ├── skills/
|   |   ├── tools/
│   │   └── requirements.txt
│   ├── summarizer/
│   │   ├── __init__.py
│   │   ├── summarizer_agent.py
│   │   ├── skills/
|   |   ├── tools/
│   │   └── requirements.txt
│   ├── differ/
│   │   ├── __init__.py
│   │   ├── differ_agent.py
│   │   ├── skills/
|   |   ├── tools/
│   │   └── requirements.txt
│   ├── analyser/
│   │   ├── __init__.py
│   │   ├──  analyser_agent.py
│   │   ├── skills/
|   |   ├── tools/
│   │   └── requirements.txt
│   ├── reporter/
│   │   ├── __init__.py
│   │   ├──  reporter_agent.py
│   │   ├── skills/
|   |   ├── tools/
│   │   └── requirements.txt
├── data/
│   └── input/          # Your raw files go here
├── output/              # The final digest appears here
├── tests/               # Unit and integration tests
├── .env                 # API keys (gitignored!)
├── .gitignore
└── README.md

**Prerequisites and Environment Setup**
You need the following tools installed before starting:
    - Python 3.10 or higher — the language for the agents
    - OpenAI Python SDK (openai >= 1.0) — LLM API access

**Inputuri**
    - se vor incarca urmatoarele documente:
        - memoriu.pdf
        - formular_initial.pdf
        - formular_modificat.pdf
**Procesul proiectului:** 
    - userul incarca documentele format .pdf in folderul /data/input folosind upload_files.py
    - documentele sunt convertite, by the The Formater Agent in format .md (Markdown) folosind libraria Docling (sau echivalent). In cazul in care se foloseste Docling, Docling se va conecta remote la Kaggle pe care ruleaza  vLLM sau OMALLA folosind OpenAI Python SDK si ngrok (sau echivalent). Dupa conversie documentele memoriu.md, formular_initial.md si formular_modificat.md sunt salvate in folderul /data/output. The Formater Agent se va folosi de skills, tools sau/si mcp.
    - The Differ Agent va compara fisierele formular_initial.md si formular_modificat.md folosind libraria difflib (sau echivalent). Diferentele se vor salva in /data/output/differs.md pentru a fi folosite ulterior de The Analyser Agent.
    - The Summarizer Agent va citi fisierul memoriu.md, and calls an LLM API (Kaggle pe care ruleaza  vLLM sau OMALLA) to produce a concise summary.md in folderul /data/output.  The Summarizer Agent se va folosi de skills, tools sau/si mcp.
    - The Analyser Agent va analiza fisierele summary.md, differs.md sa verifice daca toate cerintele din summary.md sunt respectate si reflectate in differs.md viceversa. Apoi va genera un raport in format .md (Markdown) in care vor fi mentionate  detaliat toate cerintele din summary.md si reflectate in differs.md viceversa. Raportul va fi salvat in folderul /data/output. The Analyser Agent se va folosi de skills, tools sau/si mcp.
    - The Reporter Agent va citi fisierul raport.md si va genera un raport in format .pdf (PDF) in folderul /data/output. The Reporter Agent se va folosi de skills, tools sau/si mcp.
