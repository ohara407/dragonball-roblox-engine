"""
Módulo de Integração com Google Gemini AI
Utilizado para:
- Geração procedural de roteiros de animação (Keyframes, Easing, VFX)
- Geração de prompts e concept art para personagens, auras e cenários
- Diálogos inteligentes de NPCs e chefes de saga (Raditz, Freeza, Cell, Jiren)
- Geração procedural de missões e balanceamento dinâmico
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# Obtém chave da variável de ambiente ou arquivo .env local
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Tenta carregar do .env caso não esteja nas variáveis do sistema
if not GEMINI_API_KEY:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    GEMINI_API_KEY = line.strip().split("=", 1)[1].strip("\"' ")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


class GeminiAIEngine:
    """Motor de IA generativa do Google para o jogo Dragon Ball Roblox."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            print("[AVISO] GEMINI_API_KEY não configurada. Operando em modo de simulação/fallback.")

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Chama a API REST do Google Gemini de forma direta e sem dependências externas."""
        if not self.api_key:
            return self._fallback_response(prompt)

        url = f"{GEMINI_API_URL}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return "Sem resposta gerada pelo modelo."
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[ERRO HTTP {e.code}] Gemini API: {err_body}")
            return self._fallback_response(prompt)
        except Exception as e:
            print(f"[ERRO] Falha ao comunicar com Gemini: {e}")
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Resposta de fallback com designs e dados pré-calculados de alto nível."""
        return (
            "/* [MODO OFFLINE / RESPOSTA PRÉ-DEFINIDA] */\n"
            "// Animação calculada com base no padrão Dragon Ball Studio:\n"
            "// Keyframes: Charge (0-1.2s), Flash (1.2-1.5s), Blast (1.5-3.0s)\n"
            "// VFX: Emitter.Rate = 120, Speed = 45, Color = ColorSequence.new(Color3.fromRGB(0, 200, 255))\n"
        )

    # =========================================================================
    # GERAÇÃO DE DESIGN DE ANIMAÇÃO PARA ROBLOX
    # =========================================================================

    def generate_animation_script(self, skill_or_form: str) -> Dict[str, Any]:
        """Gera especificações completas de animação e partículas no Roblox para um golpe ou transformação."""
        system_prompt = (
            "Você é o Diretor Técnico Chefe de Animação e Efeitos Visuais (VFX) da Toei Animation "
            "e especialista em Roblox Luau. Sua função é desenhar a anatomia visual de animações de "
            "Dragon Ball com especificações de keyframes, curvas de easing, tempos de carga e parâmetros "
            "de ParticleEmitter para Roblox Studio. Responda em formato estruturado (JSON quando solicitado)."
        )
        user_prompt = f"""
        Gere as especificações completas de animação e efeitos visuais no Roblox Studio para:
        "{skill_or_form}".

        Inclua:
        1. Fases da Animação (Preparação, Carga, Disparo, Impacto/Finalização) com tempos em segundos.
        2. Posturas do esqueleto R15 (Root, Torso, Right Arm, Left Arm, Head).
        3. Configurações exatas do Roblox ParticleEmitter (ColorSequence, LightEmission, Size, Rate, Speed, Lifetime).
        4. Efeitos de câmera (CameraShake: amplitude, frequência, duração).
        5. Efeitos sonoros recomendados (Sound IDs conceituais e modulação de pitch).
        """
        result = self._call_gemini(user_prompt, system_prompt)
        return {
            "target": skill_or_form,
            "design_specs": result,
            "engine": "Google Gemini 1.5 Flash"
        }

    # =========================================================================
    # GERAÇÃO DE DIÁLOGOS DE CHEFES E NPCs
    # =========================================================================

    def generate_boss_dialogue(self, boss_name: str, player_power: int, boss_power: int, situation: str) -> str:
        """Gera falas canônicas e dinâmicas dos vilões durante as lutas."""
        system_prompt = (
            "Você é o roteirista oficial dos jogos de Dragon Ball. Gere falas icônicas, "
            "dramáticas e fiéis à personalidade de cada personagem do universo Dragon Ball."
        )
        user_prompt = f"""
        Personagem: {boss_name}
        Poder do Jogador: {player_power:,} PL
        Poder do Chefe: {boss_power:,} PL
        Situação de Combate: {situation} (Ex: Início da luta, jogador se transformou em Super Saiyajin, chefe com vida baixa, vitória do chefe).

        Gere 3 falas curtas e impactantes para o chat do Roblox que façam o jogador arrepiar!
        """
        return self._call_gemini(user_prompt, system_prompt)

    # =========================================================================
    # GERAÇÃO PROCEDURAL DE MISSÕES DIÁRIAS
    # =========================================================================

    def generate_daily_quest(self, player_level: int, player_form: str) -> Dict[str, Any]:
        """Cria uma missão procedural exclusiva para o jogador com auxílio da IA."""
        system_prompt = "Você é o gerador procedural de missões do Dragon Ball RPG. Retorne um objeto JSON válido."
        user_prompt = f"""
        Gere uma missão procedural única de Dragon Ball para um guerreiro no Nível {player_level} com a forma {player_form}.
        Retorne em formato JSON:
        {{
            "title": "Título épico da missão",
            "saga": "Nome da saga correspondente",
            "description": "História e objetivo imersivo",
            "objective_type": "defeat_boss | train_gravity | collect_dragonballs",
            "target": "Nome do alvo ou local",
            "reward_exp": 1000,
            "reward_zeni": 5000,
            "lore_quote": "Citação motivacional de Mestre Kame ou Senhor Kaioh"
        }}
        """
        raw = self._call_gemini(user_prompt, system_prompt)
        try:
            # Limpa blocos de código se presentes
            clean = raw.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            return json.loads(clean.strip())
        except Exception:
            return {
                "title": f"Desafio dos Deuses para {player_form}",
                "saga": "Treino Especial de Bills",
                "description": raw,
                "reward_exp": player_level * 500,
                "reward_zeni": player_level * 1000
            }


if __name__ == "__main__":
    ai = GeminiAIEngine()
    print("Testando Gemini AI Engine...")
    anim = ai.generate_animation_script("Kamehameha Carregado em Super Saiyajin Blue")
    print(anim["design_specs"][:500] + "...")
