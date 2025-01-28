from Py4GWCoreLib import *
module_name = "Set title on map load"

class config:
    def __init__(self):
        self.title_applied = False

widget_config = config()

def configure():
    pass

asuran_map_names = {
    "Alcazia Tangle", "Arbor Bay", "Gadd's Encampment", "Magus Stones",
    "Rata Sum", "Riven Earth", "Sparkfly Swamp", "Tarnished Haven",
    "Umbral Grotto", "Verdant Cascades", "Vlox's Falls",
    "Finding the Bloodstone (Level 1)", "Finding the Bloodstone (Level 2)",
    "Finding the Bloodstone (Level 3)", "The Elusive Golemancer (Level 1)",
    "The Elusive Golemancer (Level 2)", "The Elusive Golemancer (Level 3)"
}

deldrimor_map_names = {
    "A Gate Too Far (Level 1)", "A Gate Too Far (Level 2)", "A Gate Too Far (Level 3)",
    "A Time for Heroes", "Central Transfer Chamber", "Destruction's Depths (Level 1)",
    "Destruction's Depths (Level 2)", "Destruction's Depths (Level 3)",
    "Genius Operated Living Enchanted Manifestation", "Glint's Challenge",
    "Raven's Point (Level 1)", "Raven's Point (Level 2)", "Raven's Point (Level 3)"
}

norn_map_names = {
    "Attack of the Nornbear", "Bjora Marches", "Blood Washes Blood",
    "Boreal Station", "Cold as Ice", "Curse of the Nornbear",
    "Drakkar Lake", "Eye of the North", "Gunnar's Hold", "Ice Cliff Chasms",
    "Jaga Moraine", "Mano a Norn-o", "Norrhart Domains", "Olafstead",
    "Service in Defense of the Eye", "Sifhalla", "The Norn Fighting Tournament",
    "Varajar Fells"
}

vanguard_map_names = {
    "Against the Charr", "Ascalon City", "Assault on the Stronghold",
    "Cathedral of Flames (Level 1)", "Cathedral of Flames (Level 2)",
    "Cathedral of Flames (Level 3)", "Dalada Uplands", "Diessa Lowlands",
    "Doomlore Shrine", "Dragon's Gullet", "Eastern Frontier",
    "Flame Temple Corridor", "Fort Ranik", "Frontier Gate", "Grendich Courthouse",
    "Grothmar Wardowns", "Longeye's Ledge", "Nolani Academy", "Old Ascalon",
    "Piken Square", "Regent Valley", "Rragar's Menagerie (Level 1)",
    "Rragar's Menagerie (Level 2)", "Rragar's Menagerie (Level 3)",
    "Ruins of Surmia", "Sacnoth Valley", "Sardelac Sanitarium",
    "The Breach", "The Great Northern Wall", "Warband Training",
    "Warband of Brothers (Level 1)", "Warband of Brothers (Level 2)",
    "Warband of Brothers (Level 3)"
}

lightbringer_map_names = {
    "Abaddon's Gate", "Basalt Grotto", "Bone Palace", "Crystal Overlook",
    "Depths of Madness", "Domain of Anguish", "Domain of Fear", "Domain of Pain",
    "Domain of Secrets", "The Ebony Citadel of Mallyx", "Dzagonur Bastion",
    "Forum Highlands", "Gate of Desolation", "Gate of Fear", "Gate of Madness",
    "Gate of Pain", "Gate of Secrets", "Gate of Torment", "Gate of the Nightfallen Lands",
    "Grand Court of Sebelkeh", "Heart of Abaddon", "Jennur's Horde", "Joko's Domain",
    "Lair of the Forgotten", "Nightfallen Coast", "Nightfallen Garden",
    "Nightfallen Jahai", "Nundu Bay", "Poisoned Outcrops", "Remains of Sahlahja",
    "Ruins of Morah", "The Alkali Pan", "The Mirror of Lyss", "The Mouth of Torment",
    "The Ruptured Heart", "The Shadow Nexus", "The Shattered Ravines",
    "The Sulfurous Wastes", "Throne of Secrets", "Vehtendi Valley", "Yatendi Canyons"
}

def main():
    global widget_config
    if (Map.IsMapReady() and Map.IsExplorable() and Party.IsPartyLoaded() and widget_config.title_applied == False):
         # Check which set the map name belongs to and return the corresponding TitleID
        map_name = Map.GetMapName()
        if map_name in asuran_map_names:
            Player.SetActiveTitle(TitleID.Asuran.value)
        elif map_name in deldrimor_map_names:
            Player.SetActiveTitle(TitleID.Deldrimor.value)
        elif map_name in norn_map_names:
            Player.SetActiveTitle(TitleID.Norn.value)
        elif map_name in vanguard_map_names:
            Player.SetActiveTitle(TitleID.Vanguard.value)
        elif map_name in lightbringer_map_names:
            Player.SetActiveTitle(TitleID.Lightbringer.value)
        else:
            return None  # Default if no match found
        widget_config.title_applied = True
        
    if not Map.IsExplorable():
        widget_config.title_applied = False

if __name__ == "__main__":
    main()

