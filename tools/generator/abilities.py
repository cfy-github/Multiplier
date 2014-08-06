from lib.keyvalues import KeyValues
from lib import clean
from lib import update_addons
import os


force_divide = ['min_blink_range', 'base_attack_time', 'transformation_time', 'attack_interval', 'structure_damage_mod', 'quill_release_threshold', 'formation_time']

ignore_all_special = ['crit_chance', 'bonus_evasion', 'dodge_chance_pct', 'miss_chance', 'dodge_chance',
                    'illusion_damage_out_pct', 'illusion_damage_in_pct', 'incoming_damage', 'illusion_outgoing_damage',
                      'illusion_incoming_damage', 'illusion_outgoing_tooltip', 'shadowraze_range', 'miss_rate', 'tick_rate', 'tick_interval',
                      'delay', 'tooltip_delay', 'light_strike_array_delay_time', 'damage_delay', 'static_remnant_delay', 'sand_storm_invis_delay', 'jump_delay',
                      'bounce_delay', 'idle_invis_delay', 'fire_delay', 'path_delay', 'hero_teleport_delay', 'attack_delay', 'multicast_delay', 'teleport_delay',
                      'stun_delay', 'cast_delay', 'activation_delay', 'rock_explosion_delay', 'first_wave_delay', 'explode_delay', 'cooldown_scepter',
                      'omni_slash_cooldown_scepter', 'epicenter_cooldown_scepter', 'nether_swap_cooldown_scepter', 'scepter_cooldown', 'replica_damage_outgoing_scepter',
                      'tooltip_outgoing_scepter', 'shadowraze_radius', 'mana_cost_per_second', 'stun_duration', 'light_strike_array_stun_duration', 'arrow_min_stun',
                      'arrow_max_stun', 'stun_min', 'stun_max', 'coil_stun_duration', 'blast_stun_duration', 'bolt_stun_duration', 'stun_chance', 'magic_missile_stun',
                      'fail_stun_duration', 'min_stun', 'max_stun', 'stun_delay', 'hero_stun_duration', 'creep_stun_duration', 'initial_stun_duration', 'sleep_duration',
                      'non_hero_stun_duration', 'magic_missile_stun', 'cast_animation', 'stun_radius', 'lift_duration', 'silence_duration', 'knockback_duration', 'fade_time',
                      'shock_radius', 'pre_flight_time', 'fiend_grip_tick_interval', 'fiend_grip_duration', 'fiend_grip_duration_scepter', 'damage_modifier', 'damage_modifier_tooltip',
                      'illusion_incoming_dmg_pct_tooltip', 'duration', 'tooltip_duration', 'duration_scepter', 'bash_chance', 'bonus_range', 'bonus_range_scepter', 'bonus_cleave_damage_scepter',
                      'trance_duration', 'blind_duration', 'blind_pct', 'whirl_duration', 'projectile_duration', 'slow_duration', 'pause_duration', 'purge_frequency', 'strike_interval',
                      'strike_interval_scepter', 'blast_dot_duration', 'tooltip_slow_duration', 'last_proc', 'crush_radius', 'crush_extra_slow_duration', 'charge_restore_time',
                      'echo_slam_damage_range', 'echo_slam_echo_search_range', 'echo_slam_echo_range', 'blade_dance_crit_chance', 'blade_fury_radius', 'blade_fury_damage_tick',
                      'healing_ward_aura_radius', 'omni_slash_radius', 'omni_slash_bounce_tick', 'illusion_duration', 'tooltip_attack_range', 'multicast_delay', 'scepter_mana',
                      'multicast_2_times', 'multicast_3_times', 'multicast_4_times', 'fireblast_mana_cost', 'fireblast_cooldown', 'ignite_aoe', 'bloodlust_cooldown',
                      'multicast_2_times_tooltip', 'multicast_3_times_tooltip', 'multicast_4_times_tooltip', 'outgoing_damage', 'incoming_damage', 'invuln_duration', 'outgoing_damage_tooltip']

ignore_special = {'pudge_meat_hook':{'hook_width'}, 'faceless_void_time_lock':{'chance_pct', 'duration'},
                  'shadow_shaman_mass_serpent_ward': {'duration'}, 'faceless_void_chronosphere': {'duration', 'duration_scepter'},
                  'enigma_malefice': {'stun_duration'}, 'enigma_black_hole': {'duration'}, 'enigma_malefice': {'stun_duration'},
                  'enchantress_natures_attendants': {'radius','heal_interval'}, 'ember_spirit_sleight_of_fist': {'creep_damage_penalty'},
                  'ember_spirit_flame_guard': {'radius'}, 'ember_spirit_fire_remnant': {'charge_restore_time', 'radius'},
                  'ember_spirit_activate_fire_remnant': {'charge_restore_time', 'radius'}, 'earthshaker_fissure': {'fissure_range', 'fissure_duration', 'fissure_radius', 'stun_duration'},
                  'crystal_maiden_freezing_field': {'explosion_interval', 'radius', 'explosion_radius', 'explosion_min_dist', 'explosion_max_dist'},
                  'rattletrap_power_cogs': {'radius', 'spacing', 'duration'}, 'rattletrap_battery_assault': {'interval', 'radius', 'duration'},
                  'dark_seer_ion_shell': {'radius', 'duration'}, 'necrolyte_heartstopper_aura': {'aura_radius'}, 'axe_battle_hunger': {'duration'},
                  'doom_bringer_doom': {'duration', 'duration_scepter', 'deniable_pct'}, 'doom_bringer_lvl_death': {'lvl_bonus_multiple'},
                  'doom_bringer_scorched_earth': {'radius', 'duration'}, 'dazzle_shallow_grave':{'duration_tooltip'}, 
                  'dazzle_shadow_wave':{'damage_radius'}, 'dazzle_weave':{'duration', 'duration_scepter'},'sniper_assassinate': {'projectile_speed'},
                  'dazzle_poison_touch': {'should_stun', 'duration_tooltip', 'set_time'}, 'batrider_sticky_napalm': {'radius', 'duration'},
                  'batrider_flamebreak': {'explosion_radius', 'collision_radius'}, 'batrider_firefly': {'radius', 'tree_radius', 'duration'},
                  'batrider_flaming_lasso': {'drag_distance'}, 'brewmaster_primal_split': {'split_duration'}, 'sniper_shrapnel': {'duration', 'damage_delay', 'slow_duration', 'radius'},
                  'death_prophet_exorcism': {'radius', 'max_distance', 'give_up_distance', 'spirit_speed'}, 'death_prophet_silence': {'radius'},
                  'alchemist_acid_spray': {'duration', 'radius'}, 'alchemist_chemical_rage': {'duration'}, 'spirit_breaker_greater_bash': {'chance_pct', 'duration'},
                  'alchemist_goblins_greed': {'bonus_gold_cap'}, 'weaver_shukuchi': {'radius', 'fade_time', 'duration'}, 'sniper_headshot': {'stun_duration'},
                  'viper_corrosive_skin': {'duration'}, 'windrunner_focusfire': {'focusfire_damage_reduction', 'focusfire_damage_reduction_scepter'},
                  'windrunner_powershot': {'damage_reduction', 'speed_reduction', 'arrow_width', 'tree_width', 'vision_duration'},
                  'windrunner_shackleshot': {'shackle_count'}, 'lone_druid_true_form': {'speed_loss'}, 'viper_viper_strike': {'duration'},
                  'spectre_spectral_dagger': {'dagger_path_duration', 'hero_path_duration', 'buff_persistence', 'dagger_radius', 'path_radius', 'vision_radius', 'dagger_grace_period'},
                  'tinker_march_of_the_machines': {'radius', 'collision_radius', 'splash_radius', 'duration'}, 'pugna_nether_blast': {'radius'},
                  'lone_druid_spirit_bear_entangle': {'hero_duration', 'creep_duration'}, 'lone_druid_spirit_bear_demolish': {'bonus_building_damage'},
                  'lone_druid_true_form': {'base_attack_time', 'speed_loss'}, 'lone_druid_spirit_bear': {'bear_regen_tooltip', 'bear_bat', 'bear_armor'},
                  'shadow_shaman_shackles': {'channel_time'}, 'antimage_mana_break': {'damage_per_burn'}, 'antimage_mana_void': {'mana_void_aoe_radius'},
                  'rubick_telekinesis': {'radius', 'lift_duration', 'stun_duration'}, 'rubick_fade_bolt': {'duration', 'slow_duration'},
                  'leshrac_pulse_nova': {'radius'}, 'leshrac_lightning_storm': {'slow_duration'}, 'leshrac_diabolic_edict': {'radius'},
                  'leshrac_split_earth': {'duration'}, 'rattletrap_hookshot': {'latch_radius', 'stun_radius', 'duration'}, 'ursa_overpower': {'duration_tooltip'},
                  'dragon_knight_frost_breath': {'duration'}, 'drow_ranger_silence': {'duration', 'silence_radius'}, 'drow_ranger_wave_of_silence': {''},
                  'dragon_knight_elder_dragon_form': {'duration', 'bonus_attack_range', 'corrosive_breath_duration', 'splash_radius', 'splash_damage_percent', 'frost_duration', 'frost_aoe'},
                  'ursa_fury_swipes': {'bonus_reset_time', 'bonus_reset_time_roshan'}, 'ursa_enrage': {'life_damage_bonus_percent'},
                  'gyrocopter_rocket_barrage': {'radius'}, 'gyrocopter_flak_cannon': {'radius'}, 'gyrocopter_call_down': {'radius'}, 'tinker_laser': {'duration_hero', 'miss_rate', 'speed'},
                  'bane_nightmare': {'duration', 'animation_rate', 'nightmare_dot_interval', 'nightmare_invuln_time'}, 'bloodseeker_bloodrage': {'duration'},
                  'bloodseeker_thirst': {'visibility_threshold_pct', 'invis_threshold_pct'}, 'wisp_tether': {'radius', 'latch_distance', 'tether_duration'},
                  'wisp_overcharge': {'drain_interval', 'drain_pct', 'drain_pct_tooltip'}, 'wisp_spirits': {'min_range', 'hero_hit_radius', 'explode_radius', 'default_radius'},
                  'lion_impale': {'duration', 'width'}, 'lion_voodoo': {'duration', 'movespeed'}, 'lion_mana_drain': {'duration', 'break_distance', 'illusion_kill_time', 'tick_interval'},
                  'luna_moon_glaive': {'damage_reduction_percent', 'range'}, 'luna_eclipse': {'radius', 'beam_interval', 'duration_tooltip', 'duration_tooltip_scepter'},
                  'lina_light_strike_array': {'light_strike_array_aoe', 'light_strike_array_delay_time'}, 'magnataur_empower': {'empower_duration', 'cleave_damage_pct', 'cleave_radius'},
                  'magnataur_skewer': {'skewer_radius', 'slow_duration', 'tree_radius'}, 'magnataur_reverse_polarity': {'pull_radius', 'pull_duration'},
                  'medusa_stone_gaze': {'duration', 'stone_duration', 'face_duration', 'vision_cone'}, 'medusa_split_shot': {'range', 'projectile_speed'},
                  'medusa_mystic_snake': {'radius', 'initial_speed', 'return_speed', 'snake_scale'}, 'morphling_waveform': {'width'}, 'morphling_replicate': {'duration'},
                  'morphling_morph_agi': {'mana_cost', 'morph_cooldown'}, 'morphling_morph_str': {'mana_cost', 'morph_cooldown'},
                  'omniknight_guardian_angel': {'duration', 'duration_scepter'}, 'omniknight_degen_aura': {'radius'}, 'omniknight_repel': {'duration'},
                  'omniknight_purification': {'radius'}, 'clinkz_death_pact': {'damage_gain_pct', 'duration'}, 'clinkz_wind_walk': {'duration"'},
                  'clinkz_strafe': {'duration'}, 'troll_warlord_whirling_axes_melee': {'max_range', 'hit_radius'}, 'warlock_upheaval': {'aoe', 'duration'},
                  'troll_warlord_whirling_axes_ranged': {'axe_width', 'axe_range', 'axe_slow_duration'}, 'troll_warlord_berserkers_rage': {'bash_duration', 'base_attack_time'},
                  'tiny_avalanche': {'radius', 'num_ticks'}, 'tiny_toss': {'duration', 'grab_radius', 'radius'}, 'spectre_dispersion': {'damage_reflection_pct', 'min_radius'},
                  'shredder_reactive_armor': {'stack_limit', 'stack_duration'}, 'shredder_whirling_death': {'whirling_radius', 'duration'},
                  'earthshaker_aftershock': {'aftershock_range', 'tooltip_duration'}, 'razor_plasma_field': {'radius'},
                  'razor_static_link': {'drain_duration', 'drain_range', 'radius', 'speed', 'vision_duration'}, 'razor_eye_of_the_storm': {'radius', 'duration', 'strike_interval'},
                  'skeleton_king_reincarnation': {'reincarnate_time'}, 'slardar_bash': {'chance', 'duration', 'duration_creep'}, 'warlock_fatal_bonds': {'duration'},
                  'earth_spirit_geomagnetic_grip': {'radius', 'speed'}, 'bristleback_viscous_nasal_goo': {'goo_duration', 'base_move_slow', 'move_slow_per_stack'},
                  'bristleback_quill_spray': {'quill_stack_duration', 'radius'}, 'bristleback_bristleback': {'side_angle', 'back_angle', 'back_damage_reduction', 'side_damage_reduction'},
                  'bristleback_warpath': {'stack_duration'}, 'terrorblade_metamorphosis': {'base_attack_time'}, 'treant_natures_guise': {'radius', 'grace_time'},
                  'treant_overgrowth': {'radius'}, 'treant_living_armor': {'damage_count'}, 'undying_decay': {'radius', 'decay_duration'},
                  'undying_soul_rip': {'radius'}, 'undying_tombstone': {'duration', 'radius', 'zombie_interval'}, 'undying_tombstone_zombie_aura': {'radius', 'zombie_interval'},
                  'undying_tombstone_zombie_deathstrike': {'duration'}, 'undying_flesh_golem': {'duration', 'radius'}, 'disruptor_thunder_strike': {'radius', 'strike_interval', 'duration'},
                  'disruptor_glimpse': {'backtrack_time'}, 'disruptor_kinetic_field': {'radius', 'duration'}, 'disruptor_static_storm': {'radius', 'duration', 'duration_scepter'},
                  'nyx_assassin_impale': {'width', 'duration'}, 'nyx_assassin_vendetta': {'duration'}, 'naga_siren_ensnare': {'duration'},
                  'naga_siren_rip_tide': {'radius'}, 'naga_siren_song_of_the_siren': {'duration', 'animation_rate'}}


ignore_normal = {'enchantress_impetus': {'AbilityCastRange'}, 'dazzle_shallow_grave':{'AbilityDuration'}, 'dazzle_poison_touch': {'AbilityDuration'},
                 'death_prophet_exorcism': {'AbilityDuration'}, 'leshrac_diabolic_edict': {'AbilityDuration'}, 'leshrac_split_earth': {'AbilityDuration'},
                 'ursa_overpower': {'AbilityDuration'}, 'gyrocopter_flak_cannon': {'AbilityDuration'}, 'wisp_tether': {'AbilityCastRange'},
                 'lion_mana_drain': {'AbilityCastRange', 'AbilityChannelTime'}, 'shredder_whirling_death': {'AbilityCastRange'},
                 'razor_static_link': {'AbilityCastRange'}}

ignore_all_normal = ['ID', 'AbilityCastPoint', 'AbilityManaCost', 'AbilityCooldown', 'AbilityModifierSupportValue', 'MaxLevel', 'RequiredLevel', 'LevelsBetweenUpgrades',
                     'DisplayAdditionalHeroes', 'AbilityDuration']


dont_parse = ['Version', 'ability_base', 'default_attack', 'invoker_invoke', 'invoker_empty1', 'invoker_empty2', 'ancient_apparition_ice_blast_release',
              'meepo_divided_we_stand', 'weaver_geminate_attack', 'lone_druid_true_form_druid', 'lone_druid_spirit_bear_return', 'pugna_decrepify', 'shadow_shaman_voodoo',
              'rubick_telekinesis_land', 'tinker_rearm', 'bane_nightmare_end', 'wisp_tether_break', 'wisp_spirits_in', 'wisp_spirits_out', 'wisp_empty1', 'wisp_empty2', 'wisp_relocate',
              'morphling_morph_replicate', 'terrorblade_sunder', 'naga_siren_song_of_the_siren_cancel']

override_instead = ['abaddon_frostmourne', 'pudge_rot', 'alchemist_unstable_concoction',
                    'alchemist_unstable_concoction_throw', 'drow_ranger_frost_arrows', 'axe_counter_helix',
                    'beastmaster_call_of_the_wild', 'beastmaster_call_of_the_wild_boar', 'ember_spirit_fire_remnant',
                    'ember_spirit_activate_fire_remnant', 'invoker_cold_snap', 'invoker_ghost_walk', 'invoker_tornado', 'invoker_emp',
                    'invoker_alacrity', 'invoker_chaos_meteor', 'invoker_sun_strike', 'invoker_forge_spirit', 'forged_spirit_melting_strike',
                    'invoker_ice_wall', 'invoker_deafening_blast', 'ancient_apparition_ice_blast', 'lycan_summon_wolves',
                    'lone_druid_true_form_battle_cry', 'lone_druid_spirit_bear_entangle', 'lone_druid_spirit_bear_demolish', 'wisp_spirits',
                    'wisp_tether', 'luna_lucent_beam', 'lina_fiery_soul', 'morphling_replicate', 'earth_spirit_stone_caller',
                    'naga_siren_song_of_the_siren']
        #, 'invoker_exort', 'invoker_wex', 'invoker_quas'

item_fixed_value = {'item_heart': {'health_regen_rate':'1'}}

factors = [2,3,5,10]
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

                            if item in item_fixed_value and varElement in item_fixed_value[item]:
                                value = item_fixed_value[item][varElement]
                            else:
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
    update_addons.updateAddons()
