"""
Servidor REST FastAPI de Integração Roblox <-> Python para Dragon Ball.
Fornece endpoints para:
- Carregamento e sincronização de dados de jogadores
- Treinamento em tempo real (Flexões, Meditação, Sala do Tempo, Gravidade)
- Ativação, drenagem e reversão de Transformações (SSJ 1-3, God, Blue, Ultra Instinct/Ego)
- Sistema de Missões e Sagas
- Sistema de Golpes Especiais e Habilidades (Kamehameha, Genki Dama, etc.)
- Sistema de Loja, Itens e Inventário (Senzu Beans, Armaduras, Scouter)
- Integração de IA Google Gemini (Roteiros de Animação VFX, Diálogos de Chefes, Missões Diárias)
"""
import os
import sys
from typing import Optional, Dict
from pydantic import BaseModel
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
from skills import (
    SKILL_CATALOG, PlayerSkillSet,
    learn_skill, use_skill, get_player_skillset
)
from shop import (
    ITEM_CATALOG, Inventory,
    buy_item, use_item, get_inventory, get_shop_catalog
)
from gemini_ai import GeminiAIEngine

# Instancia o motor de IA do Google
ai_engine = GeminiAIEngine()

app = FastAPI(
    title="Dragon Ball Roblox Backend API",
    description="API Python integrada ao Roblox para controle de status, treinamento, transformações, combate, loja e IA.",
    version="1.2.0"
)

# Habilita CORS para requisições externas ou painéis
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
    print(">>> Módulos carregados: Player, Combat, Skills, Shop, Gemini AI.")

@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "service": "Dragon Ball Roblox Engine",
        "version": "1.2.0",
        "features": [
            "Player & Stats Engine",
            "8 Super Saiyan Transformations",
            "15 Iconic Combat Skills",
            "Zeni Shop & Inventory",
            "Google Gemini AI Generative VFX & Dialogues",
            "Roblox HttpService Bridge"
        ]
    }

# ==============================================================================
# MODELOS DE REQUISIÇÃO AUXILIARES
# ==============================================================================

class LearnSkillRequest(BaseModel):
    skill_id: str

class UseSkillRequest(BaseModel):
    skill_id: str
    target_defense: int = 50
    target_power: int = 1000

class BuyItemRequest(BaseModel):
    item_id: str
    quantity: int = 1

class UseItemRequest(BaseModel):
    item_id: str

class AnimationAIRequest(BaseModel):
    skill_or_form: str

class BossDialogueAIRequest(BaseModel):
    boss_name: str
    player_power: int
    boss_power: int
    situation: str

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
    """Carrega o Ki do jogador (chamado quando o jogador segura a tecla [C] no Roblox)."""
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
    
    if player.power_level < quest.power_level_req:
        return ApiResponse(
            success=False,
            message=f"Poder insuficiente para vencer {quest.target_enemy}! Requer {quest.power_level_req:,}.",
            player=player
        )
    
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

# ==============================================================================
# ROTAS DE GOLPES ESPECIAIS (SKILLS)
# ==============================================================================

@app.get("/api/skills", tags=["Habilidades"])
def list_skills():
    """Retorna todos os 15 golpes especiais com danos, custos de Ki e requisitos."""
    return SKILL_CATALOG

@app.get("/api/player/{user_id}/skills", response_model=PlayerSkillSet, tags=["Habilidades"])
def get_skills_route(user_id: int):
    """Retorna o conjunto de golpes aprendidos pelo jogador."""
    return get_player_skillset(user_id)

@app.post("/api/player/{user_id}/skills/learn", response_model=ApiResponse, tags=["Habilidades"])
def learn_skill_route(user_id: int, request: LearnSkillRequest):
    """Aprende uma nova habilidade caso atenda aos requisitos de nível e saga."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    success, msg, skill = learn_skill(player, request.skill_id)
    return ApiResponse(success=success, message=msg, player=player)

@app.post("/api/player/{user_id}/skills/use", response_model=ApiResponse, tags=["Habilidades"])
def use_skill_route(user_id: int, request: UseSkillRequest):
    """Executa um golpe especial, deduzindo Ki e calculando o dano de combate."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    success, msg, result = use_skill(player, request.skill_id, request.target_defense, request.target_power)
    if success:
        save_player(player)
    return ApiResponse(success=success, message=msg, player=player, extra_data=result)

# ==============================================================================
# ROTAS DE LOJA E INVENTÁRIO
# ==============================================================================

@app.get("/api/shop/catalog", tags=["Loja & Inventário"])
def get_catalog():
    """Retorna todos os itens disponíveis na loja com preços em Zeni."""
    return get_shop_catalog()

@app.get("/api/player/{user_id}/inventory", response_model=Inventory, tags=["Loja & Inventário"])
def get_player_inventory(user_id: int):
    """Retorna o inventário de itens do jogador."""
    return get_inventory(user_id)

@app.post("/api/player/{user_id}/shop/buy", response_model=ApiResponse, tags=["Loja & Inventário"])
def buy_item_route(user_id: int, request: BuyItemRequest):
    """Compra um item na loja debitando Zeni da conta do jogador."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    success, msg, inv = buy_item(player, request.item_id, request.quantity)
    if success:
        save_player(player)
    return ApiResponse(success=success, message=msg, player=player, extra_data={"inventory": inv.model_dump() if hasattr(inv, "model_dump") else inv.dict()})

@app.post("/api/player/{user_id}/inventory/use", response_model=ApiResponse, tags=["Loja & Inventário"])
def use_item_route(user_id: int, request: UseItemRequest):
    """Consome ou equipa um item do inventário (ex: Senzu Bean restaura 100% HP/Ki)."""
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    success, msg, extra = use_item(player, request.item_id)
    if success:
        save_player(player)
    return ApiResponse(success=success, message=msg, player=player, extra_data=extra)

# ==============================================================================
# ROTAS DE IA GENERATIVA (GOOGLE GEMINI)
# ==============================================================================

@app.post("/api/ai/animation_specs", tags=["Google Gemini AI"])
def generate_animation_specs(request: AnimationAIRequest):
    """Gera o design técnico de animações, keyframes e partículas VFX no Roblox com IA."""
    result = ai_engine.generate_animation_script(request.skill_or_form)
    return result

@app.post("/api/ai/boss_dialogue", tags=["Google Gemini AI"])
def generate_boss_dialogue(request: BossDialogueAIRequest):
    """Gera falas dinâmicas e dramáticas de chefes de saga baseadas no poder do jogador."""
    dialogue = ai_engine.generate_boss_dialogue(
        request.boss_name,
        request.player_power,
        request.boss_power,
        request.situation
    )
    return {"boss_name": request.boss_name, "dialogue": dialogue}

@app.get("/api/ai/daily_quest", tags=["Google Gemini AI"])
def generate_daily_quest(level: int = 1, form: str = "Forma Base"):
    """Gera uma missão procedural personalizada com o auxílio do Gemini 1.5 Flash."""
    quest = ai_engine.generate_daily_quest(level, form)
    return quest


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
