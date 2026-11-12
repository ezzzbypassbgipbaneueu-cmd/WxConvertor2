# -*- coding: utf-8 -*-
"""Tabelas de mapeamento Minecraft Java -> Blockman GO.

Chave   = nome da textura no Blockman GO (existe em bg_reference/).
Valor   = lista de nomes candidatos no Resource Pack Java, em ordem de
          prioridade. Misturam o padrao novo (1.13+, "flattening") e o
          padrao antigo (<=1.12), porque o Blockman GO usa nomes antigos.

build_texture_mapping() em mc_to_blockman.py descarta qualquer chave que nao
exista na referencia interna, entao nomes inventados nao chegam ao ZIP final.
"""

COLORS = ["black", "blue", "brown", "cyan", "gray", "green", "light_blue",
          "lime", "magenta", "orange", "pink", "purple", "red", "silver",
          "white", "yellow"]


def _j(color):
    """Nome da cor no Java novo (o 'silver' antigo virou 'light_gray')."""
    return "light_gray" if color == "silver" else color


WOODS = {  # nome Blockman -> nome Java novo
    "oak": "oak", "spruce": "spruce", "birch": "birch", "jungle": "jungle",
    "acacia": "acacia", "big_oak": "dark_oak",
}

BLOCKS = {
    "bedrock": ["bedrock"],
    "bookshelf": ["bookshelf"],
    "brick": ["bricks", "brick"],
    "beacon": ["beacon"],
    "cactus_bottom": ["cactus_bottom"],
    "cactus_side": ["cactus_side"],
    "cactus_top": ["cactus_top"],
    "cake_bottom": ["cake_bottom"],
    "cake_inner": ["cake_inner"],
    "cake_side": ["cake_side"],
    "cake_top": ["cake_top"],
    "clay": ["clay"],
    "coal_block": ["coal_block"],
    "coal_ore": ["coal_ore"],
    "coarse_dirt": ["coarse_dirt"],
    "cobblestone": ["cobblestone"],
    "cobblestone_mossy": ["mossy_cobblestone", "cobblestone_mossy"],
    "command_block": ["command_block"],
    "crafting_table_front": ["crafting_table_front"],
    "crafting_table_side": ["crafting_table_side"],
    "crafting_table_top": ["crafting_table_top"],
    "daylight_detector_inverted_top": ["daylight_detector_inverted_top"],
    "daylight_detector_side": ["daylight_detector_side"],
    "daylight_detector_top": ["daylight_detector_top"],
    "deadbush": ["dead_bush", "deadbush"],
    "diamond_block": ["diamond_block"],
    "diamond_ore": ["diamond_ore"],
    "dirt": ["dirt"],
    "dirt_new": ["dirt"],          # alias (mesma cor media na referencia)
    "dirt_top": ["dirt"],          # alias (mesma cor media na referencia)
    "dirt_podzol_side": ["podzol_side", "dirt_podzol_side"],
    "dirt_podzol_top": ["podzol_top", "dirt_podzol_top"],
    "dispenser_front_horizontal": ["dispenser_front_horizontal", "dispenser_front"],
    "dispenser_front_vertical": ["dispenser_front_vertical"],
    "dropper_front_horizontal": ["dropper_front_horizontal", "dropper_front"],
    "dropper_front_vertical": ["dropper_front_vertical"],
    "dragon_egg": ["dragon_egg"],
    "emerald_block": ["emerald_block"],
    "emerald_ore": ["emerald_ore"],
    "enchanting_table_bottom": ["enchanting_table_bottom"],
    "enchanting_table_side": ["enchanting_table_side"],
    "enchanting_table_top": ["enchanting_table_top"],
    "end_stone": ["end_stone"],
    "endframe_eye": ["end_portal_frame_eye", "endframe_eye"],
    "endframe_side": ["end_portal_frame_side", "endframe_side"],
    "endframe_top": ["end_portal_frame_top", "endframe_top"],
    "farmland_dry": ["farmland", "farmland_dry"],
    "farmland_wet": ["farmland_moist", "farmland_wet"],
    "fern": ["fern"],
    "flower_allium": ["allium", "flower_allium"],
    "flower_blue_orchid": ["blue_orchid", "flower_blue_orchid"],
    "flower_dandelion": ["dandelion", "flower_dandelion"],
    "flower_houstonia": ["azure_bluet", "flower_houstonia"],
    "flower_oxeye_daisy": ["oxeye_daisy", "flower_oxeye_daisy"],
    "flower_paeonia": ["flower_paeonia"],
    "flower_pot": ["flower_pot"],
    "flower_rose": ["poppy", "flower_rose"],
    "flower_tulip_orange": ["orange_tulip", "flower_tulip_orange"],
    "flower_tulip_pink": ["pink_tulip", "flower_tulip_pink"],
    "flower_tulip_red": ["red_tulip", "flower_tulip_red"],
    "flower_tulip_white": ["white_tulip", "flower_tulip_white"],
    "furnace_front_off": ["furnace_front", "furnace_front_off"],
    "furnace_front_on": ["furnace_front_on"],
    "furnace_side": ["furnace_side"],
    "furnace_top": ["furnace_top"],
    "glass": ["glass"],
    "glass_new": ["glass"],        # alias (mesma cor media na referencia)
    "glowstone": ["glowstone"],
    "gold_block": ["gold_block"],
    "gold_ore": ["gold_ore"],
    "grass_side": ["grass_block_side", "grass_side"],
    "grass_side_overlay": ["grass_block_side_overlay", "grass_side_overlay"],
    "grass_side_snowed": ["grass_block_snow", "grass_side_snowed"],
    "grass_top": ["grass_block_top", "grass_top"],
    "gravel": ["gravel"],
    "hardened_clay": ["terracotta", "hardened_clay"],
    "hay_block_side": ["hay_block_side"],
    "hay_block_top": ["hay_block_top"],
    "hopper_inside": ["hopper_inside"],
    "hopper_outside": ["hopper_outside"],
    "hopper_top": ["hopper_top"],
    "ice": ["ice"],
    "ice_packed": ["packed_ice", "ice_packed"],
    "iron_bars": ["iron_bars"],
    "iron_block": ["iron_block"],
    "iron_ore": ["iron_ore"],
    "itemframe_background": ["itemframe_background", "item_frame"],
    "jukebox_side": ["jukebox_side"],
    "jukebox_top": ["jukebox_top"],
    "ladder": ["ladder"],
    "lapis_block": ["lapis_block"],
    "lapis_ore": ["lapis_ore"],
    "lever": ["lever"],
    "melon_side": ["melon_side"],
    "melon_stem_connected": ["attached_melon_stem", "melon_stem_connected"],
    "melon_stem_disconnected": ["melon_stem", "melon_stem_disconnected"],
    "melon_top": ["melon_top"],
    "mob_spawner": ["spawner", "mob_spawner"],
    "mushroom_block_inside": ["mushroom_block_inside"],
    "mushroom_block_skin_brown": ["brown_mushroom_block", "mushroom_block_skin_brown"],
    "mushroom_block_skin_red": ["red_mushroom_block", "mushroom_block_skin_red"],
    "mushroom_block_skin_stem": ["mushroom_stem", "mushroom_block_skin_stem"],
    "mushroom_brown": ["brown_mushroom", "mushroom_brown"],
    "mushroom_red": ["red_mushroom", "mushroom_red"],
    "mycelium_side": ["mycelium_side"],
    "mycelium_top": ["mycelium_top"],
    "nether_brick": ["nether_bricks", "nether_brick"],
    "nether_wart_stage_0": ["nether_wart_stage0", "nether_wart_stage_0"],
    "nether_wart_stage_1": ["nether_wart_stage1", "nether_wart_stage_1"],
    "nether_wart_stage_2": ["nether_wart_stage2", "nether_wart_stage_2"],
    "netherrack": ["netherrack"],
    "noteblock": ["note_block", "noteblock"],
    "observer_back": ["observer_back"],
    "observer_back_lit": ["observer_back_on", "observer_back_lit"],
    "observer_front": ["observer_front"],
    "observer_side": ["observer_side"],
    "observer_top": ["observer_top"],
    "obsidian": ["obsidian"],
    "piston_bottom": ["piston_bottom"],
    "piston_inner": ["piston_inner"],
    "piston_side": ["piston_side"],
    "piston_top_normal": ["piston_top", "piston_top_normal"],
    "piston_top_sticky": ["piston_top_sticky"],
    "prismarine": ["prismarine", "prismarine_rough"],       # 1o frame se animada
    "prismarine_bricks": ["prismarine_bricks"],
    "prismarine_dark": ["dark_prismarine", "prismarine_dark"],
    "prismarine_rough": ["prismarine_rough", "prismarine"],  # tira animada
    "pumpkin_face_off": ["carved_pumpkin", "pumpkin_face_off"],
    "pumpkin_face_on": ["jack_o_lantern", "pumpkin_face_on"],
    "pumpkin_side": ["pumpkin_side"],
    "pumpkin_stem_connected": ["attached_pumpkin_stem", "pumpkin_stem_connected"],
    "pumpkin_stem_disconnected": ["pumpkin_stem", "pumpkin_stem_disconnected"],
    "pumpkin_top": ["pumpkin_top"],
    "quartz_block_bottom": ["quartz_block_bottom"],
    "quartz_block_chiseled": ["chiseled_quartz_block", "quartz_block_chiseled"],
    "quartz_block_chiseled_top": ["chiseled_quartz_block_top", "quartz_block_chiseled_top"],
    "quartz_block_lines": ["quartz_pillar", "quartz_block_lines"],
    "quartz_block_lines_top": ["quartz_pillar_top", "quartz_block_lines_top"],
    "quartz_block_side": ["quartz_block_side"],
    "quartz_block_top": ["quartz_block_top"],
    "quartz_ore": ["nether_quartz_ore", "quartz_ore"],
    "rail_activator": ["activator_rail", "rail_activator"],
    "rail_activator_powered": ["activator_rail_on", "rail_activator_powered"],
    "rail_detector": ["detector_rail", "rail_detector"],
    "rail_detector_powered": ["detector_rail_on", "rail_detector_powered"],
    "rail_golden": ["powered_rail", "rail_golden"],
    "rail_golden_powered": ["powered_rail_on", "rail_golden_powered"],
    "rail_normal": ["rail", "rail_normal"],
    "rail_normal_turned": ["rail_corner", "rail_normal_turned"],
    "red_nether_brick": ["red_nether_bricks", "red_nether_brick"],
    "red_sand": ["red_sand"],
    "redstone_block": ["redstone_block"],
    "redstone_dust_cross": ["redstone_dust_cross"],
    "redstone_dust_cross_overlay": ["redstone_dust_cross_overlay"],
    "redstone_dust_line": ["redstone_dust_line"],
    "redstone_dust_line_overlay": ["redstone_dust_line_overlay"],
    "redstone_lamp_off": ["redstone_lamp", "redstone_lamp_off"],
    "redstone_lamp_on": ["redstone_lamp_on"],
    "redstone_ore": ["redstone_ore"],
    "redstone_torch_off": ["redstone_torch_off"],
    "redstone_torch_on": ["redstone_torch", "redstone_torch_on"],
    "reeds": ["sugar_cane", "reeds"],
    "repeater_off": ["repeater", "repeater_off"],
    "repeater_on": ["repeater_on"],
    "comparator_off": ["comparator", "comparator_off"],
    "comparator_on": ["comparator_on"],
    "sand": ["sand"],
    "sandstone_bottom": ["sandstone_bottom"],
    "sandstone_carved": ["chiseled_sandstone", "sandstone_carved"],
    "sandstone_normal": ["sandstone", "sandstone_normal"],
    "sandstone_smooth": ["cut_sandstone", "sandstone_smooth"],
    "sandstone_top": ["sandstone_top"],
    "red_sandstone_bottom": ["red_sandstone_bottom"],
    "red_sandstone_carved": ["chiseled_red_sandstone", "red_sandstone_carved"],
    "red_sandstone_normal": ["red_sandstone", "red_sandstone_normal"],
    "red_sandstone_smooth": ["cut_red_sandstone", "red_sandstone_smooth"],
    "red_sandstone_top": ["red_sandstone_top"],
    "sea_lantern": ["sea_lantern"],                          # tira animada
    "slime": ["slime_block", "slime"],
    "snow": ["snow"],
    "soul_sand": ["soul_sand"],
    "sponge": ["sponge"],
    "sponge_wet": ["wet_sponge", "sponge_wet"],
    "stone": ["stone"],
    "stone_andesite": ["andesite", "stone_andesite"],
    "stone_andesite_smooth": ["polished_andesite", "stone_andesite_smooth"],
    "stone_diorite": ["diorite", "stone_diorite"],
    "stone_diorite_smooth": ["polished_diorite", "stone_diorite_smooth"],
    "stone_granite": ["granite", "stone_granite"],
    "stone_granite_smooth": ["polished_granite", "stone_granite_smooth"],
    "stone_slab_side": ["stone_slab_side", "smooth_stone_slab_side"],
    "stone_slab_top": ["stone_slab_top", "smooth_stone"],
    "stonebrick": ["stone_bricks", "stonebrick"],
    "stonebrick_carved": ["chiseled_stone_bricks", "stonebrick_carved"],
    "stonebrick_cracked": ["cracked_stone_bricks", "stonebrick_cracked"],
    "stonebrick_mossy": ["mossy_stone_bricks", "stonebrick_mossy"],
    "tallgrass": ["short_grass", "grass", "tallgrass"],
    "tnt_bottom": ["tnt_bottom"],
    "tnt_side": ["tnt_side"],
    "tnt_top": ["tnt_top"],
    "torch_on": ["torch", "torch_on"],
    "trapdoor": ["oak_trapdoor", "trapdoor"],
    "trip_wire": ["tripwire", "trip_wire"],
    "trip_wire_source": ["trip_wire_source"],
    "vine": ["vine"],
    "waterlily": ["lily_pad", "waterlily"],
    "web": ["cobweb", "web"],
    "anvil_base": ["anvil_base", "anvil"],
    "anvil_top_damaged_0": ["anvil_top", "anvil_top_damaged_0"],
    "anvil_top_damaged_1": ["chipped_anvil_top", "anvil_top_damaged_1"],
    "anvil_top_damaged_2": ["damaged_anvil_top", "anvil_top_damaged_2"],
    "brewing_stand": ["brewing_stand"],
    "brewing_stand_base": ["brewing_stand_base"],
    "cauldron_bottom": ["cauldron_bottom"],
    "cauldron_inner": ["cauldron_inner"],
    "cauldron_side": ["cauldron_side"],
    "cauldron_top": ["cauldron_top"],
    "double_plant_fern_bottom": ["large_fern_bottom", "double_plant_fern_bottom"],
    "double_plant_fern_top": ["large_fern_top", "double_plant_fern_top"],
    "double_plant_grass_bottom": ["tall_grass_bottom", "double_plant_grass_bottom"],
    "double_plant_grass_top": ["tall_grass_top", "double_plant_grass_top"],
    "double_plant_paeonia_bottom": ["peony_bottom", "double_plant_paeonia_bottom"],
    "double_plant_paeonia_top": ["peony_top", "double_plant_paeonia_top"],
    "double_plant_rose_bottom": ["rose_bush_bottom", "double_plant_rose_bottom"],
    "double_plant_rose_top": ["rose_bush_top", "double_plant_rose_top"],
    "double_plant_sunflower_back": ["sunflower_back", "double_plant_sunflower_back"],
    "double_plant_sunflower_bottom": ["sunflower_bottom", "double_plant_sunflower_bottom"],
    "double_plant_sunflower_front": ["sunflower_front", "double_plant_sunflower_front"],
    "double_plant_sunflower_top": ["sunflower_top", "double_plant_sunflower_top"],
    "double_plant_syringa_bottom": ["lilac_bottom", "double_plant_syringa_bottom"],
    "double_plant_syringa_top": ["lilac_top", "double_plant_syringa_top"],
}

for _n in range(4):
    BLOCKS["carrots_stage_%d" % _n] = ["carrots_stage%d" % _n, "carrots_stage_%d" % _n]
    BLOCKS["potatoes_stage_%d" % _n] = ["potatoes_stage%d" % _n, "potatoes_stage_%d" % _n]
for _n in range(8):
    BLOCKS["wheat_stage_%d" % _n] = ["wheat_stage%d" % _n, "wheat_stage_%d" % _n]
for _n in range(3):
    BLOCKS["cocoa_stage_%d" % _n] = ["cocoa_stage%d" % _n, "cocoa_stage_%d" % _n]
for _n in range(10):
    BLOCKS["destroy_stage_%d" % _n] = ["destroy_stage_%d" % _n]

for _bg, _java in WOODS.items():
    BLOCKS["planks_" + _bg] = ["%s_planks" % _java, "planks_" + _bg]
    BLOCKS["log_" + _bg] = ["%s_log" % _java, "log_" + _bg]
    BLOCKS["log_%s_top" % _bg] = ["%s_log_top" % _java, "log_%s_top" % _bg]
    BLOCKS["leaves_" + _bg] = ["%s_leaves" % _java, "leaves_" + _bg]
    # leaves_*_opaque sao DERIVADAS de leaves_* (ver OPAQUE_LEAVES)
BLOCKS["sapling_oak"] = ["oak_sapling", "sapling_oak"]
BLOCKS["sapling_spruce"] = ["spruce_sapling", "sapling_spruce"]
BLOCKS["sapling_birch"] = ["birch_sapling", "sapling_birch"]
BLOCKS["sapling_jungle"] = ["jungle_sapling", "sapling_jungle"]
BLOCKS["sapling_acacia"] = ["acacia_sapling", "sapling_acacia"]
BLOCKS["sapling_roofed_oak"] = ["dark_oak_sapling", "sapling_roofed_oak"]

for _d in ("wood", "iron", "acacia", "birch", "dark_oak", "jungle", "spruce"):
    _jv = {"wood": "oak"}.get(_d, _d)
    for _half, _jhalf in (("lower", "bottom"), ("upper", "top")):
        BLOCKS["door_%s_%s" % (_d, _half)] = ["%s_door_%s" % (_jv, _jhalf),
                                              "door_%s_%s" % (_d, _half)]

for _c in COLORS:
    BLOCKS["wool_colored_" + _c] = ["%s_wool" % _j(_c), "wool_colored_" + _c, "wool_colored_" + _j(_c)]
    BLOCKS["concrete_" + _c] = ["%s_concrete" % _j(_c), "concrete_" + _c]
    BLOCKS["hardened_clay_stained_" + _c] = ["%s_terracotta" % _j(_c), "hardened_clay_stained_" + _c]
    BLOCKS["glass_" + _c] = ["%s_stained_glass" % _j(_c), "glass_" + _c]
    BLOCKS["glass_pane_top_" + _c] = ["%s_stained_glass_pane_top" % _j(_c), "glass_pane_top_" + _c]
BLOCKS["glass_pane_top"] = ["glass_pane_top"]

# Blockman: leaves_X_opaque = folha sem buracos (alpha 255). Derivada da folha Java.
OPAQUE_LEAVES = {"leaves_%s_opaque" % w: "leaves_%s" % w for w in WOODS}

# Blockman -> motivo. Existem na referencia, mas esta versao do conversor
# NAO converte (formato/animacao ainda nao validado). Nao sao "convertidos".
UNSUPPORTED_BLOCKS = {
    "water_still": "liquido animado (contagem de frames do Blockman nao validada)",
    "water_flow": "liquido animado (contagem de frames do Blockman nao validada)",
    "lava_still": "liquido animado (contagem de frames do Blockman nao validada)",
    "lava_flow": "liquido animado (contagem de frames do Blockman nao validada)",
    "fire_layer_0": "fogo animado (contagem de frames do Blockman nao validada)",
    "fire_layer_1": "fogo animado (contagem de frames do Blockman nao validada)",
    "gameloading": "tela de loading (interface, fora do escopo atual)",
}

# ----------------------------------------------------------------- itens
ITEMS = {
    "apple": ["apple"],
    "apple_golden": ["golden_apple", "apple_golden"],
    "arrow": ["arrow"],
    "bed": ["red_bed", "bed"],
    "beef_cooked": ["cooked_beef", "beef_cooked"],
    "beef_raw": ["beef", "beef_raw"],
    "blaze_rod": ["blaze_rod"],
    "bone": ["bone"],
    "book_enchanted": ["enchanted_book", "book_enchanted"],
    "book_normal": ["book", "book_normal"],
    "book_writable": ["writable_book", "book_writable"],
    "book_written": ["written_book", "book_written"],
    "bow_standby": ["bow", "bow_standby"],
    "bow_pulling_0": ["bow_pulling_0"],
    "bow_pulling_1": ["bow_pulling_1"],
    "bow_pulling_2": ["bow_pulling_2"],
    "bread": ["bread"],
    "brick": ["brick"],
    "bucket_empty": ["bucket", "bucket_empty"],
    "bucket_lava": ["lava_bucket", "bucket_lava"],
    "bucket_milk": ["milk_bucket", "bucket_milk"],
    "bucket_water": ["water_bucket", "bucket_water"],
    "carrot": ["carrot"],
    "carrot_golden": ["golden_carrot", "carrot_golden"],
    "charcoal": ["charcoal"],
    "chicken_cooked": ["cooked_chicken", "chicken_cooked"],
    "chicken_raw": ["chicken", "chicken_raw"],
    "cookie": ["cookie"],
    "diamond": ["diamond"],
    "diamond_horse_armor": ["diamond_horse_armor"],
    "door_birch": ["birch_door", "door_birch"],
    "door_iron": ["iron_door", "door_iron"],
    "door_wood": ["oak_door", "door_wood"],
    "emerald": ["emerald"],
    "empty_armor_slot_boots": ["empty_armor_slot_boots"],
    "empty_armor_slot_chestplate": ["empty_armor_slot_chestplate"],
    "empty_armor_slot_helmet": ["empty_armor_slot_helmet"],
    "empty_armor_slot_leggings": ["empty_armor_slot_leggings"],
    "ender_pearl": ["ender_pearl"],
    "experience_bottle": ["experience_bottle"],
    "fireball": ["fire_charge", "fireball"],
    "fishing_rod_cast": ["fishing_rod_cast"],
    "fishing_rod_uncast": ["fishing_rod", "fishing_rod_uncast"],
    "flint": ["flint"],
    "flint_and_steel": ["flint_and_steel"],
    "glowstone_dust": ["glowstone_dust"],
    "gold_ingot": ["gold_ingot"],
    "item_frame": ["item_frame"],
    "leather": ["leather"],
    "nether_star": ["nether_star"],
    "netherbrick": ["nether_brick", "netherbrick"],
    "potato": ["potato"],
    "potato_baked": ["baked_potato", "potato_baked"],
    "potato_poisonous": ["poisonous_potato", "potato_poisonous"],
    "porkchop_cooked": ["cooked_porkchop", "porkchop_cooked"],
    "porkchop_raw": ["porkchop", "porkchop_raw"],
    "potion_bottle_drinkable": ["potion", "potion_bottle_drinkable"],
    "potion_bottle_empty": ["glass_bottle", "potion_bottle_empty"],
    "potion_bottle_splash": ["splash_potion", "potion_bottle_splash"],
    "potion_overlay": ["potion_overlay"],
    "prismarine_crystals": ["prismarine_crystals"],
    "prismarine_shard": ["prismarine_shard"],
    "pumpkin_pie": ["pumpkin_pie"],
    "quartz": ["quartz"],
    "record_chirp": ["music_disc_chirp", "record_chirp"],
    "rotten_flesh": ["rotten_flesh"],
    "seeds_pumpkin": ["pumpkin_seeds", "seeds_pumpkin"],
    "seeds_wheat": ["wheat_seeds", "seeds_wheat"],
    "shears": ["shears"],
    "sign": ["oak_sign", "sign"],
    "slimeball": ["slime_ball", "slimeball"],
    "snowball": ["snowball"],
    "spawn_egg": ["spawn_egg"],
    "spawn_egg_overlay": ["spawn_egg_overlay"],
    "stick": ["stick"],
    "wheat": ["wheat"],
}

_TOOL_PREFIX = {  # nome Blockman -> [nomes Java]
    "wood": ["wooden", "wood"],
    "stone": ["stone"],
    "iron": ["iron"],
    "gold": ["golden", "gold"],
    "diamond": ["diamond"],
}
for _m, _pre in _TOOL_PREFIX.items():
    for _t in ("sword", "pickaxe", "axe", "shovel", "hoe"):
        if _m == "diamond" and _t == "hoe":
            continue  # nao existe no atlas do Blockman GO
        ITEMS["%s_%s" % (_m, _t)] = ["%s_%s" % (p, _t) for p in _pre]
for _m, _pre in (("iron", ["iron"]), ("gold", ["golden", "gold"]),
                 ("diamond", ["diamond"]), ("chainmail", ["chainmail"]),
                 ("leather", ["leather"])):
    for _a in ("helmet", "chestplate", "leggings", "boots"):
        ITEMS["%s_%s" % (_m, _a)] = ["%s_%s" % (p, _a) for p in _pre]
for _a in ("helmet", "chestplate", "leggings", "boots"):
    ITEMS["leather_%s_overlay" % _a] = ["leather_%s_overlay" % _a]

_DYE_SPECIAL = {  # cor Blockman -> nomes Java extras (1.13 antigo)
    "black": ["ink_sac"], "red": ["rose_red"], "green": ["cactus_green"],
    "brown": ["cocoa_beans"], "blue": ["lapis_lazuli"], "white": ["bone_meal"],
    "yellow": ["dandelion_yellow"],
}
for _c in COLORS:
    ITEMS["dye_powder_" + _c] = (["dye_powder_" + _c, "%s_dye" % _j(_c)] +
                                 _DYE_SPECIAL.get(_c, []))


# ----------------------------------------------------------------- skybox
# Origem Java: assets/minecraft/{mcpatcher,optifine}/sky/world0/<prefixo><N>.png
# Destino Blockman: Media/Textures/skybox/<pasta>/<prefixo>_<face>.png
# ATENCAO: prefixo Java -> pasta Blockman e a correspondencia abaixo NAO foram
# validadas no jogo (ajuste aqui se necessario).
SKY_SOURCES = {
    "cloud": ("sunny", "qing"),          # ceu de dia
    "starfield": ("stars", "fanxing"),   # estrelas
}
# Layout confirmado pelo esquema sun.png fornecido:
# linha 1: bottom | top | front
# linha 2: left   | back| right
SKY_GRID_3X2 = [["bottom", "top", "front"],
                ["left", "back", "right"]]
# Os nomes de saida correspondem diretamente as seis faces.
SKY_FACE_TO_BG = {"front": "front", "back": "back", "left": "left",
                  "right": "right", "top": "top", "bottom": "bottom"}
