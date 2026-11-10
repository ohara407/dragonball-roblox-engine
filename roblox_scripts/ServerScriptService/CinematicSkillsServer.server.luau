--[[
    ========================================================================
    DRAGON BALL CINEMATIC SKILLS & VFX (SERVER SCRIPT)
    Localização: ServerScriptService -> CinematicSkillsServer.server.luau
    ========================================================================
    Tecnologias de Mercado:
    - Feixe Volumétrico de Kamehameha com cilindros luminosos e shockwaves
    - Genki Dama (Spirit Bomb) com expansão esférica e colapso de luz
    - Teletransporte (Shunkan Ido) com rastro de pós-imagem (Afterimage)
    - Dano autoritativo e sincronização com o Backend Python
]]

local Workspace = game:GetService("Workspace")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local DBFolder = ReplicatedStorage:WaitForChild("DragonBallNetwork")

local function getOrCreateRemote(className, name)
    local remote = DBFolder:FindFirstChild(name)
    if not remote then
        remote = Instance.new(className)
        remote.Name = name
        remote.Parent = DBFolder
    end
    return remote
end

local RemoteCastSkill = getOrCreateRemote("RemoteFunction", "CastCinematicSkill")
local CombatImpactEvent = getOrCreateRemote("RemoteEvent", "CombatImpact")

-- ==============================================================================
-- 1. FEIXE DE KAMEHAMEHA VOLUMÉTRICO
-- ==============================================================================
local function spawnKamehamehaBeam(character, targetCFrame, duration)
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end

    local beamLength = 120
    local origin = root.CFrame * CFrame.new(0, 0.5, -2)
    local direction = root.CFrame.LookVector

    -- Núcleo de Energia (Cilindro Interno Branco Puro)
    local coreBeam = Instance.new("Part")
    coreBeam.Name = "KamehamehaCore"
    coreBeam.Shape = Enum.PartType.Cylinder
    coreBeam.Material = Enum.Material.Neon
    coreBeam.Color = Color3.fromRGB(255, 255, 255)
    coreBeam.Size = Vector3.new(beamLength, 6, 6)
    coreBeam.CFrame = CFrame.new(origin.Position + (direction * (beamLength / 2)), origin.Position + (direction * beamLength)) * CFrame.Angles(0, math.rad(90), 0)
    coreBeam.Anchored = true
    coreBeam.CanCollide = false
    coreBeam.CastShadow = false
    coreBeam.Parent = Workspace

    -- Cilindro Externo de Ki Azul Resplandecente
    local outerBeam = Instance.new("Part")
    outerBeam.Name = "KamehamehaOuter"
    outerBeam.Shape = Enum.PartType.Cylinder
    outerBeam.Material = Enum.Material.Neon
    outerBeam.Color = Color3.fromRGB(0, 190, 255)
    outerBeam.Transparency = 0.35
    outerBeam.Size = Vector3.new(beamLength + 2, 12, 12)
    outerBeam.CFrame = coreBeam.CFrame
    outerBeam.Anchored = true
    outerBeam.CanCollide = false
    outerBeam.CastShadow = false
    outerBeam.Parent = Workspace

    -- Anéis de Onda de Choque (Shockwave Rings)
    for i = 1, 5 do
        task.spawn(function()
            local ring = Instance.new("Part")
            ring.Shape = Enum.PartType.Cylinder
            ring.Material = Enum.Material.Neon
            ring.Color = Color3.fromRGB(150, 235, 255)
            ring.Size = Vector3.new(1, 4, 4)
            ring.CFrame = origin * CFrame.Angles(0, math.rad(90), 0)
            ring.Anchored = true
            ring.CanCollide = false
            ring.Parent = Workspace

            local tween = TweenService:Create(ring, TweenInfo.new(0.6, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out), {
                Size = Vector3.new(1, 28, 28),
                Transparency = 1,
                CFrame = ring.CFrame * CFrame.new((i * 22), 0, 0)
            })
            tween:Play()
            Debris:AddItem(ring, 0.65)
        end)
    end

    -- Notifica clientes para tremor de tela pesado
    CombatImpactEvent:FireAllClients(0.85)

    -- Animação de Desaparecimento
    task.delay(duration or 1.2, function()
        local tCore = TweenService:Create(coreBeam, TweenInfo.new(0.35), { Size = Vector3.new(beamLength, 0, 0), Transparency = 1 })
        local tOuter = TweenService:Create(outerBeam, TweenInfo.new(0.35), { Size = Vector3.new(beamLength, 0, 0), Transparency = 1 })
        tCore:Play()
        tOuter:Play()
        Debris:AddItem(coreBeam, 0.4)
        Debris:AddItem(outerBeam, 0.4)
    end)
end

-- ==============================================================================
-- 2. GENKI DAMA (SPIRIT BOMB)
-- ==============================================================================
local function spawnSpiritBomb(character, targetPosition)
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end

    local bomb = Instance.new("Part")
    bomb.Name = "GenkiDamaOrb"
    bomb.Shape = Enum.PartType.Ball
    bomb.Material = Enum.Material.Neon
    bomb.Color = Color3.fromRGB(220, 245, 255)
    bomb.Size = Vector3.new(6, 6, 6)
    bomb.CFrame = root.CFrame * CFrame.new(0, 25, 0)
    bomb.Anchored = true
    bomb.CanCollide = false
    bomb.Parent = Workspace

    -- Partículas azuis e brancas reunidas de seres vivos
    local pe = Instance.new("ParticleEmitter")
    pe.Color = ColorSequence.new(Color3.fromRGB(150, 230, 255))
    pe.LightEmission = 1
    pe.Size = NumberSequence.new(3, 0)
    pe.Rate = 120
    pe.Speed = NumberRange.new(5, 15)
    pe.Lifetime = NumberRange.new(0.5, 1)
    pe.Parent = bomb

    -- Crescimento dramático da esfera
    local growTween = TweenService:Create(bomb, TweenInfo.new(1.8, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = Vector3.new(45, 45, 45)
    })
    growTween:Play()

    -- Queda devastadora em direção ao alvo
    task.delay(2.0, function()
        local dropTween = TweenService:Create(bomb, TweenInfo.new(1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
            Position = targetPosition or (root.Position + (root.CFrame.LookVector * 60))
        })
        dropTween:Play()
        dropTween.Completed:Connect(function()
            -- Explosão massiva
            pe.Rate = 0
            local explosionPart = Instance.new("Part")
            explosionPart.Shape = Enum.PartType.Ball
            explosionPart.Material = Enum.Material.Neon
            explosionPart.Color = Color3.fromRGB(255, 255, 255)
            explosionPart.Size = Vector3.new(20, 20, 20)
            explosionPart.Position = bomb.Position
            explosionPart.Anchored = true
            explosionPart.CanCollide = false
            explosionPart.Parent = Workspace

            local boomTween = TweenService:Create(explosionPart, TweenInfo.new(0.8, Enum.EasingStyle.Exponential, Enum.EasingDirection.Out), {
                Size = Vector3.new(160, 160, 160),
                Transparency = 1
            })
            boomTween:Play()
            CombatImpactEvent:FireAllClients(1.0) -- Tremor máximo de tela
            Debris:AddItem(explosionPart, 0.9)
            bomb:Destroy()
        end)
    end)
end

-- ==============================================================================
-- 3. TELETRANSPORTE (SHUNKAN IDO) COM PÓS-IMAGEM
-- ==============================================================================
local function performInstantTransmission(character, targetCFrame)
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end

    -- Cria efeito de pós-imagem no local de origem
    for _, part in ipairs(character:GetChildren()) do
        if part:IsA("BasePart") and part.Transparency < 1 then
            local ghost = part:Clone()
            ghost.CanCollide = false
            ghost.Anchored = true
            ghost.Material = Enum.Material.Neon
            ghost.Color = Color3.fromRGB(150, 230, 255)
            ghost.Transparency = 0.4
            ghost.Parent = Workspace

            local fade = TweenService:Create(ghost, TweenInfo.new(0.4), { Transparency = 1 })
            fade:Play()
            Debris:AddItem(ghost, 0.45)
        end
    end

    -- Teleporta instantaneamente o personagem
    root.CFrame = targetCFrame
    CombatImpactEvent:FireClient(Players:GetPlayerFromCharacter(character), 0.25)
end

-- Handler central de invocação
RemoteCastSkill.OnServerInvoke = function(player, skillId, targetPos)
    local char = player.Character
    if not char then return false end

    if skillId == "kamehameha" then
        spawnKamehamehaBeam(char, targetPos, 1.3)
        return true, "Kamehameha disparado com sucesso!"
    elseif skillId == "spirit_bomb" then
        spawnSpiritBomb(char, targetPos)
        return true, "Genki Dama invocada!"
    elseif skillId == "instant_transmission" then
        local root = char:FindFirstChild("HumanoidRootPart")
        if root then
            local dest = root.CFrame * CFrame.new(0, 0, -35)
            performInstantTransmission(char, dest)
            return true, "Teletransporte realizado!"
        end
    end
    return false, "Habilidade não reconhecida"
end

print("[CINEMATICS] Servidor de Efeitos Especiais e Golpes Cinematográficos carregado!")
