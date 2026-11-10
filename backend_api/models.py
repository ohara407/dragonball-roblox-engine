"""
Modelos de dados (Pydantic) para o Backend Python do jogo Dragon Ball no Roblox.
"""
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class TrainingType(str, Enum):
    PUSHUPS = "pushups"                  # Aumenta Força e Defesa
    SHADOW_BOXING = "shadow_boxing"      # Aumenta Agilidade e Ki
    MEDITATION = "meditation"            # Aumenta Max Ki e Controle de Ki
    GRAVITY_CHAMBER = "gravity_chamber"  # Multiplicador alto de todos os stats
    HYPERBOLIC_TIME = "hyperbolic_time"  # Sala do Tempo: ganho massivo com cooldown

class Transformation(BaseModel):
    id: str
    name: str
    multiplier: float
    ki_drain_per_sec: float
    min_power_level: int
    required_quest_id: Optional[str] = None
    aura_color: str  # Hex RGB (ex: "#FFD700" para Dourado SSJ)
    hair_color: Optional[str] = None
    description: str

class Quest(BaseModel):
    id: str
    title: str
    description: str
    saga: str
    target_enemy: str
    target_count: int = 1
    power_level_req: int
    reward_exp: int
    reward_zeni: int
    reward_form: Optional[str] = None

class PlayerStats(BaseModel):
    user_id: int
    username: str
    power_level: int = 100
    level: int = 1
    exp: int = 0
    exp_next: int = 500
    zeni: int = 100
    
    # Atributos Base
    health: float = 1000.0
    max_health: float = 1000.0
    ki: float = 500.0
    max_ki: float = 500.0
    strength: int = 20
    defense: int = 20
    agility: int = 20
    
    # Estados de Transformação
    current_transformation: Optional[str] = None
    unlocked_transformations: List[str] = Field(default_factory=lambda: ["kaioken"])
    
    # Sistema de Quests
    completed_quests: List[str] = Field(default_factory=list)
    active_quests: List[str] = Field(default_factory=lambda: ["quest_raditz"])
    
    # Multiplicador de Linhagem Saiyajin
    zenkai_count: int = 0

class TrainRequest(BaseModel):
    training_type: TrainingType
    duration_seconds: int = 5

class TransformRequest(BaseModel):
    transformation_id: str

class CompleteQuestRequest(BaseModel):
    quest_id: str

class ApiResponse(BaseModel):
    success: bool
    message: str
    player: Optional[PlayerStats] = None
    extra_data: Optional[Dict] = None
