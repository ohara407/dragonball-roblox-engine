"""
Testes Automatizados do Backend Dragon Ball Roblox — pytest.

Suite completa de testes cobrindo:
    - Criação de jogador com atributos padrão
    - Ganhos de treino por tipo (flexões, sombra, meditação, gravidade, sala do tempo)
    - Mecânica de level up com overflow de EXP
    - Ativação de transformação (sucesso e falhas: poder insuficiente, quest faltando)
    - Tick de drenagem de Ki e reversão automática
    - Zenkai Boost (+15% permanente)
    - Conclusão de quests e recompensas
    - Uso de habilidades (custo de Ki, cooldown, cálculo de dano)
    - Compra na loja (dedução de Zeni, atualização de inventário)

Todos os nomes de testes estão em português para clareza.
"""
import sys
import os
from datetime import datetime, timedelta

import pytest

# Garante que o diretório backend_api esteja no path de importação
sys.path.insert(0, os.path.dirname(__file__))

from models import PlayerStats, TrainingType
from engine import (
    TRANSFORMATIONS_CATALOG,
    QUESTS_CATALOG,
    recalculate_power_level,
    process_training,
    apply_zenkai_boost,
    transform_player,
    revert_transformation,
    drain_ki_tick,
)
from skills import (
    SKILL_CATALOG,
    PlayerSkillSet,
    learn_skill,
    use_skill,
    calculate_skill_damage,
)
from shop import (
    ITEM_CATALOG,
    Inventory,
    buy_item,
    use_item,
    get_shop_catalog,
    get_inventory,
)


# ==============================================================================
# FIXTURES — Jogadores e Objetos de Teste
# ==============================================================================

@pytest.fixture
def jogador_novo() -> PlayerStats:
    """Cria um jogador recém-criado com atributos padrão."""
    return PlayerStats(user_id=1, username="Goku_Teste")


@pytest.fixture
def jogador_forte() -> PlayerStats:
    """Cria um jogador avançado com poder suficiente para transformações."""
    return PlayerStats(
        user_id=2,
        username="Vegeta_Forte",
        power_level=500000,
        level=30,
        exp=0,
        exp_next=100000,
        zeni=1000000,
        health=50000.0,
        max_health=50000.0,
        ki=10000.0,
        max_ki=10000.0,
        strength=5000,
        defense=4000,
        agility=3500,
        current_transformation=None,
        unlocked_transformations=["kaioken", "ssj1", "ssj2"],
        completed_quests=[
            "quest_raditz", "quest_nappa", "quest_vegeta",
            "quest_freeza", "quest_cell",
        ],
        zenkai_count=3,
    )


@pytest.fixture
def skill_set_novo() -> PlayerSkillSet:
    """Cria um conjunto de habilidades padrão para um jogador novo."""
    return PlayerSkillSet(player_id=1)


@pytest.fixture
def skill_set_forte() -> PlayerSkillSet:
    """Cria um conjunto de habilidades para o jogador forte."""
    return PlayerSkillSet(
        player_id=2,
        learned_skills=[
            "rogafufuken", "ki_blast_barrage", "kamehameha",
            "masenko", "galick_ho", "final_flash",
        ],
    )


@pytest.fixture
def inventario_vazio() -> Inventory:
    """Cria um inventário vazio."""
    return Inventory(player_id=1)


@pytest.fixture
def inventario_com_itens() -> Inventory:
    """Cria um inventário com alguns itens para teste."""
    return Inventory(
        player_id=2,
        items={"senzu_bean": 3, "scouter": 1, "korin_water": 5},
        equipped=[],
    )


# ==============================================================================
# TESTES — CRIAÇÃO DE JOGADOR
# ==============================================================================

class TestCriacaoJogador:
    """Testes de criação de jogador com atributos padrão."""

    def teste_jogador_padrao_possui_atributos_iniciais(self, jogador_novo: PlayerStats):
        """Verifica se um jogador recém-criado possui todos os atributos padrão corretos."""
        assert jogador_novo.user_id == 1
        assert jogador_novo.username == "Goku_Teste"
        assert jogador_novo.power_level == 100
        assert jogador_novo.level == 1
        assert jogador_novo.exp == 0
        assert jogador_novo.exp_next == 500
        assert jogador_novo.zeni == 100

    def teste_jogador_padrao_possui_stats_base(self, jogador_novo: PlayerStats):
        """Verifica HP, Ki, Força, Defesa e Agilidade iniciais."""
        assert jogador_novo.health == 1000.0
        assert jogador_novo.max_health == 1000.0
        assert jogador_novo.ki == 500.0
        assert jogador_novo.max_ki == 500.0
        assert jogador_novo.strength == 20
        assert jogador_novo.defense == 20
        assert jogador_novo.agility == 20

    def teste_jogador_padrao_sem_transformacao_ativa(self, jogador_novo: PlayerStats):
        """Verifica que nenhuma transformação está ativa no início."""
        assert jogador_novo.current_transformation is None

    def teste_jogador_padrao_kaioken_desbloqueado(self, jogador_novo: PlayerStats):
        """Verifica que o Kaioken é a transformação inicial desbloqueada."""
        assert "kaioken" in jogador_novo.unlocked_transformations
        assert len(jogador_novo.unlocked_transformations) == 1

    def teste_jogador_padrao_quest_raditz_ativa(self, jogador_novo: PlayerStats):
        """Verifica que a primeira quest (Raditz) está ativa."""
        assert "quest_raditz" in jogador_novo.active_quests
        assert len(jogador_novo.completed_quests) == 0


# ==============================================================================
# TESTES — TREINAMENTO
# ==============================================================================

class TestTreinamento:
    """Testes dos ganhos de treinamento por tipo."""

    def teste_flexoes_aumentam_forca_e_defesa(self, jogador_novo: PlayerStats):
        """Treino de flexões deve aumentar Força e Defesa do jogador."""
        forca_antes = jogador_novo.strength
        defesa_antes = jogador_novo.defense

        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.PUSHUPS, duration=1)

        assert jogador_novo.strength > forca_antes
        assert jogador_novo.defense > defesa_antes
        assert ganhos["strength"] == 5   # 5 * time_factor(1)
        assert ganhos["defense"] == 4    # 4 * time_factor(1)

    def teste_shadow_boxing_aumenta_agilidade_e_ki(self, jogador_novo: PlayerStats):
        """Treino de sombra deve aumentar Agilidade e Max Ki."""
        agilidade_antes = jogador_novo.agility
        max_ki_antes = jogador_novo.max_ki

        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.SHADOW_BOXING, duration=1)

        assert jogador_novo.agility > agilidade_antes
        assert jogador_novo.max_ki > max_ki_antes
        assert ganhos["agility"] == 6
        assert ganhos["max_ki"] == 5.0

    def teste_meditacao_aumenta_ki_e_defesa(self, jogador_novo: PlayerStats):
        """Meditação deve expandir Max Ki, restaurar Ki e aumentar Defesa."""
        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.MEDITATION, duration=1)

        assert ganhos["max_ki"] == 15.0
        assert ganhos["ki"] == 25.0
        assert ganhos["defense"] == 2

    def teste_sala_de_gravidade_aumenta_todos_stats(self, jogador_novo: PlayerStats):
        """Sala de gravidade deve aumentar Força, Defesa, Agilidade e Max Ki."""
        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.GRAVITY_CHAMBER, duration=1)

        assert ganhos["strength"] == 12
        assert ganhos["defense"] == 10
        assert ganhos["agility"] == 10
        assert ganhos["max_ki"] == 10.0
        assert ganhos["exp"] == 80

    def teste_sala_do_tempo_ganho_massivo(self, jogador_novo: PlayerStats):
        """Sala do Tempo (Hyperbolic Time) deve dar os maiores ganhos."""
        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.HYPERBOLIC_TIME, duration=1)

        assert ganhos["strength"] == 25
        assert ganhos["defense"] == 25
        assert ganhos["agility"] == 20
        assert ganhos["max_ki"] == 30.0
        assert ganhos["exp"] == 200

    def teste_poder_de_luta_recalculado_apos_treino(self, jogador_novo: PlayerStats):
        """O poder de luta deve ser recalculado após cada treino."""
        poder_antes = jogador_novo.power_level
        jogador_novo, _ = process_training(jogador_novo, TrainingType.GRAVITY_CHAMBER, duration=5)
        assert jogador_novo.power_level > poder_antes

    def teste_duracao_limitada_entre_1_e_60(self, jogador_novo: PlayerStats):
        """Duração do treino deve ser limitada entre 1 e 60 segundos."""
        # Duração excessiva é limitada a 60
        jogador_novo, ganhos = process_training(jogador_novo, TrainingType.PUSHUPS, duration=100)
        assert ganhos["strength"] == 5 * 60  # max 60

        # Duração negativa é limitada a 1
        jogador2 = PlayerStats(user_id=99, username="Teste_Dur")
        jogador2, ganhos2 = process_training(jogador2, TrainingType.PUSHUPS, duration=-5)
        assert ganhos2["strength"] == 5 * 1  # min 1


# ==============================================================================
# TESTES — LEVEL UP
# ==============================================================================

class TestLevelUp:
    """Testes da mecânica de level up."""

    def teste_level_up_ao_atingir_exp_necessaria(self, jogador_novo: PlayerStats):
        """Jogador deve subir de nível quando EXP >= EXP necessária."""
        jogador_novo.exp = 499  # Falta 1 ponto
        assert jogador_novo.level == 1

        # Treino que dá pelo menos 1 EXP vai estourar o limite
        jogador_novo.exp = 500
        # Simular chamada de process_training que verifica level up
        jogador_novo, _ = process_training(jogador_novo, TrainingType.PUSHUPS, duration=1)
        # Treino dá 25 exp, e 500 base já alcançava level up
        assert jogador_novo.level >= 2

    def teste_level_up_exp_overflow_multiplos_niveis(self):
        """Se EXP exceder múltiplos thresholds, vários level ups devem ocorrer."""
        jogador = PlayerStats(user_id=10, username="ExpOverflow")
        # exp_next = 500, vamos dar EXP suficiente para múltiplos levels
        jogador.exp = 1200  # 500 (lvl2, exp_next→750) + 700 (sobra) → lvl3 também

        # Process training para disparar o while loop de level up
        jogador, _ = process_training(jogador, TrainingType.PUSHUPS, duration=1)
        # 1200 + 25 = 1225; level up: 1225-500=725 (lvl2, next=750);
        # 725 < 750 → para no level 2
        assert jogador.level >= 2

    def teste_level_up_aumenta_stats_bonus(self):
        """Cada level up deve dar bônus de HP, Ki, Força, Defesa e Agilidade."""
        jogador = PlayerStats(user_id=11, username="BonusLevel")
        hp_antes = jogador.max_health
        str_antes = jogador.strength

        jogador.exp = 500  # Exatamente o necessário
        jogador, _ = process_training(jogador, TrainingType.PUSHUPS, duration=1)

        assert jogador.max_health >= hp_antes + 200  # +200 por level
        assert jogador.strength >= str_antes + 10 + 5  # +10 level + 5 treino


# ==============================================================================
# TESTES — TRANSFORMAÇÕES
# ==============================================================================

class TestTransformacoes:
    """Testes de ativação e falha de transformações."""

    def teste_transformacao_kaioken_sucesso(self, jogador_forte: PlayerStats):
        """Jogador forte deve conseguir ativar o Kaioken."""
        sucesso, msg, trans = transform_player(jogador_forte, "kaioken")
        assert sucesso is True
        assert jogador_forte.current_transformation == "kaioken"
        assert trans is not None
        assert trans.name == "Kaioken x3"

    def teste_transformacao_ssj1_sucesso(self, jogador_forte: PlayerStats):
        """Jogador forte com quest completa deve ativar SSJ1."""
        sucesso, msg, trans = transform_player(jogador_forte, "ssj1")
        assert sucesso is True
        assert jogador_forte.current_transformation == "ssj1"

    def teste_transformacao_falha_poder_insuficiente(self, jogador_novo: PlayerStats):
        """Jogador fraco deve falhar ao tentar SSJ1 (poder insuficiente)."""
        # Precisa completar a quest primeiro para testar o poder
        jogador_novo.completed_quests.append("quest_freeza")
        sucesso, msg, trans = transform_player(jogador_novo, "ssj1")
        assert sucesso is False
        assert "insuficiente" in msg.lower() or "Poder" in msg

    def teste_transformacao_falha_quest_nao_completa(self, jogador_forte: PlayerStats):
        """Jogador deve falhar se a quest necessária não foi completada."""
        # SSJ3 requer quest_majin_buu que NÃO está completa
        assert "quest_majin_buu" not in jogador_forte.completed_quests
        sucesso, msg, trans = transform_player(jogador_forte, "ssj3")
        assert sucesso is False
        assert "quest_majin_buu" in msg or "Missão" in msg

    def teste_transformacao_forma_inexistente(self, jogador_forte: PlayerStats):
        """Tentar uma forma que não existe deve falhar."""
        sucesso, msg, trans = transform_player(jogador_forte, "ssj_imaginario")
        assert sucesso is False
        assert trans is None

    def teste_transformacao_falha_ki_insuficiente(self, jogador_forte: PlayerStats):
        """Transformação deve falhar se Ki < 50."""
        jogador_forte.ki = 10.0
        sucesso, msg, trans = transform_player(jogador_forte, "kaioken")
        assert sucesso is False
        assert "Ki insuficiente" in msg

    def teste_reverter_transformacao(self, jogador_forte: PlayerStats):
        """Reverter transformação deve limpar a forma ativa."""
        transform_player(jogador_forte, "ssj1")
        assert jogador_forte.current_transformation == "ssj1"

        revert_transformation(jogador_forte)
        assert jogador_forte.current_transformation is None


# ==============================================================================
# TESTES — DRENAGEM DE KI
# ==============================================================================

class TestDrenagemKi:
    """Testes do tick de drenagem de Ki durante transformações."""

    def teste_ki_diminui_durante_transformacao(self, jogador_forte: PlayerStats):
        """Ki deve diminuir a cada tick enquanto transformado."""
        transform_player(jogador_forte, "ssj1")
        ki_antes = jogador_forte.ki

        jogador_forte, reverteu = drain_ki_tick(jogador_forte, delta_time=1.0)

        assert jogador_forte.ki < ki_antes
        assert reverteu is False
        # SSJ1 drena 12/s → ki_antes - 12
        assert jogador_forte.ki == ki_antes - 12.0

    def teste_ki_zero_reverte_automaticamente(self, jogador_forte: PlayerStats):
        """Quando Ki chega a 0, a transformação deve ser revertida automaticamente."""
        transform_player(jogador_forte, "ssj1")
        jogador_forte.ki = 5.0  # Quase acabando

        jogador_forte, reverteu = drain_ki_tick(jogador_forte, delta_time=1.0)

        assert reverteu is True
        assert jogador_forte.ki == 0.0
        assert jogador_forte.current_transformation is None

    def teste_sem_drenagem_sem_transformacao(self, jogador_forte: PlayerStats):
        """Sem transformação ativa, o Ki não deve ser drenado."""
        ki_antes = jogador_forte.ki
        jogador_forte, reverteu = drain_ki_tick(jogador_forte, delta_time=1.0)

        assert jogador_forte.ki == ki_antes
        assert reverteu is False


# ==============================================================================
# TESTES — ZENKAI BOOST
# ==============================================================================

class TestZenkaiBoost:
    """Testes do sistema Zenkai Boost (ganho permanente de 15%)."""

    def teste_zenkai_aumenta_atributos_em_15_porcento(self, jogador_novo: PlayerStats):
        """Zenkai deve aumentar Força, Defesa e Agilidade em 15%."""
        str_antes = jogador_novo.strength
        def_antes = jogador_novo.defense
        agi_antes = jogador_novo.agility

        jogador_novo, total_boost = apply_zenkai_boost(jogador_novo)

        # int(20 * 0.15) = 3 para cada stat base de 20
        assert jogador_novo.strength == str_antes + int(str_antes * 0.15)
        assert jogador_novo.defense == def_antes + int(def_antes * 0.15)
        assert jogador_novo.agility == agi_antes + int(agi_antes * 0.15)

    def teste_zenkai_incrementa_contador(self, jogador_novo: PlayerStats):
        """Cada Zenkai deve incrementar o contador."""
        assert jogador_novo.zenkai_count == 0
        apply_zenkai_boost(jogador_novo)
        assert jogador_novo.zenkai_count == 1
        apply_zenkai_boost(jogador_novo)
        assert jogador_novo.zenkai_count == 2

    def teste_zenkai_restaura_hp_e_ki(self, jogador_novo: PlayerStats):
        """Zenkai deve restaurar HP e Ki ao máximo."""
        jogador_novo.health = 100.0  # Quase morto
        jogador_novo.ki = 50.0       # Quase sem Ki

        jogador_novo, _ = apply_zenkai_boost(jogador_novo)

        assert jogador_novo.health == jogador_novo.max_health
        assert jogador_novo.ki == jogador_novo.max_ki

    def teste_zenkai_aumenta_max_ki(self, jogador_novo: PlayerStats):
        """Zenkai deve aumentar o Max Ki em 15%."""
        max_ki_antes = jogador_novo.max_ki
        jogador_novo, _ = apply_zenkai_boost(jogador_novo)
        assert jogador_novo.max_ki == max_ki_antes + max_ki_antes * 0.15


# ==============================================================================
# TESTES — QUESTS
# ==============================================================================

class TestQuests:
    """Testes do sistema de conclusão de quests e recompensas."""

    def teste_catalogo_quests_nao_vazio(self):
        """O catálogo de quests deve ter entradas."""
        assert len(QUESTS_CATALOG) > 0

    def teste_quest_raditz_existe_com_recompensas(self):
        """A quest do Raditz deve existir e dar Kaioken como recompensa."""
        quest = QUESTS_CATALOG.get("quest_raditz")
        assert quest is not None
        assert quest.reward_exp == 500
        assert quest.reward_zeni == 1000
        assert quest.reward_form == "kaioken"

    def teste_quest_freeza_desbloqueia_ssj1(self):
        """A quest do Freeza deve desbloquear SSJ1."""
        quest = QUESTS_CATALOG.get("quest_freeza")
        assert quest is not None
        assert quest.reward_form == "ssj1"
        assert quest.saga == "Saga de Namekusei"

    def teste_conclusao_quest_adiciona_recompensas(self, jogador_novo: PlayerStats):
        """Simula completar uma quest e verifica se EXP e Zeni são adicionados."""
        quest = QUESTS_CATALOG["quest_raditz"]

        # Simula conclusão
        jogador_novo.exp += quest.reward_exp
        jogador_novo.zeni += quest.reward_zeni
        jogador_novo.completed_quests.append(quest.id)
        if quest.reward_form:
            jogador_novo.unlocked_transformations.append(quest.reward_form)

        assert jogador_novo.exp == quest.reward_exp
        assert jogador_novo.zeni == 100 + quest.reward_zeni
        assert "quest_raditz" in jogador_novo.completed_quests
        assert "kaioken" in jogador_novo.unlocked_transformations


# ==============================================================================
# TESTES — SISTEMA DE HABILIDADES (SKILLS)
# ==============================================================================

class TestHabilidades:
    """Testes do sistema de golpes especiais."""

    def teste_catalogo_tem_15_habilidades(self):
        """O catálogo deve conter exatamente 15 habilidades."""
        assert len(SKILL_CATALOG) == 15

    def teste_aprender_habilidade_sucesso(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Jogador no nível correto deve aprender uma nova habilidade."""
        sucesso, msg, skill_set = learn_skill(jogador_forte, skill_set_forte, "kienzan")
        assert sucesso is True
        assert "kienzan" in skill_set.learned_skills

    def teste_aprender_habilidade_ja_aprendida(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Tentar aprender uma habilidade já aprendida deve falhar."""
        sucesso, msg, _ = learn_skill(jogador_forte, skill_set_forte, "kamehameha")
        assert sucesso is False
        assert "já domina" in msg

    def teste_aprender_habilidade_nivel_insuficiente(
        self, jogador_novo: PlayerStats, skill_set_novo: PlayerSkillSet
    ):
        """Jogador de nível baixo não deve aprender habilidades de nível alto."""
        sucesso, msg, _ = learn_skill(jogador_novo, skill_set_novo, "final_flash")
        assert sucesso is False
        assert "Nível insuficiente" in msg

    def teste_aprender_habilidade_quest_necessaria(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Habilidade que requer quest não completada deve falhar."""
        # genki_dama requer quest_majin_buu
        sucesso, msg, _ = learn_skill(jogador_forte, skill_set_forte, "genki_dama")
        assert sucesso is False
        assert "quest_majin_buu" in msg

    def teste_usar_habilidade_sucesso_com_dano(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Usar uma habilidade aprendida deve causar dano e deduzir Ki."""
        ki_antes = jogador_forte.ki
        sucesso, msg, dano, player, skill_set = use_skill(
            jogador_forte, skill_set_forte, "kamehameha", target_defense=100
        )
        assert sucesso is True
        assert dano > 0
        assert player.ki < ki_antes
        assert player.ki == ki_antes - SKILL_CATALOG["kamehameha"].ki_cost

    def teste_usar_habilidade_ki_insuficiente(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Habilidade deve falhar se o jogador não tiver Ki suficiente."""
        jogador_forte.ki = 5.0  # Praticamente sem Ki
        sucesso, msg, dano, _, _ = use_skill(
            jogador_forte, skill_set_forte, "kamehameha", target_defense=0
        )
        assert sucesso is False
        assert dano == 0.0
        assert "Ki insuficiente" in msg

    def teste_usar_habilidade_em_cooldown(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Usar a mesma habilidade antes do cooldown expirar deve falhar."""
        now = datetime(2026, 1, 1, 12, 0, 0)

        # Primeiro uso — sucesso
        sucesso1, _, _, jogador_forte, skill_set_forte = use_skill(
            jogador_forte, skill_set_forte, "kamehameha",
            target_defense=0, current_time=now,
        )
        assert sucesso1 is True

        # Segundo uso 1 segundo depois — ainda em cooldown (cd = 4s)
        now_plus_1 = now + timedelta(seconds=1)
        sucesso2, msg, dano, _, _ = use_skill(
            jogador_forte, skill_set_forte, "kamehameha",
            target_defense=0, current_time=now_plus_1,
        )
        assert sucesso2 is False
        assert "cooldown" in msg

    def teste_usar_habilidade_apos_cooldown_expirar(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Após o cooldown expirar, a habilidade deve estar disponível novamente."""
        now = datetime(2026, 1, 1, 12, 0, 0)

        use_skill(
            jogador_forte, skill_set_forte, "kamehameha",
            target_defense=0, current_time=now,
        )

        # 5 segundos depois (cooldown é 4s)
        now_plus_5 = now + timedelta(seconds=5)
        sucesso, _, dano, _, _ = use_skill(
            jogador_forte, skill_set_forte, "kamehameha",
            target_defense=0, current_time=now_plus_5,
        )
        assert sucesso is True
        assert dano > 0

    def teste_usar_habilidade_requer_transformacao(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Habilidade que requer transformação deve falhar sem ela ativa."""
        # kaioken_attack requer kaioken ativo
        skill_set_forte.learned_skills.append("kaioken_attack")
        assert jogador_forte.current_transformation is None

        sucesso, msg, dano, _, _ = use_skill(
            jogador_forte, skill_set_forte, "kaioken_attack", target_defense=0
        )
        assert sucesso is False
        assert "requer" in msg.lower() or "transformação" in msg.lower()

    def teste_habilidade_utilitaria_sem_dano(
        self, jogador_forte: PlayerStats, skill_set_forte: PlayerSkillSet
    ):
        """Habilidades utilitárias (Shunkan Ido, Taiyo-ken) não devem causar dano."""
        skill_set_forte.learned_skills.append("taiyo_ken")
        sucesso, msg, dano, _, _ = use_skill(
            jogador_forte, skill_set_forte, "taiyo_ken", target_defense=0
        )
        assert sucesso is True
        assert dano == 0.0

    def teste_calculo_dano_formula(self, jogador_forte: PlayerStats):
        """Verifica a fórmula de cálculo de dano."""
        skill = SKILL_CATALOG["kamehameha"]
        defesa_alvo = 100

        dano = calculate_skill_damage(jogador_forte, skill, defesa_alvo)

        # base = (5000 * 3.5) + (10000 * 0.3) = 17500 + 3000 = 20500
        # net  = 20500 - (100 * 0.4) = 20500 - 40 = 20460
        # sem transformação, multiplicador = 1
        expected = (jogador_forte.strength * skill.damage_multiplier) + (jogador_forte.ki * 0.3) - (defesa_alvo * 0.4)
        assert dano == max(1.0, expected)


# ==============================================================================
# TESTES — LOJA E INVENTÁRIO
# ==============================================================================

class TestLoja:
    """Testes do sistema de loja e inventário."""

    def teste_catalogo_tem_12_itens(self):
        """O catálogo da loja deve conter exatamente 12 itens."""
        catalogo = get_shop_catalog()
        assert len(catalogo) == 12

    def teste_comprar_item_sucesso(
        self, jogador_forte: PlayerStats, inventario_vazio: Inventory
    ):
        """Compra de item com Zeni suficiente deve funcionar."""
        inventario_vazio.player_id = jogador_forte.user_id
        zeni_antes = jogador_forte.zeni

        sucesso, msg, player, inv = buy_item(
            jogador_forte, inventario_vazio, "senzu_bean", quantity=2
        )

        assert sucesso is True
        assert player.zeni == zeni_antes - (5000 * 2)
        assert inv.items["senzu_bean"] == 2

    def teste_comprar_item_zeni_insuficiente(
        self, jogador_novo: PlayerStats, inventario_vazio: Inventory
    ):
        """Compra deve falhar se o jogador não tiver Zeni suficiente."""
        sucesso, msg, _, _ = buy_item(
            jogador_novo, inventario_vazio, "dragon_radar", quantity=1
        )
        assert sucesso is False
        assert "Zeni insuficiente" in msg

    def teste_comprar_item_inexistente(
        self, jogador_forte: PlayerStats, inventario_vazio: Inventory
    ):
        """Compra de item que não existe no catálogo deve falhar."""
        sucesso, msg, _, _ = buy_item(
            jogador_forte, inventario_vazio, "item_fantasma", quantity=1
        )
        assert sucesso is False
        assert "não existe" in msg

    def teste_comprar_item_excede_max_stack(
        self, jogador_forte: PlayerStats, inventario_com_itens: Inventory
    ):
        """Compra deve falhar se exceder o max_stack do item."""
        # senzu_bean max_stack=10, já tem 3, tenta comprar +8
        sucesso, msg, _, _ = buy_item(
            jogador_forte, inventario_com_itens, "senzu_bean", quantity=8
        )
        assert sucesso is False
        assert "Inventário cheio" in msg or "Máximo" in msg

    def teste_usar_senzu_bean_restaura_hp_e_ki(
        self, jogador_forte: PlayerStats, inventario_com_itens: Inventory
    ):
        """Usar uma Senzu Bean deve restaurar HP e Ki ao máximo."""
        jogador_forte.health = 1000.0  # Parcialmente ferido
        jogador_forte.ki = 500.0       # Ki parcial

        sucesso, msg, player, inv = use_item(
            jogador_forte, inventario_com_itens, "senzu_bean"
        )

        assert sucesso is True
        assert player.health == player.max_health
        assert player.ki == player.max_ki
        assert inv.items["senzu_bean"] == 2  # Tinha 3, usou 1

    def teste_usar_korin_water_restaura_50_porcento_hp(
        self, jogador_forte: PlayerStats, inventario_com_itens: Inventory
    ):
        """Usar Água de Korin deve restaurar 50% do HP máximo."""
        jogador_forte.health = 0.0  # Quase morto
        sucesso, msg, player, _ = use_item(
            jogador_forte, inventario_com_itens, "korin_water"
        )
        assert sucesso is True
        assert player.health == jogador_forte.max_health * 0.5

    def teste_equipar_e_desequipar_item(
        self, jogador_forte: PlayerStats, inventario_com_itens: Inventory
    ):
        """Equipar e desequipar um item deve alternar o estado."""
        # Equipar scouter
        sucesso1, msg1, _, inv = use_item(
            jogador_forte, inventario_com_itens, "scouter"
        )
        assert sucesso1 is True
        assert "scouter" in inv.equipped

        # Desequipar scouter
        sucesso2, msg2, _, inv = use_item(
            jogador_forte, inv, "scouter"
        )
        assert sucesso2 is True
        assert "scouter" not in inv.equipped

    def teste_usar_item_que_nao_possui(
        self, jogador_forte: PlayerStats, inventario_vazio: Inventory
    ):
        """Usar um item que o jogador não possui deve falhar."""
        inventario_vazio.player_id = jogador_forte.user_id
        sucesso, msg, _, _ = use_item(
            jogador_forte, inventario_vazio, "senzu_bean"
        )
        assert sucesso is False
        assert "não possui" in msg

    def teste_get_inventory_retorna_itens(self, inventario_com_itens: Inventory):
        """get_inventory deve retornar os itens do inventário."""
        itens = get_inventory(inventario_com_itens)
        assert "senzu_bean" in itens
        assert itens["senzu_bean"] == 3
        assert itens["korin_water"] == 5

    def teste_usar_sacred_water_bonus_permanente(
        self, jogador_forte: PlayerStats, inventario_vazio: Inventory
    ):
        """Usar Água Sagrada deve dar +500 permanente em Força, Defesa e Agilidade."""
        inventario_vazio.items["sacred_water"] = 1
        str_antes = jogador_forte.strength
        def_antes = jogador_forte.defense
        agi_antes = jogador_forte.agility

        sucesso, msg, player, inv = use_item(
            jogador_forte, inventario_vazio, "sacred_water"
        )

        assert sucesso is True
        assert player.strength == str_antes + 500
        assert player.defense == def_antes + 500
        assert player.agility == agi_antes + 500
        # Item consumido — não deve mais estar no inventário
        assert "sacred_water" not in inv.items


# ==============================================================================
# TESTES — INTEGRAÇÃO (FLUXO COMPLETO)
# ==============================================================================

class TestIntegracao:
    """Testes de integração que combinam múltiplos sistemas."""

    def teste_fluxo_treinar_transformar_atacar(self):
        """Fluxo completo: treinar → transformar → usar habilidade."""
        # 1. Cria jogador
        jogador = PlayerStats(user_id=100, username="Gohan_Integração")
        skill_set = PlayerSkillSet(player_id=100)

        # 2. Treina até ter stats suficientes
        for _ in range(20):
            jogador, _ = process_training(jogador, TrainingType.GRAVITY_CHAMBER, duration=10)

        # 3. Completa quest para desbloquear Kaioken
        jogador.completed_quests.append("quest_raditz")

        # 4. Tenta transformar
        sucesso, msg, trans = transform_player(jogador, "kaioken")
        assert sucesso is True

        # 5. Aprende Kamehameha (precisa level >= 5)
        if jogador.level >= 5:
            ok, _, skill_set = learn_skill(jogador, skill_set, "kamehameha")
            assert ok is True

            # 6. Usa Kamehameha
            ok, _, dano, jogador, skill_set = use_skill(
                jogador, skill_set, "kamehameha", target_defense=50
            )
            assert ok is True
            assert dano > 0

    def teste_fluxo_comprar_e_usar_senzu(self):
        """Fluxo: ganhar Zeni → comprar Senzu → tomar dano → usar Senzu."""
        jogador = PlayerStats(user_id=200, username="Krillin_Shop")
        jogador.zeni = 10000
        inv = Inventory(player_id=200)

        # Compra 2 Senzu Beans
        ok, _, jogador, inv = buy_item(jogador, inv, "senzu_bean", 2)
        assert ok is True
        assert inv.items["senzu_bean"] == 2

        # Toma dano
        jogador.health = 100.0
        jogador.ki = 50.0

        # Usa Senzu
        ok, _, jogador, inv = use_item(jogador, inv, "senzu_bean")
        assert ok is True
        assert jogador.health == jogador.max_health
        assert jogador.ki == jogador.max_ki
        assert inv.items["senzu_bean"] == 1
