# 🧰 Project Template Toolkit

Um gerenciador de templates de projeto em Python e CustomTkinter. Esta ferramenta permite exportar a estrutura de um projeto existente como um template e, em seguida, usar esse template para criar um novo esqueleto de projeto.

Ela foi criada para fundir duas necessidades:
1.  **Exportar projetos** para análise de IAs (gerando um `.md` consolidado).
2.  **Criar novos projetos** a partir de uma estrutura pré-definida (gerando as pastas e arquivos).

---

## ✨ Funcionalidades

O "Gerenciador de Templates" opera em dois modos:

### 1. Modo "Exportar Template"
Baseado em um projeto existente, esta função analisa toda a estrutura de pastas e arquivos e gera dois artefatos:

* **Arquivo de Template (`.txt`):** Uma árvore de diretórios limpa (ex: `meu_projeto_template.txt`), ignorando pastas desnecessárias como `venv`, `node_modules`, `__pycache__`, etc.
* **Arquivo de IA (`.md`):** Um arquivo Markdown completo contendo a árvore de diretórios E todo o conteúdo dos arquivos de código, ideal para enviar para IAs como ChatGPT ou Claude.

### 2. Modo "Criar por Template"
Usando um arquivo de template (`.txt`) — como o gerado pelo modo de exportação — esta função recria toda a estrutura de pastas e arquivos vazios em um diretório de destino.

É perfeito para iniciar novos projetos rapidamente com seu "esqueleto" de pastas preferido.

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
    .\venv\Scripts\activate
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

Um executável `.exe` pré-compilado pode ser encontrado na seção [Releases](https://github.com/SEU-USUARIO/SEU-REPO/releases) deste repositório.

*(Nota: Você precisará subir o seu `.exe` manualmente para a seção "Releases" do seu GitHub para que este link funcione)*

---

## 🌟 Créditos e Agradecimentos

Este projeto foi uma fusão de duas ferramentas:

* **Analisador/Criador de Estrutura:** A lógica para ler um template `.txt` e criar a estrutura de pastas.
* **Consolidador de Projeto:** A lógica principal de análise de projeto, filtros inteligentes (perfis) e exportação do código-fonte para Markdown foi baseada e adaptada do incrível trabalho do **@ezequielvinicius**.
