"""
Motor de Lógica e Cálculos de Dragon Ball.
Contém regras de combate, multiplicadores de transformações, treinamento e sagas de quests.
"""
from typing import Dict, Optional, Tuple
from models import PlayerStats, Transformation, Quest, TrainingType

# ==============================================================================
# CATÁLOGO DE TRANSFORMAÇÕES
# ==============================================================================
TRANSFORMATIONS_CATALOG: Dict[str, Transformation] = {
    "kaioken": Transformation(
        id="kaioken",
        name="Kaioken x3",
        multiplier=1.5,
        ki_drain_per_sec=8.0,
        min_power_level=500,
        required_quest_id="quest_raditz",
        aura_color="#FF2222",
        hair_color=None,
        description="Aura carmesim intensa que aumenta o poder às custas de desgaste físico contínuo."
    ),
    "ssj1": Transformation(
        id="ssj1",
        name="Super Saiyajin 1",
        multiplier=50.0,
        ki_drain_per_sec=12.0,
        min_power_level=150000,
        required_quest_id="quest_freeza",
        aura_color="#FFD700",
        hair_color="#FFE600",
        description="A lendária forma dourada despertada pela fúria em Namekusei. Multiplica os atributos em 50x."
    ),
    "ssj2": Transformation(
        id="ssj2",
        name="Super Saiyajin 2",
        multiplier=100.0,
        ki_drain_per_sec=20.0,
        min_power_level=500000,
        required_quest_id="quest_cell",
        aura_color="#FFF066",
        hair_color="#FFF533",
        description="Poder além do Super Saiyajin, cercado por relâmpagos bioelétricos. Multiplica o poder em 100x."
    ),
    "ssj3": Transformation(
        id="ssj3",
        name="Super Saiyajin 3",
        multiplier=400.0,
        ki_drain_per_sec=45.0,
        min_power_level=2500000,
        required_quest_id="quest_majin_buu",
        aura_color="#FFC400",
        hair_color="#FFD700",
        description="Extrai cada gota de potencial latente do Saiyajin. Causa um consumo brutal de Ki."
    ),
    "ssj_god": Transformation(
        id="ssj_god",
        name="Super Saiyajin Deus (God)",
        multiplier=2000.0,
        ki_drain_per_sec=25.0,
        min_power_level=10000000,
        required_quest_id="quest_beerus",
        aura_color="#FF1A4B",
        hair_color="#FF1A4B",
        description="Ki divino que concede calma perfeita, regeneração acelerada e velocidade sobre-humana."
    ),
    "ssj_blue": Transformation(
        id="ssj_blue",
        name="Super Saiyajin Blue",
        multiplier=5000.0,
        ki_drain_per_sec=40.0,
        min_power_level=50000000,
        required_quest_id="quest_golden_freeza",
        aura_color="#00D4FF",
        hair_color="#00BFFF",
        description="A combinação do Super Saiyajin com o Ki dos Deuses. Força colossal e controle absoluto."
    ),
    "ultra_instinct": Transformation(
        id="ultra_instinct",
        name="Instinto Superior (Ultra Instinct)",
        multiplier=20000.0,
        ki_drain_per_sec=70.0,
        min_power_level=200000000,
        required_quest_id="quest_jiren",
        aura_color="#E0E6ED",
        hair_color="#C0C0C0",
        description="O ápice dos deuses e anjos. O corpo desvia e ataca sozinho sem pensar. Esquiva automática."
    ),
    "ultra_ego": Transformation(
        id="ultra_ego",
        name="Ultra Ego",
        multiplier=25000.0,
        ki_drain_per_sec=80.0,
        min_power_level=350000000,
        required_quest_id="quest_granola",
        aura_color="#8A2BE2",
        hair_color="#9932CC",
        description="O poder da destruição dos Deuses da Destruição (Hakaishin). Quanto mais dano recebe, mais forte fica."
    )
}

# ==============================================================================
# CATÁLOGO DE MISSÕES / SAGAS
# ==============================================================================
QUESTS_CATALOG: Dict[str, Quest] = {
    "quest_raditz": Quest(
        id="quest_raditz",
        title="Invasão Saiyajin: Derrote Raditz",
        description="Raditz chegou à Terra buscando seu irmão. Treine e expulse-o do planeta!",
        saga="Saga dos Saiyajins",
        target_enemy="Raditz",
        target_count=1,
        power_level_req=300,
        reward_exp=500,
        reward_zeni=1000,
        reward_form="kaioken"
    ),
    "quest_nappa": Quest(
        id="quest_nappa",
        title="O Gigante Nappa",
        description="Nappa destruiu a cidade e desafia os guerreiros Z. Prove seu treinamento de gravidade!",
        saga="Saga dos Saiyajins",
        target_enemy="Nappa",
        target_count=1,
        power_level_req=4000,
        reward_exp=2500,
        reward_zeni=5000
    ),
    "quest_vegeta": Quest(
        id="quest_vegeta",
        title="O Príncipe dos Saiyajins",
        description="Vegeta exige uma luta até o fim no deserto rochoso. Use o Kaioken com sabedoria!",
        saga="Saga dos Saiyajins",
        target_enemy="Vegeta",
        target_count=1,
        power_level_req=18000,
        reward_exp=8000,
        reward_zeni=15000
    ),
    "quest_freeza": Quest(
        id="quest_freeza",
        title="O Tirano Galáctico: Freeza 100%",
        description="Em Namekusei à beira da explosão, enfrente o imperador Freeza e desperte a fúria ancestral!",
        saga="Saga de Namekusei",
        target_enemy="Freeza Forma Final",
        target_count=1,
        power_level_req=120000,
        reward_exp=50000,
        reward_zeni=100000,
        reward_form="ssj1"
    ),
    "quest_cell": Quest(
        id="quest_cell",
        title="Os Jogos de Cell: O Guerreiro Perfeito",
        description="Cell ameaça explodir o Sistema Solar. Supere o limite do Super Saiyajin!",
        saga="Saga dos Androides",
        target_enemy="Perfect Cell",
        target_count=1,
        power_level_req=450000,
        reward_exp=200000,
        reward_zeni=300000,
        reward_form="ssj2"
    ),
    "quest_majin_buu": Quest(
        id="quest_majin_buu",
        title="O Monstro Ancestral: Kid Buu",
        description="Kid Buu ameaça a existência do universo. Libere o poder do SSJ3 ou use a Genki Dama!",
        saga="Saga de Majin Buu",
        target_enemy="Kid Buu",
        target_count=1,
        power_level_req=2000000,
        reward_exp=1000000,
        reward_zeni=1000000,
        reward_form="ssj3"
    ),
    "quest_beerus": Quest(
        id="quest_beerus",
        title="O Deus da Destruição: Lord Beerus",
        description="Beerus acordou procurando o Deus Super Saiyajin. Faça o ritual divino e mostre seu valor!",
        saga="Saga dos Deuses",
        target_enemy="Beerus",
        target_count=1,
        power_level_req=8000000,
        reward_exp=5000000,
        reward_zeni=5000000,
        reward_form="ssj_god"
    ),
    "quest_golden_freeza": Quest(
        id="quest_golden_freeza",
        title="O Renascimento do Ouro",
        description="Freeza ressuscitou e dominou sua nova forma dourada. Combine o Ki Divino com Super Saiyajin!",
        saga="Saga do Renascimento",
        target_enemy="Golden Freeza",
        target_count=1,
        power_level_req=40000000,
        reward_exp=15000000,
        reward_zeni=10000000,
        reward_form="ssj_blue"
    ),
    "quest_jiren": Quest(
        id="quest_jiren",
        title="Torneio do Poder: O Invencível Jiren",
        description="O destino do Universo 7 está em suas mãos. Quebre todas as barreiras mentais e alcance o Instinto Superior!",
        saga="Torneio do Poder",
        target_enemy="Jiren Limit Breaker",
        target_count=1,
        power_level_req=150000000,
        reward_exp=50000000,
        reward_zeni=50000000,
        reward_form="ultra_instinct"
    )
}

# ==============================================================================
# FÓRMULAS E MÉTODOS DE CÁLCULO
# ==============================================================================

def recalculate_power_level(player: PlayerStats) -> int:
    """Calcula o Poder de Luta Base = (Força * 10) + (Defesa * 8) + (Agilidade * 6) + (Max Ki * 2)"""
    base = int((player.strength * 10) + (player.defense * 8) + (player.agility * 6) + (player.max_ki * 2))
    
    # Aplica multiplicador da transformação ativa
    if player.current_transformation and player.current_transformation in TRANSFORMATIONS_CATALOG:
        trans = TRANSFORMATIONS_CATALOG[player.current_transformation]
        return int(base * trans.multiplier)
    
    return base

def process_training(player: PlayerStats, training_type: TrainingType, duration: int = 5) -> Tuple[PlayerStats, Dict]:
    """Processa uma sessão de treino e calcula os ganhos de atributos."""
    gains = {"strength": 0, "defense": 0, "agility": 0, "ki": 0.0, "max_ki": 0.0, "exp": 0}
    
    # Fator de tempo (min 1 seg, max 60 seg por ciclo)
    time_factor = max(1, min(duration, 60))
    
    if training_type == TrainingType.PUSHUPS:
        # Treino Físico (Força + Defesa)
        gains["strength"] = int(5 * time_factor)
        gains["defense"] = int(4 * time_factor)
        gains["exp"] = 25 * time_factor
    elif training_type == TrainingType.SHADOW_BOXING:
        # Treino de Combate (Agilidade + Ki)
        gains["agility"] = int(6 * time_factor)
        gains["max_ki"] = 5.0 * time_factor
        gains["exp"] = 30 * time_factor
    elif training_type == TrainingType.MEDITATION:
        # Meditação (Expansão de Ki e regeneração)
        gains["max_ki"] = 15.0 * time_factor
        gains["ki"] = 25.0 * time_factor
        gains["defense"] = int(2 * time_factor)
        gains["exp"] = 20 * time_factor
    elif training_type == TrainingType.GRAVITY_CHAMBER:
        # Sala de Gravidade (100G)
        gains["strength"] = int(12 * time_factor)
        gains["defense"] = int(10 * time_factor)
        gains["agility"] = int(10 * time_factor)
        gains["max_ki"] = 10.0 * time_factor
        gains["exp"] = 80 * time_factor
    elif training_type == TrainingType.HYPERBOLIC_TIME:
        # Sala do Tempo
        gains["strength"] = int(25 * time_factor)
        gains["defense"] = int(25 * time_factor)
        gains["agility"] = int(20 * time_factor)
        gains["max_ki"] = 30.0 * time_factor
        gains["exp"] = 200 * time_factor

    # Aplica os ganhos
    player.strength += gains["strength"]
    player.defense += gains["defense"]
    player.agility += gains["agility"]
    player.max_ki += gains["max_ki"]
    player.ki = min(player.max_ki, player.ki + gains["ki"])
    player.exp += gains["exp"]
    
    # Verifica Level Up
    while player.exp >= player.exp_next:
        player.exp -= player.exp_next
        player.level += 1
        player.exp_next = int(player.exp_next * 1.5)
        # Bônus por level
        player.max_health += 200.0
        player.health = player.max_health
        player.max_ki += 100.0
        player.strength += 10
        player.defense += 10
        player.agility += 10

    player.power_level = recalculate_power_level(player)
    return player, gains

def apply_zenkai_boost(player: PlayerStats) -> Tuple[PlayerStats, int]:
    """Zenkai Boost: Saiyajins ficam mais fortes ao sobreviver à beira da morte."""
    player.zenkai_count += 1
    # Aumenta atributos permanentemente em 15%
    str_gain = int(player.strength * 0.15)
    def_gain = int(player.defense * 0.15)
    agi_gain = int(player.agility * 0.15)
    ki_gain = player.max_ki * 0.15
    
    player.strength += str_gain
    player.defense += def_gain
    player.agility += agi_gain
    player.max_ki += ki_gain
    player.health = player.max_health
    player.ki = player.max_ki
    player.power_level = recalculate_power_level(player)
    
    total_boost = str_gain + def_gain + agi_gain
    return player, total_boost

def transform_player(player: PlayerStats, form_id: str) -> Tuple[bool, str, Optional[Transformation]]:
    """Tenta transformar o jogador na forma especificada."""
    if form_id not in TRANSFORMATIONS_CATALOG:
        return False, f"Forma '{form_id}' não existe no catálogo.", None
    
    trans = TRANSFORMATIONS_CATALOG[form_id]
    
    # Verifica se já está desbloqueada
    if form_id not in player.unlocked_transformations:
        # Verifica se atende aos requisitos para desbloqueio
        base_power = recalculate_power_level(player)
        if base_power < trans.min_power_level:
            return False, f"Poder de luta insuficiente. Necessário: {trans.min_power_level:,}, Atual: {base_power:,}", None
        
        if trans.required_quest_id and trans.required_quest_id not in player.completed_quests:
            return False, f"Missão necessária não concluída: '{trans.required_quest_id}'", None
            
        # Desbloqueia a forma
        player.unlocked_transformations.append(form_id)

    # Verifica Ki para ativar
    if player.ki < 50.0:
        return False, "Ki insuficiente para sustentar a transformação!", None
        
    player.current_transformation = form_id
    player.power_level = recalculate_power_level(player)
    return True, f"Transformação '{trans.name}' ativada com sucesso!", trans

def revert_transformation(player: PlayerStats) -> PlayerStats:
    """Reverte o jogador para a sua forma base."""
    player.current_transformation = None
    player.power_level = recalculate_power_level(player)
    return player

def drain_ki_tick(player: PlayerStats, delta_time: float = 1.0) -> Tuple[PlayerStats, bool]:
    """Drena o Ki enquanto estiver transformado. Se acabar, reverte para a base."""
    reverted = False
    if player.current_transformation and player.current_transformation in TRANSFORMATIONS_CATALOG:
        trans = TRANSFORMATIONS_CATALOG[player.current_transformation]
        drain = trans.ki_drain_per_sec * delta_time
        player.ki -= drain
        if player.ki <= 0:
            player.ki = 0.0
            player = revert_transformation(player)
            reverted = True
    return player, reverted

def charge_ki(player: PlayerStats, amount: float = 25.0) -> PlayerStats:
    """Carrega o Ki do jogador até o máximo."""
    player.ki = min(player.max_ki, player.ki + amount)
    return player
