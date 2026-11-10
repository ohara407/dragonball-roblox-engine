"""
Sistema de Golpes Especiais e Habilidades de Combate — Dragon Ball Roblox.

Este módulo implementa o sistema completo de habilidades (skills) de combate
inspiradas no universo Dragon Ball. Cada golpe possui custos de Ki, cooldowns,
requisitos de nível/transformação e fórmulas de dano detalhadas.
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Importa modelos do jogador e catálogo de transformações do motor existente
from models import PlayerStats
from engine import TRANSFORMATIONS_CATALOG, recalculate_power_level


# ==============================================================================
# ENUMS DE CLASSIFICAÇÃO DE HABILIDADES
# ==============================================================================

class RangeType(str, Enum):
    """Tipo de alcance do golpe."""
    MELEE = "melee"      # Corpo a corpo
    RANGED = "ranged"    # Projétil à distância
    AOE = "aoe"          # Área de efeito (atinge múltiplos alvos)


class ElementType(str, Enum):
    """Elemento/natureza da habilidade."""
    PHYSICAL = "physical"  # Golpe físico puro (socos, chutes)
    ENERGY = "energy"      # Rajada de Ki / energia
    DIVINE = "divine"      # Ki divino (Hakai, Genki Dama, Ryuuken)


# ==============================================================================
# MODELO DE HABILIDADE
# ==============================================================================

class Skill(BaseModel):
    """
    Representa uma habilidade de combate no jogo.

    Attributes:
        id: Identificador único do golpe.
        name: Nome de exibição do golpe (português/japonês).
        description: Descrição narrativa do golpe.
        damage_multiplier: Multiplicador aplicado sobre a força do jogador.
        ki_cost: Custo de Ki para executar o golpe.
        cooldown_seconds: Tempo de espera (segundos) entre usos consecutivos.
        range_type: Alcance do golpe (melee, ranged, aoe).
        element: Natureza elemental do golpe (physical, energy, divine).
        unlock_level: Nível mínimo do jogador para aprender o golpe.
        unlock_quest_id: Quest que deve estar completa para desbloquear (opcional).
        required_transformation: Transformação que deve estar ativa para usar (opcional).
        charge_seconds: Tempo de carga antes de disparar (0 = instantâneo).
        is_utility: Se True, o golpe não causa dano (ex.: teleporte, stun).
        stun_duration: Duração do stun em segundos (0 = sem stun).
    """
    id: str
    name: str
    description: str
    damage_multiplier: float
    ki_cost: float
    cooldown_seconds: float
    range_type: RangeType
    element: ElementType
    unlock_level: int = 1
    unlock_quest_id: Optional[str] = None
    required_transformation: Optional[str] = None
    charge_seconds: float = 0.0
    is_utility: bool = False
    stun_duration: float = 0.0


# ==============================================================================
# CATÁLOGO DE HABILIDADES — 15 GOLPES ICÔNICOS
# ==============================================================================

SKILL_CATALOG: Dict[str, Skill] = {
    # ── Golpes de Energia (Ranged) ───────────────────────────────────────
    "kamehameha": Skill(
        id="kamehameha",
        name="Kamehameha",
        description=(
            "A técnica lendária do Mestre Kame. Uma onda de energia concentrada "
            "disparada das palmas das mãos após um breve carregamento."
        ),
        damage_multiplier=3.5,
        ki_cost=80.0,
        cooldown_seconds=4.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=5,
        charge_seconds=1.5,
    ),
    "masenko": Skill(
        id="masenko",
        name="Masenko",
        description=(
            "Rajada de energia rápida ensinada por Piccolo. Menor potência que "
            "o Kamehameha, mas com disparo quase instantâneo."
        ),
        damage_multiplier=2.0,
        ki_cost=40.0,
        cooldown_seconds=2.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=3,
        charge_seconds=0.5,
    ),
    "galick_ho": Skill(
        id="galick_ho",
        name="Galick Ho",
        description=(
            "O golpe de energia exclusivo do Príncipe dos Saiyajins, Vegeta. "
            "Rival direto do Kamehameha em poder destrutivo."
        ),
        damage_multiplier=3.5,
        ki_cost=85.0,
        cooldown_seconds=4.5,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=8,
        unlock_quest_id="quest_vegeta",
        charge_seconds=1.5,
    ),
    "kienzan": Skill(
        id="kienzan",
        name="Kienzan (Disco Destruidor)",
        description=(
            "Um disco de Ki afiado capaz de cortar quase qualquer coisa. "
            "Dano muito alto, mas cooldown extenso e fácil de desviar."
        ),
        damage_multiplier=5.0,
        ki_cost=100.0,
        cooldown_seconds=10.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=10,
        charge_seconds=2.0,
    ),
    "makankosappo": Skill(
        id="makankosappo",
        name="Makankosappo (Canhão Especial)",
        description=(
            "Feixe espiral perfurante de Piccolo. Requer longo carregamento, "
            "mas penetra qualquer defesa com dano devastador."
        ),
        damage_multiplier=7.0,
        ki_cost=120.0,
        cooldown_seconds=15.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=12,
        charge_seconds=5.0,
    ),
    "final_flash": Skill(
        id="final_flash",
        name="Final Flash",
        description=(
            "O golpe supremo de Vegeta: uma explosão de energia colossal "
            "que consome uma quantidade enorme de Ki."
        ),
        damage_multiplier=6.0,
        ki_cost=150.0,
        cooldown_seconds=12.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=20,
        unlock_quest_id="quest_cell",
        charge_seconds=3.0,
    ),
    "big_bang_attack": Skill(
        id="big_bang_attack",
        name="Big Bang Attack",
        description=(
            "Esfera de energia concentrada disparada com uma mão. "
            "Rápida e poderosa — marca registrada de Vegeta."
        ),
        damage_multiplier=4.0,
        ki_cost=90.0,
        cooldown_seconds=5.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=15,
        charge_seconds=1.0,
    ),
    "ki_blast_barrage": Skill(
        id="ki_blast_barrage",
        name="Rajada de Ki (Ki Blast Barrage)",
        description=(
            "Uma saraivada rápida de múltiplos tiros de Ki. Cada projétil "
            "causa pouco dano, mas o volume compensa."
        ),
        damage_multiplier=1.2,
        ki_cost=25.0,
        cooldown_seconds=1.0,
        range_type=RangeType.RANGED,
        element=ElementType.ENERGY,
        unlock_level=1,
        charge_seconds=0.0,
    ),

    # ── Golpes Divinos / AoE ─────────────────────────────────────────────
    "genki_dama": Skill(
        id="genki_dama",
        name="Genki Dama (Esfera do Espírito)",
        description=(
            "Coleta energia de todos os seres vivos do planeta (ou universo). "
            "Dano absurdo, custo absurdo, carregamento absurdo. O golpe definitivo."
        ),
        damage_multiplier=15.0,
        ki_cost=400.0,
        cooldown_seconds=60.0,
        range_type=RangeType.AOE,
        element=ElementType.DIVINE,
        unlock_level=25,
        unlock_quest_id="quest_majin_buu",
        charge_seconds=10.0,
    ),
    "hakai": Skill(
        id="hakai",
        name="Hakai (Destruição)",
        description=(
            "O poder absoluto dos Deuses da Destruição. Apaga a existência "
            "de inimigos de nível inferior instantaneamente."
        ),
        damage_multiplier=50.0,
        ki_cost=300.0,
        cooldown_seconds=45.0,
        range_type=RangeType.RANGED,
        element=ElementType.DIVINE,
        unlock_level=50,
        required_transformation="ultra_ego",
        charge_seconds=2.0,
    ),

    # ── Golpes Corpo a Corpo (Melee) ─────────────────────────────────────
    "rogafufuken": Skill(
        id="rogafufuken",
        name="Rogafufuken (Punho do Lobo)",
        description=(
            "A técnica de combate corpo a corpo de Yamcha. Uma sequência "
            "veloz de socos e garras. Golpe inicial dos guerreiros."
        ),
        damage_multiplier=1.5,
        ki_cost=15.0,
        cooldown_seconds=1.5,
        range_type=RangeType.MELEE,
        element=ElementType.PHYSICAL,
        unlock_level=1,
    ),
    "ryuuken": Skill(
        id="ryuuken",
        name="Ryuuken (Punho do Dragão)",
        description=(
            "Um soco devastador envolto pela imagem etérea de um dragão dourado. "
            "Requer no mínimo a forma Super Saiyajin 3."
        ),
        damage_multiplier=8.0,
        ki_cost=180.0,
        cooldown_seconds=20.0,
        range_type=RangeType.MELEE,
        element=ElementType.DIVINE,
        unlock_level=30,
        required_transformation="ssj3",
        charge_seconds=1.0,
    ),
    "kaioken_attack": Skill(
        id="kaioken_attack",
        name="Kaioken Attack",
        description=(
            "Ataque físico potenciado pelo Kaioken. O corpo brilha vermelho "
            "enquanto desfere uma combinação brutal de golpes."
        ),
        damage_multiplier=2.5,
        ki_cost=50.0,
        cooldown_seconds=3.0,
        range_type=RangeType.MELEE,
        element=ElementType.PHYSICAL,
        unlock_level=5,
        required_transformation="kaioken",
    ),

    # ── Habilidades Utilitárias ──────────────────────────────────────────
    "shunkan_ido": Skill(
        id="shunkan_ido",
        name="Shunkan Ido (Transmissão Instantânea)",
        description=(
            "Teleporta instantaneamente para qualquer Ki que o jogador consiga "
            "sentir. Sem dano, mas essencial para reposicionamento tático."
        ),
        damage_multiplier=0.0,
        ki_cost=20.0,
        cooldown_seconds=5.0,
        range_type=RangeType.MELEE,
        element=ElementType.ENERGY,
        unlock_level=15,
        is_utility=True,
    ),
    "taiyo_ken": Skill(
        id="taiyo_ken",
        name="Taiyo-ken (Reflexo Solar)",
        description=(
            "Emite um clarão cegante que atordoa todos os inimigos próximos "
            "por 3 segundos. Não causa dano, mas abre janela de ataque."
        ),
        damage_multiplier=0.0,
        ki_cost=30.0,
        cooldown_seconds=8.0,
        range_type=RangeType.AOE,
        element=ElementType.ENERGY,
        unlock_level=6,
        is_utility=True,
        stun_duration=3.0,
    ),
}


# ==============================================================================
# MODELO DE HABILIDADES DO JOGADOR
# ==============================================================================

class PlayerSkillSet(BaseModel):
    """
    Rastreia as habilidades aprendidas pelo jogador e seus respectivos cooldowns.

    Attributes:
        player_id: ID do jogador dono deste conjunto de habilidades.
        learned_skills: Lista de IDs de habilidades aprendidas.
        cooldown_timestamps: Mapa de skill_id → datetime em que o cooldown expira.
            Se o horário atual >= timestamp, o golpe está disponível.
    """
    player_id: int
    learned_skills: List[str] = Field(default_factory=lambda: ["rogafufuken", "ki_blast_barrage"])
    cooldown_timestamps: Dict[str, datetime] = Field(default_factory=dict)


# ==============================================================================
# FUNÇÕES DO SISTEMA DE HABILIDADES
# ==============================================================================

def learn_skill(
    player: PlayerStats,
    skill_set: PlayerSkillSet,
    skill_id: str,
) -> Tuple[bool, str, PlayerSkillSet]:
    """
    Tenta ensinar uma habilidade ao jogador.

    Verifica se o golpe existe no catálogo, se o jogador atende ao nível mínimo
    e se completou a quest de desbloqueio (quando aplicável).

    Args:
        player: Dados atuais do jogador.
        skill_set: Conjunto de habilidades do jogador.
        skill_id: ID da habilidade a ser aprendida.

    Returns:
        Tupla (sucesso, mensagem, skill_set_atualizado).
    """
    # Verifica existência no catálogo
    if skill_id not in SKILL_CATALOG:
        return False, f"Habilidade '{skill_id}' não existe no catálogo.", skill_set

    skill = SKILL_CATALOG[skill_id]

    # Já aprendida?
    if skill_id in skill_set.learned_skills:
        return False, f"Você já domina a técnica '{skill.name}'!", skill_set

    # Verifica nível mínimo
    if player.level < skill.unlock_level:
        return (
            False,
            f"Nível insuficiente para aprender '{skill.name}'. "
            f"Necessário: {skill.unlock_level}, Atual: {player.level}.",
            skill_set,
        )

    # Verifica quest de desbloqueio
    if skill.unlock_quest_id and skill.unlock_quest_id not in player.completed_quests:
        return (
            False,
            f"É necessário completar a missão '{skill.unlock_quest_id}' "
            f"antes de aprender '{skill.name}'.",
            skill_set,
        )

    # Aprende o golpe
    skill_set.learned_skills.append(skill_id)
    return True, f"Técnica '{skill.name}' aprendida com sucesso! 🔥", skill_set


def calculate_skill_damage(
    player: PlayerStats,
    skill: Skill,
    target_defense: int,
) -> float:
    """
    Calcula o dano final de uma habilidade.

    Fórmula:
        base_damage = (player.strength * skill.damage_multiplier) + (player.ki * 0.3)
        dano_líquido = base_damage - (target_defense * 0.4)
        Se houver transformação ativa, aplica o multiplicador da forma.
        Dano mínimo garantido = 1.0

    Args:
        player: Dados atuais do jogador (pós-custo de Ki).
        skill: A habilidade sendo utilizada.
        target_defense: Defesa do alvo.

    Returns:
        Dano final (float), mínimo de 1.0.
    """
    # Dano base
    base_damage = (player.strength * skill.damage_multiplier) + (player.ki * 0.3)

    # Subtrai mitigação de defesa do alvo
    net_damage = base_damage - (target_defense * 0.4)

    # Aplica multiplicador de transformação (se ativa)
    if player.current_transformation and player.current_transformation in TRANSFORMATIONS_CATALOG:
        trans = TRANSFORMATIONS_CATALOG[player.current_transformation]
        net_damage *= trans.multiplier

    # Garante dano mínimo de 1
    return max(1.0, net_damage)


def use_skill(
    player: PlayerStats,
    skill_set: PlayerSkillSet,
    skill_id: str,
    target_defense: int = 0,
    current_time: Optional[datetime] = None,
) -> Tuple[bool, str, float, PlayerStats, PlayerSkillSet]:
    """
    Executa uma habilidade contra um alvo.

    Validações realizadas:
        1. Habilidade existe no catálogo.
        2. Jogador aprendeu a habilidade.
        3. Cooldown não está ativo.
        4. Jogador possui Ki suficiente.
        5. Transformação necessária está ativa (se aplicável).

    Args:
        player: Dados atuais do jogador.
        skill_set: Conjunto de habilidades do jogador.
        skill_id: ID da habilidade a ser usada.
        target_defense: Defesa do alvo (padrão 0).
        current_time: Horário atual (para testes); se None, usa datetime.utcnow().

    Returns:
        Tupla (sucesso, mensagem, dano_causado, player_atualizado, skill_set_atualizado).
    """
    now = current_time or datetime.utcnow()
    damage_dealt = 0.0

    # 1. Verifica existência no catálogo
    if skill_id not in SKILL_CATALOG:
        return False, f"Habilidade '{skill_id}' não existe.", damage_dealt, player, skill_set

    skill = SKILL_CATALOG[skill_id]

    # 2. Verifica se o jogador aprendeu
    if skill_id not in skill_set.learned_skills:
        return (
            False,
            f"Você ainda não aprendeu '{skill.name}'!",
            damage_dealt,
            player,
            skill_set,
        )

    # 3. Verifica cooldown
    if skill_id in skill_set.cooldown_timestamps:
        cooldown_end = skill_set.cooldown_timestamps[skill_id]
        if now < cooldown_end:
            remaining = (cooldown_end - now).total_seconds()
            return (
                False,
                f"'{skill.name}' está em cooldown! Faltam {remaining:.1f}s.",
                damage_dealt,
                player,
                skill_set,
            )

    # 4. Verifica Ki
    if player.ki < skill.ki_cost:
        return (
            False,
            f"Ki insuficiente para '{skill.name}'. "
            f"Necessário: {skill.ki_cost:.0f}, Atual: {player.ki:.0f}.",
            damage_dealt,
            player,
            skill_set,
        )

    # 5. Verifica transformação necessária
    if skill.required_transformation:
        if player.current_transformation != skill.required_transformation:
            trans_name = skill.required_transformation
            if skill.required_transformation in TRANSFORMATIONS_CATALOG:
                trans_name = TRANSFORMATIONS_CATALOG[skill.required_transformation].name
            return (
                False,
                f"'{skill.name}' requer a transformação '{trans_name}' ativa!",
                damage_dealt,
                player,
                skill_set,
            )

    # ── Execução do golpe ────────────────────────────────────────────────

    # Deduz custo de Ki
    player.ki -= skill.ki_cost

    # Inicia cooldown
    skill_set.cooldown_timestamps[skill_id] = now + timedelta(seconds=skill.cooldown_seconds)

    # Calcula dano (habilidades utilitárias causam 0)
    if skill.is_utility:
        damage_dealt = 0.0
        if skill.stun_duration > 0:
            msg = (
                f"⚡ {skill.name} executado! Inimigo atordoado por "
                f"{skill.stun_duration:.0f}s! (Ki restante: {player.ki:.0f})"
            )
        else:
            msg = f"✨ {skill.name} executado com sucesso! (Ki restante: {player.ki:.0f})"
    else:
        damage_dealt = calculate_skill_damage(player, skill, target_defense)
        msg = (
            f"💥 {skill.name} causou {damage_dealt:,.0f} de dano! "
            f"(Ki restante: {player.ki:.0f})"
        )

    # Recalcula poder de luta após gasto de Ki
    player.power_level = recalculate_power_level(player)

    return True, msg, damage_dealt, player, skill_set
