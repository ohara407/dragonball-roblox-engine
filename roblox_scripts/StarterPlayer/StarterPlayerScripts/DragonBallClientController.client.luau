--[[
    ========================================================================
    DRAGON BALL CLIENT CONTROLLER & HUD (LOCAL SCRIPT)
    Localização recomendada no Roblox Studio:
    StarterPlayer -> StarterPlayerScripts -> DragonBallClientController.client.luau
    ========================================================================
    Controles:
    - [C] (Segurar): Carregar Ki com aura visual e efeito
    - [G]: Transformar (Abre seleção ou ativa a forma mais forte)
    - [H]: Reverter para Forma Base
    - [T]: Abrir / Fechar Menu de Treinamento
    - [M]: Abrir / Fechar Menu de Missões / Sagas
]]

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local DBFolder = ReplicatedStorage:WaitForChild("DragonBallNetwork")
local RemoteSyncStats = DBFolder:WaitForChild("SyncStats")
local RemoteTrain = DBFolder:WaitForChild("RequestTrain")
local RemoteTransform = DBFolder:WaitForChild("RequestTransform")
local RemoteRevert = DBFolder:WaitForChild("RequestRevert")
local RemoteChargeKi = DBFolder:WaitForChild("ChargeKi")
local RemoteCompleteQuest = DBFolder:WaitForChild("CompleteQuest")

local CurrentStats = {
    power_level = 100,
    health = 1000,
    max_health = 1000,
    ki = 500,
    max_ki = 500,
    current_transformation = nil,
    unlocked_transformations = {"kaioken"}
}

local isChargingKi = false

-- ==============================================================================
-- CRIAÇÃO DA INTERFACE GRÁFICA HUD (GUI)
-- ==============================================================================
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "DragonBallHUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = playerGui

-- Frame Principal Inferior
local hudFrame = Instance.new("Frame")
hudFrame.Size = UDim2.new(0, 360, 0, 110)
hudFrame.Position = UDim2.new(0, 20, 1, -130)
hudFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
hudFrame.BackgroundTransparency = 0.25
hudFrame.BorderSizePixel = 0
hudFrame.Parent = screenGui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 8)
corner.Parent = hudFrame

local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(255, 170, 0)
stroke.Thickness = 2
stroke.Parent = hudFrame

-- Label de Poder de Luta e Forma
local powerLabel = Instance.new("TextLabel")
powerLabel.Size = UDim2.new(1, -20, 0, 26)
powerLabel.Position = UDim2.new(0, 10, 0, 8)
powerLabel.BackgroundTransparency = 1
powerLabel.TextColor3 = Color3.fromRGB(255, 230, 80)
powerLabel.Font = Enum.Font.GothamBold
powerLabel.TextSize = 18
powerLabel.TextXAlignment = Enum.TextXAlignment.Left
powerLabel.Text = "PODER: 100 PL | FORMA BASE"
powerLabel.Parent = hudFrame

-- Barra de Vida (Health Bar)
local hpBg = Instance.new("Frame")
hpBg.Size = UDim2.new(1, -20, 0, 18)
hpBg.Position = UDim2.new(0, 10, 0, 42)
hpBg.BackgroundColor3 = Color3.fromRGB(50, 10, 10)
hpBg.BorderSizePixel = 0
hpBg.Parent = hudFrame
Instance.new("UICorner", hpBg).CornerRadius = UDim.new(0, 4)

local hpFill = Instance.new("Frame")
hpFill.Size = UDim2.new(1, 0, 1, 0)
hpFill.BackgroundColor3 = Color3.fromRGB(230, 40, 40)
hpFill.BorderSizePixel = 0
hpFill.Parent = hpBg
Instance.new("UICorner", hpFill).CornerRadius = UDim.new(0, 4)

local hpText = Instance.new("TextLabel")
hpText.Size = UDim2.new(1, 0, 1, 0)
hpText.BackgroundTransparency = 1
hpText.TextColor3 = Color3.fromRGB(255, 255, 255)
hpText.Font = Enum.Font.GothamMedium
hpText.TextSize = 12
hpText.Text = "VIDA: 1000 / 1000"
hpText.Parent = hpBg

-- Barra de Ki (Ki Bar)
local kiBg = Instance.new("Frame")
kiBg.Size = UDim2.new(1, -20, 0, 18)
kiBg.Position = UDim2.new(0, 10, 0, 68)
kiBg.BackgroundColor3 = Color3.fromRGB(10, 30, 60)
kiBg.BorderSizePixel = 0
kiBg.Parent = hudFrame
Instance.new("UICorner", kiBg).CornerRadius = UDim.new(0, 4)

local kiFill = Instance.new("Frame")
kiFill.Size = UDim2.new(1, 0, 1, 0)
kiFill.BackgroundColor3 = Color3.fromRGB(0, 170, 255)
kiFill.BorderSizePixel = 0
kiFill.Parent = kiBg
Instance.new("UICorner", kiFill).CornerRadius = UDim.new(0, 4)

local kiText = Instance.new("TextLabel")
kiText.Size = UDim2.new(1, 0, 1, 0)
kiText.BackgroundTransparency = 1
kiText.TextColor3 = Color3.fromRGB(255, 255, 255)
kiText.Font = Enum.Font.GothamMedium
kiText.TextSize = 12
kiText.Text = "KI: 500 / 500"
kiText.Parent = kiBg

-- ==============================================================================
-- ATUALIZAÇÃO DO HUD
-- ==============================================================================
local function updateHUD()
    local formName = CurrentStats.current_transformation and string.upper(CurrentStats.current_transformation) or "FORMA BASE"
    powerLabel.Text = string.format("PODER: %s PL | %s", tostring(CurrentStats.power_level or 100), formName)
    
    local hpPct = math.clamp((CurrentStats.health or 1) / (CurrentStats.max_health or 1), 0, 1)
    hpFill.Size = UDim2.new(hpPct, 0, 1, 0)
    hpText.Text = string.format("VIDA: %d / %d", math.floor(CurrentStats.health or 1000), math.floor(CurrentStats.max_health or 1000))
    
    local kiPct = math.clamp((CurrentStats.ki or 0) / (CurrentStats.max_ki or 1), 0, 1)
    kiFill.Size = UDim2.new(kiPct, 0, 1, 0)
    kiText.Text = string.format("KI: %d / %d", math.floor(CurrentStats.ki or 500), math.floor(CurrentStats.max_ki or 500))
end

RemoteSyncStats.OnClientEvent:Connect(function(newStats)
    CurrentStats = newStats
    updateHUD()
end)

-- ==============================================================================
-- CONTROLES DE TECLADO (INPUTS)
-- ==============================================================================
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    
    -- Tecla [C]: Iniciar Carga de Ki
    if input.KeyCode == Enum.KeyCode.C then
        isChargingKi = true
    end
    
    -- Tecla [G]: Transformar (Ativa a transformação mais avançada disponível)
    if input.KeyCode == Enum.KeyCode.G then
        local formToActivate = "ssj1"
        if table.find(CurrentStats.unlocked_transformations, "ultra_instinct") then
            formToActivate = "ultra_instinct"
        elseif table.find(CurrentStats.unlocked_transformations, "ssj_blue") then
            formToActivate = "ssj_blue"
        elseif table.find(CurrentStats.unlocked_transformations, "ssj_god") then
            formToActivate = "ssj_god"
        elseif table.find(CurrentStats.unlocked_transformations, "ssj3") then
            formToActivate = "ssj3"
        elseif table.find(CurrentStats.unlocked_transformations, "ssj2") then
            formToActivate = "ssj2"
        elseif table.find(CurrentStats.unlocked_transformations, "ssj1") then
            formToActivate = "ssj1"
        elseif table.find(CurrentStats.unlocked_transformations, "kaioken") then
            formToActivate = "kaioken"
        end
        
        print("[CLIENT] Requisitando transformação: " .. formToActivate)
        local success, msg = RemoteTransform:InvokeServer(formToActivate)
        print("[CLIENT] Resultado: " .. tostring(msg))
    end
    
    -- Tecla [H]: Reverter para Base
    if input.KeyCode == Enum.KeyCode.H then
        print("[CLIENT] Revertendo para forma base...")
        RemoteRevert:InvokeServer()
    end
    
    -- Tecla [T]: Realizar Treinamento Rápido
    if input.KeyCode == Enum.KeyCode.T then
        print("[CLIENT] Iniciando treino rápido...")
        local success, msg = RemoteTrain:InvokeServer("pushups", 5)
        print("[CLIENT] Treino: " .. tostring(msg))
    end
end)

UserInputService.InputEnded:Connect(function(input, gameProcessed)
    if input.KeyCode == Enum.KeyCode.C then
        isChargingKi = false
    end
end)

-- Loop de Carga de Ki enquanto segura [C]
task.spawn(function()
    while true do
        task.wait(0.2)
        if isChargingKi then
            RemoteChargeKi:FireServer(25)
        end
    end
end)

print("[CLIENT] Dragon Ball Client Controller carregado com sucesso!")
