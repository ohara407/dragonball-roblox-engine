--[[
    ========================================================================
    DRAGON BALL CAMERA CINEMATICS & TRAUMA SHAKE CONTROLLER
    Localização: StarterPlayer -> StarterPlayerScripts -> CameraCinematicsController.client.luau
    ========================================================================
    Tecnologias de Mercado Utilizadas (Padrão The Strongest Battlegrounds / Deepwoken):
    - Sistema de Trauma de Câmera baseado em Perlin Noise (Trauma^2 / Trauma^3 decay)
    - FOV Dinâmico (Zoom in na carga de Ki/Kamehameha, Snap Zoom out no disparo)
    - Flash de Impacto e Efeito de Hitstop (Pausa dramática de impacto)
]]

local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local camera = Workspace.CurrentCamera
local player = Players.LocalPlayer

-- Parâmetros do Sistema de Trauma
local trauma = 0
local MAX_ANGLE = 8        -- Graus máximos de rotação por tremor
local MAX_OFFSET = 1.2      -- Studs máximos de deslocamento
local DECAY_RATE = 1.4     -- Velocidade de decaimento por segundo
local FREQUENCY = 25       -- Frequência do Perlin Noise

local defaultFOV = 70
local currentFOV = defaultFOV

-- Pasta de Rede
local DBFolder = ReplicatedStorage:WaitForChild("DragonBallNetwork", 10)

local CameraCinematics = {}

-- ==============================================================================
-- SISTEMA DE TREMOR DE CÂMERA (PERLIN NOISE TRAUMA SHAKE)
-- ==============================================================================

function CameraCinematics.addTrauma(amount)
    trauma = math.clamp(trauma + (amount or 0.3), 0, 1.0)
end

function CameraCinematics.setDynamicFOV(targetFOV, duration, easingStyle)
    local tweenInfo = TweenInfo.new(
        duration or 0.35,
        easingStyle or Enum.EasingStyle.Cubic,
        Enum.EasingDirection.Out
    )
    local tween = TweenService:Create(camera, tweenInfo, { FieldOfView = targetFOV })
    tween:Play()
end

function CameraCinematics.resetFOV(duration)
    CameraCinematics.setDynamicFOV(defaultFOV, duration or 0.4, Enum.EasingStyle.Exponential)
end

-- ==============================================================================
-- IMPACT FREEZE (HITSTOP DRAMÁTICO)
-- ==============================================================================

function CameraCinematics.triggerHitstop(duration)
    local freezeTime = duration or 0.06
    local char = player.Character
    if char and char:FindFirstChild("Humanoid") then
        local humanoid = char.Humanoid
        local originalSpeed = humanoid.WalkSpeed
        humanoid.WalkSpeed = 0
        task.delay(freezeTime, function()
            if humanoid then
                humanoid.WalkSpeed = originalSpeed
            end
        end)
    end
end

-- ==============================================================================
-- CICLO RENDERSTEPPED DE CÂMERA
-- ==============================================================================

local timeElapsed = 0

RunService.RenderStepped:Connect(function(dt)
    if trauma > 0 then
        timeElapsed = timeElapsed + dt * FREQUENCY
        
        -- Trauma elevado ao quadrado produz resposta exponencial suave e realista
        local shakeFactor = trauma * trauma

        local yaw = MAX_ANGLE * shakeFactor * (math.noise(timeElapsed, 0, 0))
        local pitch = MAX_ANGLE * shakeFactor * (math.noise(0, timeElapsed, 0))
        local roll = (MAX_ANGLE * 0.5) * shakeFactor * (math.noise(0, 0, timeElapsed))

        local offsetX = MAX_OFFSET * shakeFactor * (math.noise(timeElapsed + 10, 0, 0))
        local offsetY = MAX_OFFSET * shakeFactor * (math.noise(0, timeElapsed + 10, 0))
        local offsetZ = (MAX_OFFSET * 0.5) * shakeFactor * (math.noise(0, 0, timeElapsed + 10))

        camera.CFrame = camera.CFrame 
            * CFrame.Angles(math.rad(pitch), math.rad(yaw), math.rad(roll))
            * CFrame.new(offsetX, offsetY, offsetZ)

        -- Decaimento linear do trauma
        trauma = math.clamp(trauma - (DECAY_RATE * dt), 0, 1.0)
    end
end)

-- Escuta eventos de impacto se disponíveis na rede
if DBFolder then
    local impactEvent = DBFolder:FindFirstChild("CombatImpact")
    if impactEvent then
        impactEvent.OnClientEvent:Connect(function(impactIntensity)
            CameraCinematics.addTrauma(impactIntensity or 0.4)
            CameraCinematics.triggerHitstop(0.05)
        end)
    end
end

-- Exporta globalmente para outros scripts do cliente
_G.DragonBallCamera = CameraCinematics

print("[CINEMATICS] Motor de Câmera e Tremor Cinematográfico ativado com sucesso!")
return CameraCinematics
