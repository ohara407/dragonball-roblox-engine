"""
Dragon Ball RPG - Simulador Completo em Python (Terminal / CLI)
Permite testar e jogar toda a mecânica de treinamento, transformações e missões
diretamente pelo terminal Python antes ou em conjunto com a integração do Roblox!
"""
import sys
import os
import time
import random

# Importa motor do backend
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend_api"))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from models import PlayerStats, TrainingType
from engine import (
    TRANSFORMATIONS_CATALOG, QUESTS_CATALOG,
    process_training, transform_player, revert_transformation,
    drain_ki_tick, charge_ki, apply_zenkai_boost, recalculate_power_level
)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print("""
========================================================================
   ____  ____     _    ____  ___  _   _   ____    _    _     _     
  |  _ \|  _ \   / \  / ___|/ _ \| \ | | | __ )  / \  | |   | |    
  | | | | |_) | / _ \| |  _| | | |  \| | |  _ \ / _ \ | |   | |    
  | |_| |  _ < / ___ \ |_| | |_| | |\  | | |_) / ___ \| |___| |___ 
  |____/|_| \_\_/   \_\____|\___/|_| \_| |____/_/   \_\_____|_____|
               INTEGRAÇÃO PYTHON <-> ROBLOX ENGINE
========================================================================
""")

def display_hud(player: PlayerStats):
    form_display = player.current_transformation.upper() if player.current_transformation else "FORMA BASE"
    print("-" * 72)
    print(f" Guerreiro: {player.username:<18} | Nível: {player.level:<4} | Zeni: ¥{player.zeni:,}")
    print(f" Estado: [{form_display}] | Poder de Luta: {player.power_level:,} PL")
    print(f" Vida: {int(player.health)}/{int(player.max_health)} | Ki: {int(player.ki)}/{int(player.max_ki)} | Zenkai: {player.zenkai_count}x")
    print(f" Força: {player.strength} | Defesa: {player.defense} | Agilidade: {player.agility}")
    print("-" * 72)

def menu_train(player: PlayerStats):
    print("\n[ SELECIONE O TIPO DE TREINAMENTO ]")
    print("1. Flexões e Agachamentos (Físico: +Força e +Defesa)")
    print("2. Treino de Sombras (Shadow Boxing: +Agilidade e +Ki)")
    print("3. Meditação no Pico das Nuvens (+Max Ki e Regeneração)")
    print("4. Sala de Gravidade (100G) (+Ganhos Massivos em Tudo)")
    print("5. Sala do Tempo Hiperbólica (+Evolução Extrema)")
    print("0. Voltar")
    
    escolha = input("\nEscolha sua rotina de treino: ")
    tipo_map = {
        "1": TrainingType.PUSHUPS,
        "2": TrainingType.SHADOW_BOXING,
        "3": TrainingType.MEDITATION,
        "4": TrainingType.GRAVITY_CHAMBER,
        "5": TrainingType.HYPERBOLIC_TIME
    }
    
    if escolha in tipo_map:
        print("\nTreinando intensamente...", end="")
        for _ in range(3):
            time.sleep(0.4)
            print(".", end="", flush=True)
        print("\n")
        
        player, gains = process_training(player, tipo_map[escolha], duration=5)
        print(f"★ Treino concluído com sucesso!")
        print(f"  +Força: {gains['strength']} | +Defesa: {gains['defense']} | +Agilidade: {gains['agility']} | +Ki: {gains['max_ki']} | +EXP: {gains['exp']}")
        input("\nPressione [ENTER] para continuar...")

def menu_transformations(player: PlayerStats):
    print("\n[ TRANSFORMAÇÕES SAIYAJIN DISPONÍVEIS ]")
    print(f"Forma Atual: {player.current_transformation or 'Forma Base'}\n")
    
    forms = list(TRANSFORMATIONS_CATALOG.values())
    for idx, f in enumerate(forms, 1):
        unlocked = "✓ DESBLOQUEADA" if f.id in player.unlocked_transformations else f"🔒 Requer {f.min_power_level:,} PL"
        print(f"{idx}. {f.name:<28} | Mult: {f.multiplier:>6.0f}x | Dreno Ki: {f.ki_drain_per_sec:>3.0f}/s | [{unlocked}]")
    
    print("\n99. Reverter para Forma Base")
    print("0. Voltar")
    
    escolha = input("\nSelecione o número da transformação: ")
    if escolha == "99":
        player = revert_transformation(player)
        print("Você se acalmou e voltou à Forma Base.")
        time.sleep(1)
        return
    
    try:
        idx = int(escolha) - 1
        if 0 <= idx < len(forms):
            target_form = forms[idx]
            success, msg, _ = transform_player(player, target_form.id)
            print(f"\n{msg}")
            if success:
                print(f">> Uma aura resplandecente ({target_form.aura_color}) explode ao seu redor!")
            time.sleep(1.5)
    except ValueError:
        pass

def battle_enemy(player: PlayerStats, quest_id: str):
    quest = QUESTS_CATALOG[quest_id]
    print(f"\n=== ENFRENTANDO {quest.target_enemy.upper()} ===")
    print(f"Saga: {quest.saga}")
    print(f"Poder Recomendado: {quest.power_level_req:,}")
    print(f"Seu Poder Atual: {player.power_level:,}")
    
    enemy_hp = quest.power_level_req * 1.2
    max_enemy_hp = enemy_hp
    
    turn = 1
    while enemy_hp > 0 and player.health > 0:
        print(f"\n--- Turno {turn} ---")
        print(f"Sua Vida: {int(player.health)}/{int(player.max_health)} | Ki: {int(player.ki)}/{int(player.max_ki)}")
        print(f"Inimigo ({quest.target_enemy}): {int(enemy_hp)}/{int(max_enemy_hp)}")
        print("1. Ataque Básico (Soco/Chute)")
        print("2. Onda de Ki / Kamehameha (Gasta 40 Ki)")
        print("3. Carregar Ki")
        print("4. Esquivar")
        
        # Dreno de Ki por turno se transformado
        if player.current_transformation:
            player, rev = drain_ki_tick(player, delta_time=2.0)
            if rev:
                print(">> ATENÇÃO: Seu Ki se esgotou e você perdeu a transformação!")

        acao = input("Ação: ")
        
        # Turno do jogador
        dmg = 0
        if acao == "1":
            dmg = player.strength * 2 + random.randint(5, 25)
            print(f"Você desferiu uma sequência de golpes causando {dmg} de dano!")
        elif acao == "2":
            if player.ki >= 40:
                player.ki -= 40
                dmg = player.strength * 5 + int(player.ki * 0.5) + random.randint(50, 150)
                print(f"KAMEHAMEHAAAA! Uma explosão de energia causa {dmg} de dano massivo!")
            else:
                print("Ki insuficiente! Seu ataque falhou.")
        elif acao == "3":
            player = charge_ki(player, amount=60.0)
            print(f"Você concentrou sua energia! Ki atual: {int(player.ki)}/{int(player.max_ki)}")
        elif acao == "4":
            print("Você assume postura defensiva para esquivar do próximo golpe.")
            dmg = 0
            
        enemy_hp -= dmg
        if enemy_hp <= 0:
            break
            
        # Turno do Inimigo
        print(f"\n{quest.target_enemy} avança para contra-atacar!")
        enemy_dmg = max(10, int((quest.power_level_req * 0.05) - (player.defense * 0.3)))
        if acao == "4" and random.random() < (player.agility / (player.agility + 50)):
            print(f">> Você se esquivou com extrema agilidade graças ao seu reflexo!")
        else:
            player.health -= enemy_dmg
            print(f">> {quest.target_enemy} atingiu você causando {enemy_dmg} de dano!")
            
        if player.health <= 0:
            break
        turn += 1

    if player.health > 0:
        print(f"\n★★ VITÓRIA! {quest.target_enemy} foi derrotado! ★★")
        player.completed_quests.append(quest.id)
        player.exp += quest.reward_exp
        player.zeni += quest.reward_zeni
        print(f"Recompensas: +{quest.reward_exp} EXP | +¥{quest.reward_zeni} Zeni")
        if quest.reward_form and quest.reward_form not in player.unlocked_transformations:
            player.unlocked_transformations.append(quest.reward_form)
            form_info = TRANSFORMATIONS_CATALOG[quest.reward_form]
            print(f"★ DESBLOQUEIO LENDÁRIO: Você desbloqueou a forma [{form_info.name}]! ★")
    else:
        print(f"\nXX Derrota... Você caiu em combate. XX")
        print("Os curandeiros cuidaram de você...")
        # Zenkai Boost ao se recuperar
        player, boost = apply_zenkai_boost(player)
        print(f">> O sangue Saiyajin reage! ZENKAI BOOST ativado: +{boost} em atributos!")
        player.health = player.max_health
        player.ki = player.max_ki
        
    input("\nPressione [ENTER] para continuar...")

def menu_quests(player: PlayerStats):
    print("\n[ SAGAS E MISSÕES DE DRAGON BALL ]")
    for idx, (qid, q) in enumerate(QUESTS_CATALOG.items(), 1):
        status = "✓ CONCLUÍDA" if qid in player.completed_quests else f"Poder Req: {q.power_level_req:,}"
        reward_f = f" | Desbloqueia: {TRANSFORMATIONS_CATALOG[q.reward_form].name}" if q.reward_form else ""
        print(f"{idx}. [{q.saga}] {q.title}")
        print(f"   Inimigo: {q.target_enemy} | [{status}]{reward_f}")
    
    print("\n0. Voltar")
    escolha = input("\nEscolha a missão para iniciar a batalha: ")
    try:
        idx = int(escolha) - 1
        keys = list(QUESTS_CATALOG.keys())
        if 0 <= idx < len(keys):
            battle_enemy(player, keys[idx])
    except ValueError:
        pass

def main():
    clear()
    print_banner()
    nome = input("Digite o nome do seu guerreiro Saiyajin: ").strip() or "Kakarotto"
    player = PlayerStats(user_id=1, username=nome, power_level=200, strength=25, defense=20, agility=20)
    
    while True:
        player.power_level = recalculate_power_level(player)
        clear()
        print_banner()
        display_hud(player)
        
        print("\n[ MENU PRINCIPAL ]")
        print("1. Treinar Atributos (Flexões, Gravidade, Meditação)")
        print("2. Menu de Transformações (SSJ 1-3, Deus, Blue, Instinto Superior)")
        print("3. Missões e Sagas (Raditz, Freeza, Cell, Buu, Jiren)")
        print("4. Carregar Ki ao Máximo")
        print("0. Sair do Jogo")
        
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            menu_train(player)
        elif opcao == "2":
            menu_transformations(player)
        elif opcao == "3":
            menu_quests(player)
        elif opcao == "4":
            player = charge_ki(player, amount=player.max_ki)
            print("Ki carregado com sucesso!")
            time.sleep(0.8)
        elif opcao == "0":
            print("\nObrigado por jogar Dragon Ball Roblox Engine! Até a próxima batalha!")
            break

if __name__ == "__main__":
    main()
