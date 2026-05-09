# Transparência solidária
- Portal foi pensado para que entidades beneficentes cadastrem itens necessários, divulguem estoques atuais e níveis ideais, enquanto doadores consultam essas informações de forma prática e objetiva.


## Para rodar o projeto como desenvolvedor:
1. Instale uma versão de python (preferencialmente >= 3.13, < 4.0);
2. Instale o `pipx`:
```bash
pip install pipx
```
3. Instale o `poetry` usando o `pipx`:
```bash
pipx install poetry
```
4. Instale a aplicação:
```bash
poetry install
```
5. Crie um arquivo `.env` na raiz do projeto contendo as seguintes variáveis de ambiente:
```
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```
6. Instale o banco de dados [postgre](https://www.postgresql.org/download/).
7. Rode a aplicação:
```bash
poetry run fastapi dev main.py
```
