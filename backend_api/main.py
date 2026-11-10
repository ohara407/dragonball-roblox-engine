"""
Servidor REST FastAPI de Integração Roblox <-> Python para Dragon Ball.
Fornece endpoints para:
- Carregamento e sincronização de dados de jogadores
- Treinamento em tempo real (Flexões, Meditação, Sala do Tempo, Gravidade)
- Ativação, drenagem e reversão de Transformações (SSJ 1-3, God, Blue, Ultra Instinct/Ego)
- Sistema de Missões e Sagas
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Garante importações relativas
sys.path.append(os.path.dirname(__file__))

from models import (
    PlayerStats, TrainRequest, TransformRequest,
    CompleteQuestRequest, ApiResponse
)
from database import init_db, get_or_create_player, save_player, get_player
from engine import (
    TRANSFORMATIONS_CATALOG, QUESTS_CATALOG,
    process_training, transform_player, revert_transformation,
    drain_ki_tick, charge_ki, apply_zenkai_boost, recalculate_power_level
)

app = FastAPI(
    title="Dragon Ball Roblox Backend API",
    description="API Python integrada ao Roblox para controle de status, treinamento, transformações e missões.",
    version="1.0.0"
)

# Habilita CORS caso o cliente ou painéis externos acessem a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Inicializa a base de dados SQLite ao subir o servidor."""
    init_db()
    print(">>> Servidor Dragon Ball Backend inicializado com sucesso!")
    print(">>> Banco de dados SQLite pronto para conexões do Roblox.")

@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "service": "Dragon Ball Roblox Engine",
        "message": "Servidor backend de combate e progressão ativo."
    }

# ==============================================================================
# ROTAS DO JOGADOR
# ==============================================================================

@app.get("/api/player/{user_id}", response_model=PlayerStats, tags=["Player"])
def get_player_data(user_id: int, username: str = "SaiyanWarrior"):
    """Retorna os dados do jogador ou cria um novo Saiyajin padrão se for novo."""
    player = get_or_create_player(user_id, username)
    player.power_level = recalculate_power_level(player)
    return player

@app.post("/api/player/{user_id}/charge_ki", response_model=ApiResponse, tags=["Player"])
def charge_player_ki(user_id: int, amount: float = 30.0):
    """Carrega o Ki do jogador (chamado quando o jogador segura a tecla de carga no Roblox)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player = charge_ki(player, amount)
    save_player(player)
    return ApiResponse(success=True, message=f"Ki carregado: {player.ki:.1f}/{player.max_ki:.1f}", player=player)

@app.post("/api/player/{user_id}/zenkai", response_model=ApiResponse, tags=["Player"])
def trigger_zenkai(user_id: int):
    """Aciona o bônus Zenkai quando o jogador sobrevive com vida crítica (< 10%)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player, boost = apply_zenkai_boost(player)
    save_player(player)
    return ApiResponse(
        success=True,
        message=f"Zenkai Boost ativado! Ganho de +{boost} em atributos permanentes.",
        player=player
    )

# ==============================================================================
# ROTAS DE TREINAMENTO
# ==============================================================================

@app.post("/api/player/{user_id}/train", response_model=ApiResponse, tags=["Treinamento"])
def train(user_id: int, request: TrainRequest):
    """Processa o treino no jogo (flexões, meditação, gravidade, sala do tempo)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player, gains = process_training(player, request.training_type, request.duration_seconds)
    save_player(player)
    return ApiResponse(
        success=True,
        message=f"Treino '{request.training_type.value}' concluído!",
        player=player,
        extra_data={"gains": gains}
    )

# ==============================================================================
# ROTAS DE TRANSFORMAÇÃO
# ==============================================================================

@app.get("/api/transformations", tags=["Transformações"])
def list_transformations():
    """Retorna todas as transformações disponíveis com requisitos e multiplicadores."""
    return TRANSFORMATIONS_CATALOG

@app.post("/api/player/{user_id}/transform", response_model=ApiResponse, tags=["Transformações"])
def transform(user_id: int, request: TransformRequest):
    """Tenta ativar uma transformação (ex: Kaioken, SSJ1, SSJ2, SSJ3, God, Blue, UI, Ultra Ego)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    success, msg, trans = transform_player(player, request.transformation_id)
    if not success:
        return ApiResponse(success=False, message=msg, player=player)
    
    save_player(player)
    extra = trans.dict() if hasattr(trans, "dict") else trans.model_dump()
    return ApiResponse(success=True, message=msg, player=player, extra_data={"transformation": extra})

@app.post("/api/player/{user_id}/revert", response_model=ApiResponse, tags=["Transformações"])
def revert(user_id: int):
    """Reverte o jogador para a sua forma base (desativa a transformação)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player = revert_transformation(player)
    save_player(player)
    return ApiResponse(success=True, message="Forma base restaurada.", player=player)

@app.post("/api/player/{user_id}/drain_tick", response_model=ApiResponse, tags=["Transformações"])
def drain_tick(user_id: int, delta_time: float = 1.0):
    """Loop de drenagem de Ki enviado pelo servidor Roblox a cada segundo de transformação."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player, reverted = drain_ki_tick(player, delta_time)
    save_player(player)
    msg = "Ki esgotado! Revertido para a forma base." if reverted else f"Ki restante: {player.ki:.1f}"
    return ApiResponse(success=True, message=msg, player=player, extra_data={"reverted": reverted})

# ==============================================================================
# ROTAS DE MISSÕES E SAGAS
# ==============================================================================

@app.get("/api/quests", tags=["Missões"])
def list_quests():
    """Retorna a lista completa de missões e sagas de Dragon Ball."""
    return QUESTS_CATALOG

@app.post("/api/player/{user_id}/complete_quest", response_model=ApiResponse, tags=["Missões"])
def complete_quest(user_id: int, request: CompleteQuestRequest):
    """Completa uma missão no servidor Roblox, concedendo XP, Zeni e novas transformações."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    if request.quest_id not in QUESTS_CATALOG:
        raise HTTPException(status_code=404, detail="Missão inexistente.")
    
    quest = QUESTS_CATALOG[request.quest_id]
    
    if request.quest_id in player.completed_quests:
        return ApiResponse(success=False, message="Missão já foi concluída anteriormente.", player=player)
    
    # Valida poder mínimo da missão
    if player.power_level < quest.power_level_req:
        return ApiResponse(
            success=False,
            message=f"Poder insuficiente para vencer {quest.target_enemy}! Requer {quest.power_level_req:,}.",
            player=player
        )
    
    # Registra conclusão e entrega recompensas
    player.completed_quests.append(request.quest_id)
    player.exp += quest.reward_exp
    player.zeni += quest.reward_zeni
    
    unlocked_msg = ""
    if quest.reward_form and quest.reward_form not in player.unlocked_transformations:
        player.unlocked_transformations.append(quest.reward_form)
        form_name = TRANSFORMATIONS_CATALOG[quest.reward_form].name
        unlocked_msg = f" ★ NOVA TRANSFORMAÇÃO DESBLOQUEADA: {form_name}! ★"

    player.power_level = recalculate_power_level(player)
    save_player(player)
    
    return ApiResponse(
        success=True,
        message=f"Missão '{quest.title}' concluída com sucesso! +{quest.reward_exp} EXP, +{quest.reward_zeni} Zeni.{unlocked_msg}",
        player=player
    )

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
