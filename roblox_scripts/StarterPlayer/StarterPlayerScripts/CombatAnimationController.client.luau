--[[
    ========================================================================
    DRAGON BALL COMBAT ANIMATION & M1 COMBO CONTROLLER
    Localização: StarterPlayer -> StarterPlayerScripts -> CombatAnimationController.client.luau
    ========================================================================
    Tecnologias de Mercado:
    - Sistema M1 Combo de 4 Golpes (Jab -> Direto -> Gancho -> Chute Giratório Finalizador)
    - Reset de combo após 1.2 segundos sem bater
    - Impulso cinético frontal (BodyVelocity / LinearVelocity) a cada golpe
    - Integração direta com o sistema de câmera e efeitos sonoros
]]

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local player = Players.LocalPlayer
local mouse = player:GetMouse()

local comboStep = 1
local lastHitTime = 0
local isAttacking = false
local COMBO_RESET_TIME = 1.1

-- Sons de impacto e socos sintetizados
local SWING_SOUND_IDS = {
    "rbxassetid://9114223175", -- Whoosh 1
    "rbxassetid://9114223352", -- Whoosh 2
    "rbxassetid://9114223528", -- Whoosh 3
    "rbxassetid://9114223704"  -- Heavy Finisher Whoosh
}

local function playSwingSound(root, step)
    local sound = Instance.new("Sound")
    sound.SoundId = SWING_SOUND_IDS[step] or SWING_SOUND_IDS[1]
    sound.Volume = 0.8
    sound.PlaybackSpeed = 0.95 + (step * 0.05)
    sound.Parent = root
    sound:Play()
    Debris:AddItem(sound, 1.5)
end

-- ==============================================================================
-- IMPULSO CINÉTICO FRONTAL DO GOLPE
-- ==============================================================================
local function applyLungeImpulse(character, forceAmount)
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    
    local forward = root.CFrame.LookVector
    local vel = Instance.new("BodyVelocity")
    vel.MaxForce = Vector3.new(1e5, 0, 1e5)
    vel.Velocity = forward * forceAmount
    vel.Parent = root
    Debris:AddItem(vel, 0.12)
end

-- ==============================================================================
-- CRIAÇÃO DO RASTRO DE ENERGIA / SWING TRAIL
-- ==============================================================================
local function createSwingTrail(character, armName, color)
    local arm = character:FindFirstChild(armName)
    if not arm then return end

    local a0 = Instance.new("Attachment", arm)
    a0.Position = Vector3.new(0, -0.8, 0)
    local a1 = Instance.new("Attachment", arm)
    a1.Position = Vector3.new(0, 0.8, 0)

    local trail = Instance.new("Trail")
    trail.Attachment0 = a0
    trail.Attachment1 = a1
    trail.Color = ColorSequence.new(color or Color3.fromRGB(255, 255, 255))
    trail.Transparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.2),
        NumberSequenceKeypoint.new(1, 1)
    })
    trail.Lifetime = 0.2
    trail.Parent = arm

    task.delay(0.25, function()
        trail:Destroy()
        a0:Destroy()
        a1:Destroy()
    end)
end

-- ==============================================================================
-- EXECUÇÃO DO GOLPE M1
-- ==============================================================================
local function performM1Attack()
    local char = player.Character
    if not char then return end
    local humanoid = char:FindFirstChild("Humanoid")
    local root = char:FindFirstChild("HumanoidRootPart")
    if not humanoid or humanoid.Health <= 0 or not root then return end

    if isAttacking then return end
    isAttacking = true

    -- Verifica reset de combo por tempo
    local now = os.clock()
    if (now - lastHitTime) > COMBO_RESET_TIME then
        comboStep = 1
    end
    lastHitTime = now

    local currentStep = comboStep
    local isFinisher = (currentStep == 4)

    -- Impulso frontal maior no golpe finalizador
    local lungeForce = isFinisher and 45 or 22
    applyLungeImpulse(char, lungeForce)

    -- Som de golpe
    playSwingSound(root, currentStep)

    -- Efeitos visuais do braço/perna correspondente
    local arm = (currentStep % 2 == 1) and "Right Arm" or "Left Arm"
    if currentStep == 4 then arm = "Right Leg" end
    createSwingTrail(char, arm, isFinisher and Color3.fromRGB(255, 170, 0) or Color3.fromRGB(180, 220, 255))

    -- Câmera e Tremor Cinematográfico
    if _G.DragonBallCamera then
        if isFinisher then
            _G.DragonBallCamera.addTrauma(0.55)
            _G.DragonBallCamera.setDynamicFOV(62, 0.15)
            task.delay(0.25, function()
                _G.DragonBallCamera.resetFOV(0.35)
            end)
        else
            _G.DragonBallCamera.addTrauma(0.18)
        end
    end

    -- Hitbox e Detecção de Dano local
    local hitboxOrigin = root.CFrame * CFrame.new(0, 0, -3.5)
    local overlapParams = OverlapParams.new()
    overlapParams.FilterDescendantsInstances = {char}
    overlapParams.FilterType = RaycastFilterType.Exclude

    local hits = Workspace:GetPartBoundsInBox(hitboxOrigin, Vector3.new(5, 5, 5), overlapParams)
    local processedHumanoids = {}

    for _, part in ipairs(hits) do
        local enemyModel = part.Parent
        local enemyHum = enemyModel and enemyModel:FindFirstChild("Humanoid")
        if enemyHum and enemyHum ~= humanoid and not processedHumanoids[enemyHum] then
            processedHumanoids[enemyHum] = true
            
            -- Efeito de Hitstop
            if _G.DragonBallCamera then
                _G.DragonBallCamera.triggerHitstop(0.06)
            end

            -- Partículas de impacto
            local impactPart = Instance.new("Part")
            impactPart.Size = Vector3.new(0.5, 0.5, 0.5)
            impactPart.CFrame = part.CFrame
            impactPart.Anchored = true
            impactPart.CanCollide = false
            impactPart.Transparency = 1
            impactPart.Parent = Workspace

            local impactSpark = Instance.new("ParticleEmitter")
            impactSpark.Color = ColorSequence.new(Color3.fromRGB(255, 220, 100))
            impactSpark.Rate = 0
            impactSpark.Speed = NumberRange.new(15, 30)
            impactSpark.SpreadAngle = Vector2.new(180, 180)
            impactSpark.Lifetime = NumberRange.new(0.1, 0.25)
            impactSpark.Parent = impactPart
            impactSpark:Emit(18)
            Debris:AddItem(impactPart, 0.5)
            break
        end
    end

    -- Avança o passo do combo
    if isFinisher then
        comboStep = 1
        task.wait(0.4) -- Cooldown pós-finalizador
    else
        comboStep = comboStep + 1
        task.wait(0.22) -- Intervalo rápido entre golpes
    end

    isAttacking = false
end

-- Botão Esquerdo do Mouse ativa o golpe M1
UserInputService.InputBegan:Connect(function(input, processed)
    if processed then return end
    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        performM1Attack()
    end
end)

print("[COMBAT] Sistema de Combate M1 e Animações Cinematográficas ativo!")
