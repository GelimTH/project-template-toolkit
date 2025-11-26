# 🧰 Project Template Toolkit

Um gerenciador de templates e analisador de projetos em Python e CustomTkinter. Esta ferramenta é um "canivete suíço" para desenvolvedores, permitindo exportar estruturas, criar novos projetos e analisar códigos existentes.

Ela foi criada para atender três necessidades principais:
1.  **Exportar projetos** para análise de IAs (gerando um `.md` consolidado).
2.  **Criar novos projetos** a partir de uma estrutura pré-definida.
3.  **Engenharia Reversa (Sherlock)** para descobrir requisitos de backend a partir de um frontend.

---

## ✨ Funcionalidades

O "ToolKitDev" opera em três modos distintos:

### 1. Modo "Exportar Template"
Baseado em um projeto existente, esta função analisa toda a estrutura de pastas e arquivos e gera dois artefatos:

* **Arquivo de Template (`.txt`):** Uma árvore de diretórios limpa, ignorando pastas desnecessárias como `venv`, `node_modules`, `__pycache__`, etc.
* **Arquivo de Contexto IA (`.md`):** Um arquivo Markdown completo contendo a árvore de diretórios E todo o conteúdo dos arquivos de código, ideal para enviar para IAs como ChatGPT, Claude ou Gemini para análise ou refatoração.

### 2. Modo "Criar por Template"
Usando um arquivo de template (`.txt`) — como o gerado pelo modo de exportação ou criado manualmente — esta função recria toda a estrutura de pastas e arquivos vazios em um diretório de destino.

É perfeito para iniciar novos projetos rapidamente com seu "esqueleto" de pastas preferido.

### 3. Modo "Scanner (Sherlock)" 🕵️
Uma ferramenta de **análise estática** projetada para quem precisa criar o Backend de um projeto que só tem o Frontend pronto.

Aponte para a pasta `src` de um projeto (React, JS, etc.) e o Sherlock irá varrer o código procurando por pistas:
* **Rotas de API:** Identifica chamadas HTTP (ex: `axios.post('/login')`, `api.get('/eventos')`) e gera uma lista de endpoints que você precisa criar.
* **Modelos de Dados:** Infere entidades e campos (ex: ao encontrar `user.email` e `user.role`, ele sugere a criação de uma tabela `User` com essas colunas).

---

## 🛠️ Como Rodar (do Código-Fonte)

Se você não quiser usar o executável, pode rodar o projeto manualmente:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/SEU-REPO.git](https://github.com/SEU-USUARIO/SEU-REPO.git)
    cd SEU-REPO
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install customtkinter
    ```

4.  **Execute o script:**
    ```bash
    python project_toolkit_v2.py
    ```

---

## 📦 Executável (Windows)

Um executável `.exe` pré-compilado pode ser encontrado na seção [Releases](https://github.com/GelimTH/project-template-toolkit/releases) deste repositório.

---

## 🌟 Créditos e Agradecimentos

Este projeto é uma fusão de ferramentas poderosas:

* **Analisador/Criador de Estrutura:** Lógica original para manipulação de templates de diretórios.
* **Consolidador de Projeto:** A lógica de exportação para Markdown e filtros inteligentes foi baseada e adaptada do trabalho do **@ezequielvinicius**.
* **Scanner Sherlock:** Módulo de engenharia reversa desenvolvido para facilitar a migração de protótipos frontend para aplicações Full Stack.