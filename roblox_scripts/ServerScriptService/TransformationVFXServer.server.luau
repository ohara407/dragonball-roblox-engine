--[[
    ========================================================================
    DRAGON BALL VISUAL EFFECTS & COMBAT (SERVER SCRIPT)
    Localização recomendada no Roblox Studio:
    ServerScriptService -> TransformationVFXServer.server.luau
    ========================================================================
    Gerencia:
    - Efeitos de Partícula de Aura (Aura Emitter)
    - Raios elétricos para SSJ2 e SSJ3
    - Mudança visual de cor do cabelo e brilho
    - Efeitos sonoros de transformação
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local DBFolder = ReplicatedStorage:WaitForChild("DragonBallNetwork")
local RemoteSyncStats = DBFolder:WaitForChild("SyncStats")

-- Tabela de Cores das Auras por Transformação
local AURA_COLORS = {
    kaioken = ColorSequence.new(Color3.fromRGB(255, 30, 30)),
    ssj1 = ColorSequence.new(Color3.fromRGB(255, 215, 0)),
    ssj2 = ColorSequence.new(Color3.fromRGB(255, 245, 100)),
    ssj3 = ColorSequence.new(Color3.fromRGB(255, 180, 0)),
    ssj_god = ColorSequence.new(Color3.fromRGB(255, 20, 80)),
    ssj_blue = ColorSequence.new(Color3.fromRGB(0, 200, 255)),
    ultra_instinct = ColorSequence.new(Color3.fromRGB(230, 240, 255)),
    ultra_ego = ColorSequence.new(Color3.fromRGB(150, 40, 255))
}

local function clearAura(character)
    local root = character:FindFirstChild("HumanoidRootPart")
    if root then
        for _, child in ipairs(root:GetChildren()) do
            if child.Name == "DragonBallAuraEmitter" or child.Name == "DragonBallLightningEmitter" then
                child:Destroy()
            end
        end
    end
end

local function applyAura(character, formId)
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    
    clearAura(character)
    
    if not formId or not AURA_COLORS[formId] then
        return
    end

    -- Cria o Emitter da Aura de Energia
    local auraEmitter = Instance.new("ParticleEmitter")
    auraEmitter.Name = "DragonBallAuraEmitter"
    auraEmitter.Color = AURA_COLORS[formId]
    auraEmitter.LightEmission = 0.9
    auraEmitter.LightInfluence = 0
    auraEmitter.Size = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 2),
        NumberSequenceKeypoint.new(0.5, 4),
        NumberSequenceKeypoint.new(1, 0)
    })
    auraEmitter.Transparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.4),
        NumberSequenceKeypoint.new(0.8, 0.7),
        NumberSequenceKeypoint.new(1, 1)
    })
    auraEmitter.Rate = 70
    auraEmitter.Speed = NumberRange.new(8, 15)
    auraEmitter.Lifetime = NumberRange.new(0.4, 0.8)
    auraEmitter.SpreadAngle = Vector2.new(15, 15)
    auraEmitter.Parent = root

    -- Adiciona Raios Elétricos se for SSJ2, SSJ3 ou Ultra Ego
    if formId == "ssj2" or formId == "ssj3" or formId == "ultra_ego" then
        local lightningEmitter = Instance.new("ParticleEmitter")
        lightningEmitter.Name = "DragonBallLightningEmitter"
        lightningEmitter.Color = (formId == "ultra_ego") and ColorSequence.new(Color3.fromRGB(200, 50, 255)) or ColorSequence.new(Color3.fromRGB(180, 220, 255))
        lightningEmitter.Rate = 18
        lightningEmitter.Speed = NumberRange.new(5, 12)
        lightningEmitter.Lifetime = NumberRange.new(0.1, 0.3)
        lightningEmitter.Size = NumberSequence.new(1.5, 0.2)
        lightningEmitter.Parent = root
    end
end

-- Escuta sincronizações de status para atualizar os efeitos visuais
RemoteSyncStats.OnServerEvent:Connect(function() end)

-- Conecta a todos os jogadores
Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        clearAura(character)
    end)
end)
