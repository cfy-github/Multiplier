--[[
    Skill Managing Library for swapping skills during runtime
]]

-- Keeps track of what skills a given hero has
local currentSkillList = {}

-- Contains info on heroes
local heroListKV = LoadKeyValues("scripts/npc/npc_heroes.txt")

-- Contains custom abilities
local abilitiesListCustomKV = LoadKeyValues("scripts/npc/npc_abilities_custom.txt")

-- This object will be exported
local skillManager = {}


local abilitiesListCustom = {}
for skillName, values in pairs(abilitiesListCustomKV) do
	--print("Load Skill: " .. skillName)
	abilitiesListCustom[skillName] = true
end

-- Tells you if a given skill is in custom list
local function isCustomSkill(skill)
    if abilitiesListCustom[skill] then
        return true
    end

    return false
end


function skillManager:GetHeroSkills(heroClass)
    local skills = {}

    -- Build list of abilities
    for heroName, values in pairs(heroListKV) do
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


function skillManager:RemoveAllSkills(hero)
    -- Ensure the hero isn't nil
	if hero == nil then return end
	-- Check if we've touched this hero before
    if not currentSkillList[hero] then
        -- Grab the name of this hero
        local heroClass = hero:GetUnitName()
		
        -- Grab the skills
        local skills = self:GetHeroSkills(heroClass)
		
        -- Store it
        currentSkillList[hero] = skills
    end

    -- Remove all old skills
    for k,v in pairs(currentSkillList[hero]) do
        if hero:HasAbility(v) then
			--Log('remove: ' .. v)
            hero:RemoveAbility(v)
        end
    end
end



function skillManager:ApplyMultiplier(hero, factor)
    -- Ensure the hero isn't nil
	--Log('ApplySimpleBuild2')
    if hero == nil then return end
  
    -- Give all the abilities in this build
    local abNum = 0
	local heroClass = hero:GetUnitName()
	local skills = self:GetHeroSkills(heroClass)
	local newSkills = {}
    for i=1,12 do
        local v = skills[i]
        if v then
            abNum=abNum+1

			mab = v .. '_x' .. factor
			if isCustomSkill(mab) then
				hero:RemoveAbility(v)			

				-- Add to build
				hero:AddAbility(mab)
				table.insert(newSkills, mab)

			else
				table.insert(newSkills, v)
				--Log('ignore ' .. v)
			end

        end
    end
	currentSkillList[hero] = newSkills
end

-- Define the export
SkillManager = skillManager