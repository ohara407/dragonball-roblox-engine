"""
Sistema de Loja, Itens e Inventário — Dragon Ball Roblox.

Este módulo implementa a loja do jogo (Zeni Shop), o catálogo de itens,
o inventário do jogador e as funções de compra/uso de itens.
Todos os preços utilizam a moeda 'Zeni' do universo Dragon Ball.
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field

# Importa modelos do jogador do módulo existente
from models import PlayerStats


# ==============================================================================
# ENUMS DE TIPO DE ITEM
# ==============================================================================

class ItemType(str, Enum):
    """Categoria do item na loja."""
    CONSUMABLE = "consumable"  # Itens de uso único (Senzu Bean, poções)
    EQUIPMENT = "equipment"    # Equipamentos permanentes (armaduras, acessórios)
    SPECIAL = "special"        # Itens especiais de uso único e efeito permanente


# ==============================================================================
# MODELO DE ITEM
# ==============================================================================

class Item(BaseModel):
    """
    Representa um item disponível na loja ou no inventário.

    Attributes:
        id: Identificador único do item.
        name: Nome de exibição do item.
        description: Descrição narrativa do item.
        price_zeni: Preço em Zeni para compra na loja.
        item_type: Tipo do item (consumable, equipment, special).
        effect: Dicionário descrevendo os efeitos do item ao ser usado.
            Exemplos: {"heal_percent": 100}, {"stat_boost": {"strength_mult": 1.2}}
        max_stack: Quantidade máxima empilhável no inventário.
    """
    id: str
    name: str
    description: str
    price_zeni: int
    item_type: ItemType
    effect: Dict = Field(default_factory=dict)
    max_stack: int = 99


# ==============================================================================
# MODELO DE INVENTÁRIO
# ==============================================================================

class Inventory(BaseModel):
    """
    Inventário de um jogador.

    Attributes:
        player_id: ID do jogador dono deste inventário.
        items: Mapa de item_id → quantidade possuída.
        equipped: Lista de item_ids de equipamentos atualmente vestidos.
    """
    player_id: int
    items: Dict[str, int] = Field(default_factory=dict)
    equipped: List[str] = Field(default_factory=list)


# ==============================================================================
# CATÁLOGO DE ITENS DA LOJA — 12 ITENS ICÔNICOS
# ==============================================================================

ITEM_CATALOG: Dict[str, Item] = {
    # ── Consumíveis ──────────────────────────────────────────────────────
    "senzu_bean": Item(
        id="senzu_bean",
        name="Semente dos Deuses (Senzu Bean)",
        description=(
            "A lendária semente cultivada por Korin. Restaura 100% do HP "
            "e 100% do Ki instantaneamente."
        ),
        price_zeni=5000,
        item_type=ItemType.CONSUMABLE,
        effect={"heal_percent": 100, "ki_restore_percent": 100},
        max_stack=10,
    ),
    "korin_water": Item(
        id="korin_water",
        name="Água de Korin",
        description=(
            "Água sagrada da Torre de Korin. Restaura 50% do HP. "
            "Mais barata que a Senzu, mas menos eficaz."
        ),
        price_zeni=1500,
        item_type=ItemType.CONSUMABLE,
        effect={"heal_percent": 50},
        max_stack=20,
    ),

    # ── Equipamentos ─────────────────────────────────────────────────────
    "scouter": Item(
        id="scouter",
        name="Scouter (Rastreador)",
        description=(
            "Dispositivo utilizado pelos Saiyajins para medir o Poder de Luta "
            "dos inimigos. Mostra o nível de poder do oponente antes da luta."
        ),
        price_zeni=2000,
        item_type=ItemType.EQUIPMENT,
        effect={"scan_enemy": True},
        max_stack=1,
    ),
    "weighted_clothing": Item(
        id="weighted_clothing",
        name="Roupa com Pesos (Weighted Clothing)",
        description=(
            "Roupas extremamente pesadas como as usadas por Goku e Piccolo. "
            "Enquanto equipada, todos os ganhos de treinamento são DOBRADOS."
        ),
        price_zeni=15000,
        item_type=ItemType.EQUIPMENT,
        effect={"training_multiplier": 2.0},
        max_stack=1,
    ),
    "gravity_belt": Item(
        id="gravity_belt",
        name="Cinto de Gravidade (Gravity Belt)",
        description=(
            "Dispositivo portátil da Capsule Corp que simula gravidade 50G "
            "ao redor do corpo. Permite treinamento de gravidade em qualquer lugar."
        ),
        price_zeni=50000,
        item_type=ItemType.EQUIPMENT,
        effect={"portable_gravity": 50},
        max_stack=1,
    ),
    "capsule_house": Item(
        id="capsule_house",
        name="Capsule House (Casa-Cápsula)",
        description=(
            "Uma casa portátil da Capsule Corp. Ao usar, define o ponto de "
            "respawn do jogador na localização atual."
        ),
        price_zeni=8000,
        item_type=ItemType.CONSUMABLE,
        effect={"set_respawn": True},
        max_stack=5,
    ),
    "dragon_radar": Item(
        id="dragon_radar",
        name="Dragon Radar",
        description=(
            "O radar construído por Bulma para localizar as Esferas do Dragão. "
            "Essencial para completar a busca e invocar Shenron."
        ),
        price_zeni=100000,
        item_type=ItemType.EQUIPMENT,
        effect={"locate_dragon_balls": True},
        max_stack=1,
    ),
    "z_sword": Item(
        id="z_sword",
        name="Z-Sword (Espada Z)",
        description=(
            "A espada lendária cravada no Planeta Sagrado dos Kaioshins. "
            "Aumenta a Força em 20% enquanto equipada."
        ),
        price_zeni=200000,
        item_type=ItemType.EQUIPMENT,
        effect={"stat_boost": {"strength_percent": 20}},
        max_stack=1,
    ),
    "battle_armor": Item(
        id="battle_armor",
        name="Armadura de Batalha Saiyajin",
        description=(
            "A armadura elástica usada pelo exército de Freeza e Vegeta. "
            "Aumenta a Defesa em 30% enquanto equipada."
        ),
        price_zeni=150000,
        item_type=ItemType.EQUIPMENT,
        effect={"stat_boost": {"defense_percent": 30}},
        max_stack=1,
    ),
    "flying_nimbus": Item(
        id="flying_nimbus",
        name="Nuvem Voadora (Flying Nimbus)",
        description=(
            "A nuvem mágica que só carrega os puros de coração. "
            "Aumenta a velocidade de movimento em 50% enquanto equipada."
        ),
        price_zeni=25000,
        item_type=ItemType.EQUIPMENT,
        effect={"stat_boost": {"speed_percent": 50}},
        max_stack=1,
    ),

    # ── Itens Especiais (Uso Único / Efeito Permanente) ──────────────────
    "sacred_water": Item(
        id="sacred_water",
        name="Água Sagrada (Sacred Water)",
        description=(
            "Água ultra-rara do fundo da Torre de Korin. Ao beber, concede "
            "um bônus PERMANENTE de +500 a Força, Defesa e Agilidade. Uso único."
        ),
        price_zeni=500000,
        item_type=ItemType.SPECIAL,
        effect={"permanent_stat_boost": {"strength": 500, "defense": 500, "agility": 500}},
        max_stack=1,
    ),
    "potara_earring": Item(
        id="potara_earring",
        name="Brinco Potara (Potara Earring)",
        description=(
            "Brinco sagrado dos Kaioshins usado para fusão permanente. "
            "Item necessário para a mecânica de Fusão Potara com outro jogador."
        ),
        price_zeni=1000000,
        item_type=ItemType.SPECIAL,
        effect={"fusion_type": "potara"},
        max_stack=1,
    ),
}


# ==============================================================================
# FUNÇÕES DA LOJA E INVENTÁRIO
# ==============================================================================

def get_shop_catalog() -> Dict[str, Item]:
    """
    Retorna o catálogo completo de itens disponíveis na loja.

    Returns:
        Dicionário com todos os itens do catálogo (id → Item).
    """
    return ITEM_CATALOG


def get_inventory(inventory: Inventory) -> Dict[str, int]:
    """
    Retorna o conteúdo do inventário do jogador.

    Args:
        inventory: Objeto Inventory do jogador.

    Returns:
        Dicionário de item_id → quantidade.
    """
    return inventory.items


def buy_item(
    player: PlayerStats,
    inventory: Inventory,
    item_id: str,
    quantity: int = 1,
) -> Tuple[bool, str, PlayerStats, Inventory]:
    """
    Tenta comprar um item da loja.

    Validações realizadas:
        1. O item existe no catálogo.
        2. A quantidade solicitada é válida (>= 1).
        3. O jogador possui Zeni suficiente.
        4. O inventário não excederá o max_stack do item.

    Args:
        player: Dados atuais do jogador.
        inventory: Inventário atual do jogador.
        item_id: ID do item a ser comprado.
        quantity: Quantidade a ser comprada (padrão 1).

    Returns:
        Tupla (sucesso, mensagem, player_atualizado, inventário_atualizado).
    """
    # 1. Verifica existência no catálogo
    if item_id not in ITEM_CATALOG:
        return False, f"Item '{item_id}' não existe na loja.", player, inventory

    item = ITEM_CATALOG[item_id]

    # 2. Valida quantidade
    if quantity < 1:
        return False, "Quantidade inválida. Mínimo: 1.", player, inventory

    # 3. Calcula custo total e verifica Zeni
    total_cost = item.price_zeni * quantity
    if player.zeni < total_cost:
        return (
            False,
            f"Zeni insuficiente para comprar {quantity}x {item.name}. "
            f"Custo: {total_cost:,} Zeni, Saldo: {player.zeni:,} Zeni.",
            player,
            inventory,
        )

    # 4. Verifica limite de stack
    current_qty = inventory.items.get(item_id, 0)
    if current_qty + quantity > item.max_stack:
        return (
            False,
            f"Inventário cheio para '{item.name}'. "
            f"Máximo: {item.max_stack}, Atual: {current_qty}.",
            player,
            inventory,
        )

    # ── Realiza a compra ─────────────────────────────────────────────────

    # Deduz Zeni
    player.zeni -= total_cost

    # Adiciona ao inventário
    inventory.items[item_id] = current_qty + quantity

    return (
        True,
        f"Compra realizada! {quantity}x {item.name} adquirido(s) por "
        f"{total_cost:,} Zeni. (Saldo restante: {player.zeni:,} Zeni)",
        player,
        inventory,
    )


def use_item(
    player: PlayerStats,
    inventory: Inventory,
    item_id: str,
) -> Tuple[bool, str, PlayerStats, Inventory]:
    """
    Usa um item do inventário do jogador.

    Efeitos implementados:
        - heal_percent: Restaura % do HP máximo.
        - ki_restore_percent: Restaura % do Ki máximo.
        - set_respawn: Define ponto de respawn (consome o item).
        - permanent_stat_boost: Adiciona stats permanentes.
        - scan_enemy: Equipa o scouter (não consome).
        - Equipamentos: Alterna entre equipar/desequipar.

    Args:
        player: Dados atuais do jogador.
        inventory: Inventário atual do jogador.
        item_id: ID do item a ser usado.

    Returns:
        Tupla (sucesso, mensagem, player_atualizado, inventário_atualizado).
    """
    # Verifica existência no catálogo
    if item_id not in ITEM_CATALOG:
        return False, f"Item '{item_id}' não existe.", player, inventory

    item = ITEM_CATALOG[item_id]

    # Verifica se possui o item
    current_qty = inventory.items.get(item_id, 0)
    if current_qty <= 0:
        return (
            False,
            f"Você não possui '{item.name}' no inventário.",
            player,
            inventory,
        )

    effect = item.effect

    # ── Equipamentos: alternar equip/desequip ────────────────────────────
    if item.item_type == ItemType.EQUIPMENT:
        if item_id in inventory.equipped:
            inventory.equipped.remove(item_id)
            return (
                True,
                f"'{item.name}' desequipado.",
                player,
                inventory,
            )
        else:
            inventory.equipped.append(item_id)
            return (
                True,
                f"'{item.name}' equipado com sucesso!",
                player,
                inventory,
            )

    # ── Consumíveis e Especiais: aplicar efeito e remover do inventário ──

    messages: List[str] = []

    # Cura de HP
    if "heal_percent" in effect:
        heal_amount = player.max_health * (effect["heal_percent"] / 100.0)
        player.health = min(player.max_health, player.health + heal_amount)
        messages.append(f"HP restaurado em {effect['heal_percent']}%!")

    # Restauração de Ki
    if "ki_restore_percent" in effect:
        ki_amount = player.max_ki * (effect["ki_restore_percent"] / 100.0)
        player.ki = min(player.max_ki, player.ki + ki_amount)
        messages.append(f"Ki restaurado em {effect['ki_restore_percent']}%!")

    # Definir ponto de respawn
    if "set_respawn" in effect:
        messages.append("Ponto de respawn definido na localização atual!")

    # Bônus permanente de atributos
    if "permanent_stat_boost" in effect:
        boost = effect["permanent_stat_boost"]
        if "strength" in boost:
            player.strength += boost["strength"]
            messages.append(f"Força +{boost['strength']} (permanente)!")
        if "defense" in boost:
            player.defense += boost["defense"]
            messages.append(f"Defesa +{boost['defense']} (permanente)!")
        if "agility" in boost:
            player.agility += boost["agility"]
            messages.append(f"Agilidade +{boost['agility']} (permanente)!")

    # Remove o item do inventário (consumíveis e especiais)
    inventory.items[item_id] = current_qty - 1
    if inventory.items[item_id] <= 0:
        del inventory.items[item_id]

    final_message = f"'{item.name}' usado! " + " | ".join(messages)
    return True, final_message, player, inventory
