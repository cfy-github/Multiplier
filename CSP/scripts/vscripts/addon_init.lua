print ( '[[MULTIPLIER]] start' )
--[[ This chunk of code forces the reloading of all modules when we reload script.
if g_reloadState == nil then
	g_reloadState = {}
	for k,v in pairs( package.loaded ) do
		g_reloadState[k] = v
	end
else
	for k,v in pairs( package.loaded ) do
		if g_reloadState[k] == nil then
			package.loaded[k] = nil
		end
	end
end]]


local doneFake = false
Convars:RegisterCommand('fake', function(name, skillName, slotNumber)
    -- Check if the server ran it
    --if not Convars:GetCommandClient() then
        -- Stop fake from being run more than once
        if doneFake then return end
        doneFake = true

        -- Create fake Players
        SendToServerConsole('dota_create_fake_clients')

        -- Spawn heroes for the fake players
        Timers:CreateTimer(function()
            -- Loop over all players
            for i=0, 9 do
                -- Only affect fake clients
                if PlayerResource:IsFakeClient(i) then
                    -- Grab player instance
                    local ply = PlayerResource:GetPlayer(i)

                    -- Make sure we actually found a player instance
                    if ply then
                        CreateHeroForPlayer('npc_dota_hero_viper', ply)
                    end
                end
            end
        end, 'assign_fakes', 0.1)
    --end
end, 'Adds fake players', 0)



local function loadModule(name)
    local status, err = pcall(function()
        -- Load the module
        require(name)
    end)

    if not status then
        -- Tell the user about it
        print('WARNING: '..name..' failed to load!')
        print(err)
    end
end

loadModule ( 'util' )
loadModule ( 'physics' )
loadModule ( 'multiplier')
loadModule ( 'skillmanager')