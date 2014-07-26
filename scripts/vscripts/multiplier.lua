USE_LOBBY=false
THINK_TIME = 0.1
ADDON_NAME="MULTIPLIER"

STARTING_GOLD = 1000--650
MAX_LEVEL = 25

-- Fill this table up with the required XP per level if you want to change it
XP_PER_LEVEL_TABLE = {}
for i=1,MAX_LEVEL do
  XP_PER_LEVEL_TABLE[i] = i * 100
end

GameMode = nil

function Log(msg)
  print ( '['..ADDON_NAME..'] '..msg )
end

if MultiplierGameMode == nil then
  Log('creating multiplier game mode' )
  MultiplierGameMode = {}
  MultiplierGameMode.szEntityClassName = "multiplier"
  MultiplierGameMode.szNativeClassName = "dota_base_game_mode"
  MultiplierGameMode.__index = MultiplierGameMode
end

function MultiplierGameMode:new( o )
  Log('MultiplierGameMode:new' )
  o = o or {}
  setmetatable( o, MultiplierGameMode )
  return o
end

function MultiplierGameMode:InitGameMode()
  Log('Starting to load Barebones gamemode...')

  -- Setup rules
  GameRules:SetHeroRespawnEnabled( true )
  GameRules:SetUseUniversalShopMode( false )
  GameRules:SetSameHeroSelectionEnabled( false )
  GameRules:SetHeroSelectionTime( 30.0 )
  GameRules:SetPreGameTime( 30.0)
  GameRules:SetPostGameTime( 60.0 )
  GameRules:SetTreeRegrowTime( 60.0 )
  GameRules:SetUseCustomHeroXPValues ( false )
  GameRules:SetGoldPerTick(2)
  Log('Rules set')

  InitLogFile( "log/multiplier.txt","")

  -- Hooks
  ListenToGameEvent('modifier_event', Dynamic_Wrap(MultiplierGameMode, 'OnModifierEvent'), self)
  ListenToGameEvent('hero_picker_hidden', Dynamic_Wrap(MultiplierGameMode, 'OnHeroPickerHidden'), self)  
  ListenToGameEvent('entity_killed', Dynamic_Wrap(MultiplierGameMode, 'OnEntityKilled'), self)
  ListenToGameEvent('player_connect_full', Dynamic_Wrap(MultiplierGameMode, 'AutoAssignPlayer'), self)
  ListenToGameEvent('player_disconnect', Dynamic_Wrap(MultiplierGameMode, 'CleanupPlayer'), self)
  ListenToGameEvent('dota_item_purchased', Dynamic_Wrap(MultiplierGameMode, 'ShopReplacement'), self)
  ListenToGameEvent('player_say', Dynamic_Wrap(MultiplierGameMode, 'PlayerSay'), self)
  ListenToGameEvent('player_connect', Dynamic_Wrap(MultiplierGameMode, 'PlayerConnect'), self)
  --ListenToGameEvent('player_info', Dynamic_Wrap(MultiplierGameMode, 'PlayerInfo'), self)
  ListenToGameEvent('dota_player_used_ability', Dynamic_Wrap(MultiplierGameMode, 'AbilityUsed'), self)

  Convars:RegisterCommand( "command_example", Dynamic_Wrap(MultiplierGameMode, 'ExampleConsoleCommand'), "A console command example", 0 )
  
  -- Fill server with fake clients
  Convars:RegisterCommand('fake', function()
    -- Check if the server ran it
    if not Convars:GetCommandClient() or DEBUG then
      -- Create fake Players
      SendToServerConsole('dota_create_fake_clients')
        
      self:CreateTimer('assign_fakes', {
        endTime = Time(),
        callback = function(multiplier, args)
          for i=0, 9 do
            -- Check if this player is a fake one
            if PlayerResource:IsFakeClient(i) then
              -- Grab player instance
              local ply = PlayerResource:GetPlayer(i)
              -- Make sure we actually found a player instance
              if ply then
                CreateHeroForPlayer('npc_dota_hero_axe', ply)
              end
            end
          end
        end})
    end
  end, 'Connects and assigns fake Players.', 0)

  -- Change random seed
  local timeTxt = string.gsub(string.gsub(GetSystemTime(), ':', ''), '0','')
  math.randomseed(tonumber(timeTxt))
  
  

  -- Timers
  self.timers = {}

  -- userID map
  self.vUserNames = {}
  self.vUserIds = {}
  self.vSteamIds = {}
  self.vBots = {}
  self.vBroadcasters = {}

  self.vPlayers = {}
  self.vRadiant = {}
  self.vDire = {}
  
   -- Stores the current skill list for each hero
  self.currentSkillList = {}

  -- Active Hero Map
  self.vPlayerHeroData = {}
  
  self:LoadAbilityList()
  
  Log('values set')
  

  Log('Precaching stuff...')
  PrecacheUnitByName('npc_precache_everything')
  Log('Done precaching!') 

  Log('Done loading Barebones gamemode!\n\n')
  
  
 
end

function MultiplierGameMode:CaptureGameMode()
  if GameMode == nil then
    -- Set GameMode parameters
    GameMode = GameRules:GetGameModeEntity()		
    -- Disables recommended items...though I don't think it works
    GameMode:SetRecommendedItemsDisabled( true )
    -- Override the normal camera distance.  Usual is 1134
    GameMode:SetCameraDistanceOverride( 1504.0 )
    -- Set Buyback options
    GameMode:SetCustomBuybackCostEnabled( true )
    GameMode:SetCustomBuybackCooldownEnabled( true )
    GameMode:SetBuybackEnabled( false )
    -- Override the top bar values to show your own settings instead of total deaths
    GameMode:SetTopBarTeamValuesOverride ( true )
    -- Use custom hero level maximum and your own XP per level
    GameMode:SetUseCustomHeroLevels ( true )
    GameMode:SetCustomHeroMaxLevel ( MAX_LEVEL )
    GameMode:SetCustomXPRequiredToReachNextLevel( XP_PER_LEVEL_TABLE )
    -- Chage the minimap icon size
    GameRules:SetHeroMinimapIconSize( 300 )

    Log('Beginning Think' ) 
    GameMode:SetContextThink("BarebonesThink", Dynamic_Wrap( MultiplierGameMode, 'Think' ), 0.1 )
	
	
  end 
end

function MultiplierGameMode:AbilityUsed(keys)
  Log('AbilityUsed')
  PrintTable(keys)
end

-- Stick skills into slots
local handled = {}
ListenToGameEvent('npc_spawned', function(keys)
    -- Grab the unit that spawned
    local spawnedUnit = EntIndexToHScript(keys.entindex)

    -- Make sure it is a hero
    if spawnedUnit:IsHero() then
        -- Don't touch this hero more than once :O
        if handled[spawnedUnit] then return end
        handled[spawnedUnit] = true

        -- Grab their playerID
        local playerID = spawnedUnit:GetPlayerID()

        -- Don't touch bots
        if PlayerResource:IsFakeClient(playerID) then return end

        -- Grab their build
        --local build = skillList[playerID] or {}

        -- Apply the build
		
		--PrintTable(SkillManager)
		--PrintTable(getmetatable(SkillManager))
		SkillManager:ApplyBuildMultiplier(spawnedUnit)
		
    end
end, nil)

function MultiplierGameMode:OnHeroPickerHidden(keys)
  Log('OnHeroPickerHidden')
  PrintTable(keys)
end

-- Cleanup a player when they leave
function MultiplierGameMode:CleanupPlayer(keys)
  Log('Player Disconnected ' .. tostring(keys.userid))
end

function MultiplierGameMode:CloseServer()
  -- Just exit
  SendToServerConsole('exit')
end

function MultiplierGameMode:PlayerConnect(keys)
  Log('PlayerConnect')
  PrintTable(keys)
  
  -- Fill in the usernames for this userID
  self.vUserNames[keys.userid] = keys.name
  if keys.bot == 1 then
    -- This user is a Bot, so add it to the bots table
    self.vBots[keys.userid] = 1
  end
end

local hook = nil
local attach = 0
local controlPoints = {}
local particleEffect = ""

function MultiplierGameMode:PlayerSay(keys)
  Log('PlayerSay')
  PrintTable(keys)
  
  -- Get the player entity for the user speaking
  local ply = self.vUserIds[keys.userid]
  if ply == nil then
    return
  end
  
  -- Get the player ID for the user speaking
  local plyID = ply:GetPlayerID()
  if not PlayerResource:IsValidPlayer(plyID) then
    return
  end
  
  -- Should have a valid, in-game player saying something at this point
  -- The text the person said
  local text = keys.text
  
  -- Match the text against something
  local matchA, matchB = string.match(text, "^-swap%s+(%d)%s+(%d)")
  if matchA ~= nil and matchB ~= nil then
    -- Act on the match
  end
  
end

function MultiplierGameMode:AutoAssignPlayer(keys)
  Log('AutoAssignPlayer')
  PrintTable(keys)
  MultiplierGameMode:CaptureGameMode()
  
  local entIndex = keys.index+1
  -- The Player entity of the joining user
  local ply = EntIndexToHScript(entIndex)
  
  -- The Player ID of the joining player
  local playerID = ply:GetPlayerID()
  
  -- Update the user ID table with this user
  self.vUserIds[keys.userid] = ply
  -- Update the Steam ID table
  self.vSteamIds[PlayerResource:GetSteamAccountID(playerID)] = ply
  
  -- If the player is a broadcaster flag it in the Broadcasters table
  if PlayerResource:IsBroadcaster(playerID) then
    self.vBroadcasters[keys.userid] = 1
    return
  end
  
  -- If this player is a bot (spectator) flag it and continue on
  if self.vBots[keys.userid] ~= nil then
    return
  end

  
  playerID = ply:GetPlayerID()
  -- Figure out if this player is just reconnecting after a disconnect
  if self.vPlayers[playerID] ~= nil then
    self.vUserIds[keys.userid] = ply
    return
  end
  
  -- If we're not on D2MODD.in, assign players round robin to teams
  if not USE_LOBBY and playerID == -1 then
    if #self.vRadiant > #self.vDire then
      ply:SetTeam(DOTA_TEAM_BADGUYS)
      ply:__KeyValueFromInt('teamnumber', DOTA_TEAM_BADGUYS)
      table.insert (self.vDire, ply)
    else
      ply:SetTeam(DOTA_TEAM_GOODGUYS)
      ply:__KeyValueFromInt('teamnumber', DOTA_TEAM_GOODGUYS)
      table.insert (self.vRadiant, ply)
    end
    playerID = ply:GetPlayerID()
  end

  --Autoassign player
  self:CreateTimer('assign_player_'..entIndex, {
  endTime = Time(),
  callback = function(multiplier, args)
    -- Make sure the game has started
    if GameRules:State_Get() >= DOTA_GAMERULES_STATE_PRE_GAME then
      -- Assign a hero to a fake client
      local heroEntity = ply:GetAssignedHero()
      if PlayerResource:IsFakeClient(playerID) then
        if heroEntity == nil then
          CreateHeroForPlayer('npc_dota_hero_axe', ply)
        else
          PlayerResource:ReplaceHeroWith(playerID, 'npc_dota_hero_axe', 0, 0)
        end
      end
      heroEntity = ply:GetAssignedHero()
      -- Check if we have a reference for this player's hero
      if heroEntity ~= nil and IsValidEntity(heroEntity) then
        -- Set up a heroTable containing the state for each player to be tracked
        local heroTable = {
          hero = heroEntity,
          nTeam = ply:GetTeam(),
          bRoundInit = false,
          name = self.vUserNames[keys.userid],
        }
        self.vPlayers[playerID] = heroTable

        if GameRules:State_Get() > DOTA_GAMERULES_STATE_PRE_GAME then
            -- This section runs if the player picks a hero after the round starts
        end

        return
      end
    end

    return Time() + 1.0
  end
})
end

function MultiplierGameMode:FindHeroOwner(skillName)
    local heroOwner = ""
    for heroName, values in pairs(self.heroListKV) do
        if type(values) == "table" then
            for i = 1, 16 do
                if values["Ability"..i] == skillName then
                    heroOwner = heroName
                    goto foundHeroName
                end
            end
        end
    end

    ::foundHeroName::
    return heroOwner
end

function MultiplierGameMode:LoadAbilityList()
    local abs = LoadKeyValues("scripts/kv/abilities.kv")
    self.heroListKV = LoadKeyValues("scripts/npc/npc_heroes.txt")
    self.customItemKV = LoadKeyValues("scripts/npc/npc_items_custom.txt")
    self.subAbilities = LoadKeyValues("scripts/kv/abilityDeps.kv")

    -- Build list of heroes
    self.heroList = {}
    self.heroListEnabled = {}
    for heroName, values in pairs(self.heroListKV) do
        -- Validate hero name
        if heroName ~= 'Version' and heroName ~= 'npc_dota_hero_base' and heroName ~= 'npc_dota_hero_abyssal_underlord' then
            -- Make sure the hero is enabled
            if values.Enabled == 1 then
                -- Store this unit
                table.insert(self.heroList, heroName)
                self.heroListEnabled[heroName] = 1
            end
        end
    end

    -- Table containing every skill
    self.vAbList = {}
    self.vAbListSort = {}
    self.vAbListLookup = {}

    -- Build skill list
    for k,v in pairs(abs) do
        for kk, vv in pairs(v) do
            -- This comparison is really dodgy for some reason
            if tonumber(vv) == 1 then
                -- Attempt to find the owning hero of this ability
                local heroOwner = self:FindHeroOwner(kk)

                -- Store this skill
                table.insert(self.vAbList, {
                    name = kk,
                    sort = k,
                    hero = heroOwner
                })

                -- Store into the sort container
                if not self.vAbListSort[k] then
                    self.vAbListSort[k] = {}
                end

                -- Store the sort reference
                table.insert(self.vAbListSort[k], kk)

                -- Store the reverse lookup
                self.vAbListLookup[kk] = k
            end
        end
    end
end

function MultiplierGameMode:IsValidPlayerID(checkPlayerID)
    local isValid = false
    self:LoopOverPlayers(function(ply, playerID)
        if playerID == checkPlayerID then
            isValid = true
            return true
        end
    end)

    return isValid
end

function MultiplierGameMode:ApplyBuild(hero, build)
    if hero == nil then
        Say(nil, COLOR_RED..'WARNING: Failed to apply a build!', false)
        return
    end

    -- Grab playerID
    local playerID = hero:GetPlayerID()
    if not self:IsValidPlayerID(playerID) then
        return
    end

    -- Remove all the skills from our hero
    self:RemoveAllSkills(hero)

    -- Table to store all the extra skills we need to give
    local extraSkills = {}

    -- Give all the abilities in this build
    for k,v in ipairs(build) do
        -- Check if this skill has sub abilities
        if self.subAbilities[v] then
            -- Store that we need this skill
            extraSkills[self.subAbilities[v]] = true
        end

        -- Add to build
        hero:AddAbility(v)
        self.currentSkillList[hero][k] = v
    end

    -- Add missing abilities
    local i = #build+1
    for k,v in pairs(extraSkills) do
        -- Add the ability
        hero:AddAbility(k)

        -- Store that we have it
        self.currentSkillList[hero][i] = k

        -- Move onto the next slot
        i = i + 1
    end
end

function MultiplierGameMode:GetRandomAbility(sort)
    if not sort or not self.vAbListSort[sort] then
        sort = 'Abs'
    end

    return self.vAbListSort[sort][math.random(1, #self.vAbListSort[sort])]
end


function MultiplierGameMode:RemoveAllSkills( hero )
	Log('RemoveAllSkills: ')
	hero:SetGold(hero:GetGold() + 10, false)
	
	-- Check if we've touched this hero before
    if not self.currentSkillList[hero] then
        -- Grab the name of this hero
        local heroClass = hero:GetUnitName()

        local skills = self:GetHeroSkills(heroClass)

        -- Store it
        self.currentSkillList[hero] = skills
    end

    -- Remove all old skills
    for k,v in pairs(self.currentSkillList[hero]) do
        if hero:HasAbility(v) then
            hero:RemoveAbility(v)
        end
    end
	
end

function MultiplierGameMode:GetHeroSkills(heroClass)
    local skills = {}

    -- Build list of abilities
    for heroName, values in pairs(self.heroListKV) do
        if heroName == heroClass then
            for i = 1, 16 do
                local ab = values["Ability"..i]
                if ab and ab ~= 'attribute_bonus' then
                    table.insert(skills, ab)
                end
            end
        end
    end

    return skills
end

function MultiplierGameMode:LoopOverPlayers(callback)
  for k, v in pairs(self.vPlayers) do
    -- Validate the player
    if IsValidEntity(v.hero) then
      -- Run the callback
      if callback(v, v.hero:GetPlayerID()) then
        break
      end
    end
  end
end

function MultiplierGameMode:ShopReplacement( keys )
  Log('ShopReplacement' )
  PrintTable(keys)
  Log('Replacing ' .. keys.itemname .. ' with: item_shadow_amulet' )

  -- The playerID of the hero who is buying something
  local plyID = keys.PlayerID
  if not plyID then return end
  
  local player = self.vPlayers[plyID]
  if not player then return end

  -- The name of the item purchased
  local itemName = keys.itemname 
    
  -- The cost of the item purchased
  local itemcost = keys.itemcost
  
  local item = self:getItemByName(player.hero, keys.itemname)
  if not item then return end
  
  print ( item:GetAbilityName())
  --player.hero:SetGold(itemcost, true)
  --item:Remove()
  
  --local v = player.hero
  --local item2 = CreateItem('item_shadow_amulet', v, v)
  --v:AddItem(item2)
  
end

function MultiplierGameMode:getItemByName( hero, name )
  -- Find item by slot
  for i=0,11 do
    local item = hero:GetItemInSlot( i )
    if item ~= nil then
      local lname = item:GetAbilityName()
      if lname == name then
        return item
      end
    end
  end

  return nil
end

function MultiplierGameMode:Think()
  -- If the game's over, it's over.
  if GameRules:State_Get() >= DOTA_GAMERULES_STATE_POST_GAME then
    return
  end

  -- Track game time, since the dt passed in to think is actually wall-clock time not simulation time.
  local now = GameRules:GetGameTime()
  --Log('time: ' .. now)
  if MultiplierGameMode.t0 == nil then
    MultiplierGameMode.t0 = now
  end
  local dt = now - MultiplierGameMode.t0
  MultiplierGameMode.t0 = now

  --MultiplierGameMode:thinkState( dt )

  -- Process timers
  for k,v in pairs(MultiplierGameMode.timers) do
    local bUseGameTime = false
    if v.useGameTime and v.useGameTime == true then
      bUseGameTime = true;
    end
    -- Check if the timer has finished
    if (bUseGameTime and GameRules:GetGameTime() > v.endTime) or (not bUseGameTime and Time() > v.endTime) then
      -- Remove from timers list
      MultiplierGameMode.timers[k] = nil

      -- Run the callback
      local status, nextCall = pcall(v.callback, MultiplierGameMode, v)

      -- Make sure it worked
      if status then
        -- Check if it needs to loop
        if nextCall then
          -- Change it's end time
          v.endTime = nextCall
          MultiplierGameMode.timers[k] = v
        end

      else
        -- Nope, handle the error
        MultiplierGameMode:HandleEventError('Timer', k, nextCall)
      end
    end
  end

  return THINK_TIME
end

function MultiplierGameMode:HandleEventError(name, event, err)
  -- This gets fired when an event throws an error

  -- Log to console
  print(err)

  -- Ensure we have data
  name = tostring(name or 'unknown')
  event = tostring(event or 'unknown')
  err = tostring(err or 'unknown')

  -- Tell everyone there was an error
  Say(nil, name .. ' threw an error on event '..event, false)
  Say(nil, err, false)

  -- Prevent loop arounds
  if not self.errorHandled then
    -- Store that we handled an error
    self.errorHandled = true
  end
end

function MultiplierGameMode:CreateTimer(name, args)
  --[[
  args: {
  endTime = Time you want this timer to end: Time() + 30 (for 30 seconds from now),
  useGameTime = use Game Time instead of Time()
  callback = function(frota, args) to run when this timer expires,
  text = text to display to clients,
  send = set this to true if you want clients to get this,
  persist = bool: Should we keep this timer even if the match ends?
  }

  If you want your timer to loop, simply return the time of the next callback inside of your callback, for example:

  callback = function()
  return Time() + 30 -- Will fire again in 30 seconds
  end
  ]]

  if not args.endTime or not args.callback then
    print("Invalid timer created: "..name)
    return
  end

  -- Store the timer
  self.timers[name] = args
end

function MultiplierGameMode:RemoveTimer(name)
  -- Remove this timer
  self.timers[name] = nil
end

function MultiplierGameMode:RemoveTimers(killAll)
  local timers = {}

  -- If we shouldn't kill all timers
  if not killAll then
    -- Loop over all timers
    for k,v in pairs(self.timers) do
      -- Check if it is persistant
      if v.persist then
        -- Add it to our new timer list
        timers[k] = v
      end
    end
  end

  -- Store the new batch of timers
  self.timers = timers
end

function MultiplierGameMode:ExampleConsoleCommand()
  print( '******* Example Console Command ***************' )
  local cmdPlayer = Convars:GetCommandClient()
  if cmdPlayer then
    local playerID = cmdPlayer:GetPlayerID()
    if playerID ~= nil and playerID ~= -1 then
      -- Do something here for the player who called this command
    end
  end

  print( '*********************************************' )
end

function MultiplierGameMode:OnModifierEvent( keys )
  Log('OnModifierEvent Called' )
  PrintTable( keys )
  

  -- Put code here to handle when an entity gets killed
end

function MultiplierGameMode:OnEntityKilled( keys )
  --Log('OnEntityKilled Called' )
  --PrintTable( keys )
  
  -- The Unit that was Killed
  local killedUnit = EntIndexToHScript( keys.entindex_killed )
  -- The Killing entity
  local killerEntity = nil

  if keys.entindex_attacker ~= nil then
    killerEntity = EntIndexToHScript( keys.entindex_attacker )
  end

  -- Put code here to handle when an entity gets killed
end

-- A helper function for dealing damage from a source unit to a target unit.  Damage dealt is pure damage
function dealDamage(source, target, damage)
  local unit = nil
  if damage == 0 then
    return
  end
  
  if source ~= nil then
    unit = CreateUnitByName("npc_dummy_unit", target:GetAbsOrigin(), false, source, source, source:GetTeamNumber())
  else
    unit = CreateUnitByName("npc_dummy_unit", target:GetAbsOrigin(), false, nil, nil, DOTA_TEAM_NOTEAM)
  end
  unit:AddNewModifier(unit, nil, "modifier_invulnerable", {})
  unit:AddNewModifier(unit, nil, "modifier_phased", {})
  local dummy = unit:FindAbilityByName("reflex_dummy_unit")
  dummy:SetLevel(1)
  
  local abilIndex = math.floor((damage-1) / 20) + 1
  local abilLevel = math.floor(((damage-1) % 20)) + 1
  if abilIndex > 100 then
    abilIndex = 100
    abilLevel = 20
  end
  
  local abilityName = "modifier_damage_applier" .. abilIndex
  unit:AddAbility(abilityName)
  ability = unit:FindAbilityByName( abilityName )
  ability:SetLevel(abilLevel)
  
  local diff = nil
  
  local hp = target:GetHealth()
  
  diff = target:GetAbsOrigin() - unit:GetAbsOrigin()
  diff.z = 0
  unit:SetForwardVector(diff:Normalized())
  unit:CastAbilityOnTarget(target, ability, 0 )
  
  MultiplierGameMode:CreateTimer(DoUniqueString("damage"), {
    endTime = GameRules:GetGameTime() + 0.3,
    useGameTime = true,
    callback = function(multiplier, args)
      unit:Destroy()
      if target:GetHealth() == hp and hp ~= 0 and damage ~= 0 then
        Log("WARNING: dealDamage did no damage: " .. hp)
        dealDamage(source, target, damage)
      end
    end
  })
end
