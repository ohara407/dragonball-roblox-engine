--[[
    ========================================================================
    DRAGON BALL ROBLOX <-> PYTHON BRIDGE (SERVER SCRIPT)
    Localização recomendada no Roblox Studio:
    ServerScriptService -> DragonBallBackendBridge.server.luau
    ========================================================================
    Este script é o coração da integração no lado do servidor Roblox.
    Ele utiliza o HttpService para se comunicar diretamente com a API Python (FastAPI).
]]

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- URL do Servidor Python FastAPI (ajuste a porta ou use Ngrok se for hospedar na nuvem)
local BACKEND_URL = "http://127.0.0.1:8000"

-- Configuração de pastas e RemoteEvents no ReplicatedStorage
local DBFolder = ReplicatedStorage:FindFirstChild("DragonBallNetwork")
if not DBFolder then
    DBFolder = Instance.new("Folder")
    DBFolder.Name = "DragonBallNetwork"
    DBFolder.Parent = ReplicatedStorage
end

local function getOrCreateRemote(className, name)
    local remote = DBFolder:FindFirstChild(name)
    if not remote then
        remote = Instance.new(className)
        remote.Name = name
        remote.Parent = DBFolder
    end
    return remote
end

local RemoteSyncStats = getOrCreateRemote("RemoteEvent", "SyncStats")
local RemoteTrain = getOrCreateRemote("RemoteFunction", "RequestTrain")
local RemoteTransform = getOrCreateRemote("RemoteFunction", "RequestTransform")
local RemoteRevert = getOrCreateRemote("RemoteFunction", "RequestRevert")
local RemoteChargeKi = getOrCreateRemote("RemoteEvent", "ChargeKi")
local RemoteCompleteQuest = getOrCreateRemote("RemoteFunction", "CompleteQuest")

-- Cache em memória dos jogadores logados
local PlayerSessionData = {}

-- Função auxiliar para requisições HTTP seguras
local function HttpRequest(endpoint, method, payload)
    local url = BACKEND_URL .. endpoint
    local headers = {
        ["Content-Type"] = "application/json",
        ["Accept"] = "application/json"
    }
    
    local options = {
        Url = url,
        Method = method or "GET",
        Headers = headers,
        Body = payload and HttpService:JSONEncode(payload) or nil
    }

    local success, response = pcall(function()
        return HttpService:RequestAsync(options)
    end)

    if success and response.Success then
        local decodeSuccess, decoded = pcall(function()
            return HttpService:JSONDecode(response.Body)
        end)
        if decodeSuccess then
            return true, decoded
        end
    end
    
    warn("[DB-BRIDGE] Falha ao comunicar com Python Backend em: " .. url)
    return false, nil
end

-- ==============================================================================
-- CICLO DE VIDA DO JOGADOR (JOIN / LEAVE)
-- ==============================================================================

local function onPlayerAdded(player)
    print("[DB-BRIDGE] Conectando jogador: " .. player.Name .. " (UserId: " .. player.UserId .. ")")
    
    -- Busca ou cria o perfil no Python FastAPI
    local success, data = HttpRequest("/api/player/" .. player.UserId .. "?username=" .. HttpService:UrlEncode(player.Name), "GET")
    
    if success and data then
        PlayerSessionData[player.UserId] = data
        print("[DB-BRIDGE] Perfil carregado com sucesso! Poder de Luta: " .. tostring(data.power_level))
    else
        -- Fallback local se o backend não responder imediatamente
        warn("[DB-BRIDGE] Usando dados locais de contingência para " .. player.Name)
        PlayerSessionData[player.UserId] = {
            user_id = player.UserId,
            username = player.Name,
            power_level = 100,
            health = 1000,
            max_health = 1000,
            ki = 500,
            max_ki = 500,
            strength = 20,
            defense = 20,
            agility = 20,
            zeni = 100,
            current_transformation = nil,
            unlocked_transformations = {"kaioken"}
        }
    end

    -- Sincroniza com o cliente
    RemoteSyncStats:FireClient(player, PlayerSessionData[player.UserId])
end

local function onPlayerRemoving(player)
    PlayerSessionData[player.UserId] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- ==============================================================================
-- HANDLERS DE EVENTOS DE REDE (TREINO, TRANSFORMAÇÃO, KI)
-- ==============================================================================

-- Treinamento (Flexões, Meditação, Sala do Tempo, Gravidade)
RemoteTrain.OnServerInvoke = function(player, trainingType, duration)
    local endpoint = "/api/player/" .. player.UserId .. "/train"
    local payload = {
        training_type = trainingType or "pushups",
        duration_seconds = duration or 5
    }
    
    local success, response = HttpRequest(endpoint, "POST", payload)
    if success and response.success then
        PlayerSessionData[player.UserId] = response.player
        RemoteSyncStats:FireClient(player, response.player)
        return true, response.message, response.extra_data
    end
    return false, "Falha ao processar treino no backend", nil
end

-- Ativação de Transformação
RemoteTransform.OnServerInvoke = function(player, formId)
    local endpoint = "/api/player/" .. player.UserId .. "/transform"
    local payload = {
        transformation_id = formId
    }
    
    local success, response = HttpRequest(endpoint, "POST", payload)
    if success and response.success then
        PlayerSessionData[player.UserId] = response.player
        RemoteSyncStats:FireClient(player, response.player)
        
        -- Aplica atributos físicos no Humanoid do Roblox
        local char = player.Character
        if char then
            local humanoid = char:FindFirstChild("Humanoid")
            if humanoid then
                local trans = response.extra_data and response.extra_data.transformation
                local mult = trans and trans.multiplier or 1
                humanoid.WalkSpeed = 16 + math.min(100, mult * 2)
            end
        end
        
        return true, response.message, response.extra_data
    end
    
    local errMsg = response and response.message or "Erro de comunicação ao transformar"
    return false, errMsg, nil
end

-- Reverter Transformação para Forma Base
RemoteRevert.OnServerInvoke = function(player)
    local endpoint = "/api/player/" .. player.UserId .. "/revert"
    local success, response = HttpRequest(endpoint, "POST", {})
    if success and response.success then
        PlayerSessionData[player.UserId] = response.player
        RemoteSyncStats:FireClient(player, response.player)
        
        local char = player.Character
        if char then
            local humanoid = char:FindFirstChild("Humanoid")
            if humanoid then
                humanoid.WalkSpeed = 16
            end
        end
        return true, "Forma base restaurada"
    end
    return false, "Falha ao reverter forma"
end

-- Carregar Ki contínuo
RemoteChargeKi.OnServerEvent:Connect(function(player, amount)
    local session = PlayerSessionData[player.UserId]
    if session then
        session.ki = math.min(session.max_ki, session.ki + (amount or 20))
        -- Notifica cliente
        RemoteSyncStats:FireClient(player, session)
    end
end)

-- Concluir Missão
RemoteCompleteQuest.OnServerInvoke = function(player, questId)
    local endpoint = "/api/player/" .. player.UserId .. "/complete_quest"
    local payload = { quest_id = questId }
    local success, response = HttpRequest(endpoint, "POST", payload)
    if success and response.success then
        PlayerSessionData[player.UserId] = response.player
        RemoteSyncStats:FireClient(player, response.player)
        return true, response.message
    end
    return false, response and response.message or "Erro ao concluir missão"
end

-- ==============================================================================
-- LOOP TICK DE DRENAGEM DE KI DAS TRANSFORMAÇÕES
-- ==============================================================================
task.spawn(function()
    while true do
        task.wait(1.5)
        for _, player in ipairs(Players:GetPlayers()) do
            local session = PlayerSessionData[player.UserId]
            if session and session.current_transformation then
                local endpoint = "/api/player/" .. player.UserId .. "/drain_tick?delta_time=1.5"
                local success, response = HttpRequest(endpoint, "POST", {})
                if success and response.success then
                    PlayerSessionData[player.UserId] = response.player
                    RemoteSyncStats:FireClient(player, response.player)
                    
                    if response.extra_data and response.extra_data.reverted then
                        -- Reverte velocidade do personagem
                        local char = player.Character
                        if char and char:FindFirstChild("Humanoid") then
                            char.Humanoid.WalkSpeed = 16
                        end
                    end
                end
            end
        end
    end
end)

print("[DB-BRIDGE] Dragon Ball Backend Bridge iniciado e escutando requisições!")
