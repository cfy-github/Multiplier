from lib.keyvalues import KeyValues
from lib import clean
import os


force_divide = ['min_blink_range']

ignore_all_special = ['crit_chance', 'bonus_evasion', 'dodge_chance_pct', 'miss_chance', 'dodge_chance',
                    'illusion_damage_out_pct', 'illusion_damage_in_pct', 'incoming_damage', 'illusion_outgoing_damage',
                      'illusion_incoming_damage', 'illusion_outgoing_tooltip', 'shadowraze_range', 'miss_rate']

ignore_special = {'pudge_meat_hook':{'hook_width'}, 'faceless_void_time_lock':{'chance_pct', 'duration'},
                  'shadow_shaman_mass_serpent_ward': {'duration'}, 'faceless_void_chronosphere': {'duration', 'duration_scepter'},
                  'enigma_malefice': {'stun_duration'}, 'enigma_black_hole': {'duration'}, 'enigma_malefice': {'tick_rate', 'stun_duration'},
                  'enchantress_natures_attendants': {'radius','heal_interval'}, 'ember_spirit_sleight_of_fist': {'attack_interval', 'creep_damage_penalty'},
                  'ember_spirit_flame_guard': {'radius'}, 'ember_spirit_fire_remnant': {'charge_restore_time', 'radius'},
                  'ember_spirit_activate_fire_remnant': {'charge_restore_time', 'radius'}, 'earthshaker_fissure': {'fissure_range', 'fissure_duration'}}

ignore_normal = {'enchantress_impetus': {'AbilityCastRange'}}

ignore_all_normal = ['ID', 'AbilityCastPoint', 'AbilityManaCost', 'AbilityCooldown']


dont_parse = ['Version', 'ability_base', 'default_attack']

override_instead = ['abaddon_frostmourne', 'pudge_rot', 'alchemist_unstable_concoction'
             'alchemist_unstable_concoction_throw', 'drow_ranger_frost_arrows', 'axe_counter_helix',
             'beastmaster_call_of_the_wild', 'beastmaster_call_of_the_wild_boar', 'ember_spirit_fire_remnant',
             'ember_spirit_activate_fire_remnant']

factors = [2,3,5]
override_factor = 2




def str_to_type (s):
    try:                
        f = float(s)        
        if "." not in s:
            return int
        return float
    except ValueError:
        #print "EXCEPTION: %s" % s 
        value = s.upper()
        if value == "TRUE" or value == "FALSE":
            return bool
        return type(s)



def multiply(values, by, separator):
    aslist = values.strip().split(separator)
    tmplist = []
    newvalues = ''
    for value in aslist:
        try:
            newvalue = str(float(value.strip())*float(by))
            if newvalue[-2:] == '.0' and value[-2:] != '.0':
                newvalue = newvalue[:-2]
            tmplist.append(newvalue)
        except ValueError:
            print "EXCEPTION - ValueError multiply: %s | %s" % (value.strip(), values)
         
    return ' '.join(tmplist)

def divide(values, by, separator):
    aslist = values.strip().split(separator)
    tmplist = []
    newvalues = ''
    for value in aslist:
        try:
            newvalue = str(float(value.strip())/float(by))
            if newvalue[-2:] == '.0' and value[-2:] != '.0':
                newvalue = newvalue[:-2]
            tmplist.append(newvalue)
        except ValueError:
            print "EXCEPTION - ValueError divide: %s | %s" % (value.strip(), values)
        
    return ' '.join(tmplist)

def divide_or_multiply(key, values, by, separator):
    #if key == 'speed_bonus':
    #    print key + ': ' + values
    valueslist = values.strip().split(separator)
    if key in force_divide:
        return divide(values, by, separator)
    
    if len(valueslist) > 1:
        if str_to_type(valueslist[0]) < 0:
            print 'negative'
        if str_to_type(valueslist[0]) < str_to_type(valueslist[len(valueslist)-1]):
            #last value is higher than first, then multiply
            if key == 'speed_bonus':
                print 'multiply'
            return multiply(values, by, separator)
        elif str_to_type(valueslist[0]) == str_to_type(valueslist[len(valueslist)-1]):
            # same value, multiply
            if key == 'speed_bonus':
                print 'multiply'
            return multiply(values, by, separator)
        else:
            #last value is lower than first, then divide
            if key == 'speed_bonus':
                print 'divide'
            return divide(values, by, separator)
    else:
        # only single element, then multiply (parse exceptions in dividelist...)
        return multiply(values, by, separator)
    return ' '.join(tmplist)

    
if __name__ == "__main__":

    # remove comments from file (there's bug in _custom that some comments have only an single slash instead of double slash...
    clean.remove_comments('npc_abilities.txt', 'npc_abilities_custom.tmp')
    clean.remove_comments('items.txt', 'items.tmp')

    kv = KeyValues()
    kv.load('npc_abilities_custom.tmp')

    itemkv = KeyValues()
    itemkv.load('items.tmp')

    root = KeyValues('DOTAAbilities')
    rootov = KeyValues('DOTAAbilities')

    for factor in factors:
        if factor == override_factor:
            print 'Factor x%d (_override.txt)...' % factor
        else:
            print 'Factor x%d (_custom.txt)...' % factor
        if factor == override_factor:
            print 'Generating items'
            for item in itemkv:
                basekv = KeyValues(item)            
                if 'AbilitySpecial' in itemkv[item]:
                    basekv['AbilitySpecial'] = KeyValues(itemkv[item])
                    for element in itemkv[item]['AbilitySpecial']:
                        basekv['AbilitySpecial'][element] = KeyValues(element)
                        for varElement in itemkv[item]['AbilitySpecial'][element]:
                            value = itemkv[item]['AbilitySpecial'][element][varElement]
                            
                            testinstance = str_to_type(value.split(" ")[0])
                            if 'cooldown' not in varElement and varElement != 'var_type' and varElement not in ignore_all_special and testinstance in (int, long, float, complex):
                                value = divide_or_multiply(varElement, value, factor, " ")
                            basekv['AbilitySpecial'][element][varElement] = value
                            #print varElement
                rootov[item] = basekv
            
              
        print 'Generating skills'
        for skill in kv:            
            if skill in dont_parse or (factor != override_factor and skill in override_instead):
                continue

            skillkv = KeyValues(skill)
            skillkv['BaseClass'] = skill

            for base in kv[skill]:
                base = str(base)
                if base != 'AbilitySpecial':
                    valueslist = kv[skill][base].strip().split(" ")
                    if base not in ignore_all_normal and str_to_type(valueslist[0]) in (int, long, float, complex):
                        if skill in ignore_normal and base in ignore_normal[skill]:
                            skillkv[base] = kv[skill][base]
                        else:
                            skillkv[base] = divide_or_multiply(base, kv[skill][base], factor, " ")
                    else:
                        skillkv[base] = kv[skill][base]
                #print str(skillkv[base]) + ' = ' + str(kv[skill][base])
            
            if 'AbilitySpecial' in kv[skill]:
                abilityspecial = KeyValues('AbilitySpecial')
                for element in kv[skill]['AbilitySpecial']:
                    number = KeyValues(element)
                    for varElement in kv[skill]['AbilitySpecial'][element]:
                        numberValue = False
                        #print '%s -> %s' % (skill, varElement)
                       
                        testvalue = kv[skill]['AbilitySpecial'][element][varElement].split(" ")[0]
                        testinstance = str_to_type(testvalue)
                        if (skill in ignore_special and varElement in ignore_special[skill]) or (varElement in ignore_all_special):
                            #print '###ignore: %s / %s [x%d]' % (skill, varElement, factor)
                            pass
                        elif varElement != 'var_type' and testinstance in (int, long, float, complex):
                            varlist = kv[skill]['AbilitySpecial'][element][varElement]
                            numberValue = divide_or_multiply(varElement, varlist, factor, ' ')
                            #if '-' in varlist:
                            #    print 'negative: %s / %s -> %s' % (varlist, varElement, skill)
                            #    print 'negative2: %s / %s -> %s' % (numberValue, varElement, skill)
                            
                        #check if variable number was defined                        
                        if numberValue:
                            number[varElement] = numberValue
                        else:
                            number[varElement] = kv[skill]['AbilitySpecial'][element][varElement]
                            #print varElement
                            #print kv[skill]['AbilitySpecial'][element][varElement]
                    abilityspecial[element] = number
                #if usespec:
                skillkv['AbilitySpecial'] = abilityspecial
            if factor == override_factor:
                rootov[skill] = skillkv
            else:
                root[skill + '_x'+str(factor)] = skillkv
    root.save('npc_abilities_custom.txt')
    rootov.save('npc_abilities_override.txt')
    os.remove('npc_abilities_custom.tmp')
