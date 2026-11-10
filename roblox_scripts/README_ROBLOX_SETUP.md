# 🛠️ Guia de Configuração: Dragon Ball Roblox + Python

Este guia explica passo a passo como configurar o **Roblox Studio** para se comunicar com o servidor **Python (FastAPI)**.

---

## 1. Ativar Requisições HTTP no Roblox Studio (Obrigatório!)
Por padrão de segurança, o Roblox desativa chamadas para servidores externos. Para ativar:
1. Abra seu jogo no **Roblox Studio**.
2. Na barra superior (Menu), clique em **Home** (Início) -> **Game Settings** (Configurações do Jogo).
   *(Se o jogo for novo, salve-o no Roblox primeiro para liberar a opção).*
3. No menu lateral, clique na aba **Security** (Segurança).
4. Ative a chave: **Allow HTTP Requests** (Permitir Requisições HTTP).
5. Clique em **Save** (Salvar).

---

## 2. Instalar os Scripts no Roblox Studio

### A) Scripts do Servidor (`ServerScriptService`)
1. No painel **Explorer**, localize a pasta `ServerScriptService`.
2. Clique no ícone `+` ao lado de `ServerScriptService` e adicione um **Script** tradicional (Script de Servidor).
3. Renomeie o script para `DragonBallBackendBridge`.
4. Copie todo o conteúdo do arquivo:
   `dragonball_roblox/roblox_scripts/ServerScriptService/DragonBallBackendBridge.server.luau`
   e cole dentro dele.
5. Adicione um segundo **Script** dentro de `ServerScriptService`, renomeie para `TransformationVFXServer`, e cole o conteúdo de:
   `dragonball_roblox/roblox_scripts/ServerScriptService/TransformationVFXServer.server.luau`.

### B) Scripts do Cliente (`StarterPlayerScripts`)
1. No painel **Explorer**, abra a pasta `StarterPlayer`.
2. Dentro dela, localize a pasta `StarterPlayerScripts`.
3. Clique no `+` e adicione um **LocalScript** (Script Local).
4. Renomeie para `DragonBallClientController`.
5. Copie todo o conteúdo de:
   `dragonball_roblox/roblox_scripts/StarterPlayer/StarterPlayerScripts/DragonBallClientController.client.luau`
   e cole dentro dele.

---

## 3. Como Rodar o Servidor Python

1. Abra um terminal na pasta do backend:
   ```bash
   cd c:\Users\Aluno\Documents\Estudopython\dragonball_roblox\backend_api
   ```
2. Instale as dependências (se ainda não tiver instalado):
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor FastAPI:
   ```bash
   python main.py
   ```
   *O servidor iniciará em `http://127.0.0.1:8000` e criará o banco `dragonball_game.db` automaticamente.*
4. Você pode ver a documentação interativa Swagger de todas as rotas no navegador em:
   `http://127.0.0.1:8000/docs`

---

## 4. Testando o Jogo no Roblox Studio
1. Com o Python rodando, clique em **Play** (Jogar) no Roblox Studio.
2. Você verá o HUD no canto inferior esquerdo com:
   - **PODER DE LUTA**
   - **BARRA DE VIDA**
   - **BARRA DE KI**
3. Pressione as teclas de comando:
   - **[T]**: Realiza treino rápido (aumenta Força, Defesa e Poder de Luta sincronizados com o Python).
   - **[C] (segurar)**: Carrega a barra de Ki.
   - **[G]**: Ativa a transformação (Aura de partículas coloridas e aumento de velocidade).
   - **[H]**: Desativa a transformação e volta à forma base.
