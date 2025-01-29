from logging import exception
from Py4GWCoreLib import *
from datetime import datetime
from abc import ABC, abstractmethod
from WindowUtilites import *

import Mapping
import Items

pyParty = PyParty.PyParty()

class Heroes:
    Norgu = 1
    Goren = 2
    Tahlkora = 3
    MasterOfWhispers = 4
    AcolyteJin = 5
    Koss = 6
    Dunkoro = 7
    AcolyteSousuke = 8
    Melonni = 9
    ZhedShadowhoof = 10
    GeneralMorgahn = 11
    MagridTheSly = 12
    Zenmai = 13
    Olias = 14
    Razah = 15
    MOX = 16
    KeiranThackeray = 17
    Jora = 18
    PyreFierceshot = 19
    Anton = 20
    Livia = 21
    Hayda = 22
    Kahmu = 23
    Gwen = 24
    Xandra = 25
    Vekk = 26
    Ogden = 27
    MercenaryHero1 = 28
    MercenaryHero2 = 29
    MercenaryHero3 = 30
    MercenaryHero4 = 31
    MercenaryHero5 = 32
    MercenaryHero6 = 33
    MercenaryHero7 = 34
    MercenaryHero8 = 35
    Miku = 36
    ZeiRi = 37

    @staticmethod
    def Exists(value):
        return any(value == getattr(Heroes, attr) for attr in vars(Heroes))

class GameAreas:
    Touch = 144
    Adjacent = 166
    Nearby = 252
    Area = 322
    Lesser_Earshot = 900
    Earshot = 1012 
    Spellcast = 1248
    Spirit = 2500
    Compass = 5000

################## SKILL HANDLING ROUTINES ##################

class aftercast_class:
    in_aftercast = False
    aftercast_time = 0
    aftercast_timer = Timer()
    aftercast_timer.Start()

    def update(self):
        if self.aftercast_timer.HasElapsed(self.aftercast_time):
            self.in_aftercast = False
            self.aftercast_time = 0
            self.aftercast_timer.Stop()

    def set_aftercast(self, skill_id):
        self.in_aftercast = True
        self.aftercast_time = Skill.Data.GetActivation(skill_id) + Skill.Data.GetAftercast(skill_id) + 600
        self.aftercast_timer.Reset()


aftercast = aftercast_class()

def TargetNearestItem():
    items = AgentArray.GetItemArray()
    items = AgentArray.Filter.ByDistance(items,Player.GetXY(), 200)
    items = AgentArray.Sort.ByDistance(items, Player.GetXY())
    if len(items) > 0:        
        Player.ChangeTarget(items[0])

### --- CHECK BUFF EXISTS --- ###
def HasBuff(agent_id, skill_id):
    if Effects.BuffExists(agent_id, skill_id) or Effects.EffectExists(agent_id, skill_id):
        return True
    return False

def BuffTimeRemaining(agent_id, skill_id):
    if HasBuff(agent_id, skill_id):
        buffs = Effects.GetBuffs(agent_id)

        Agent.GetAttributes()

        if buffs:
            for buff in buffs:
                if buff.skill_id == skill_id:
                    return buff.time_remaining
        
        effects = Effects.GetEffects(agent_id)

        if effects:
            for effect in effects:
                if effect.skill_id == skill_id:
                    return effect.time_remaining

def GetAllEffectsTimeRemaining(agent_id):
    effects = Effects.GetEffects(agent_id)

    effects_time = []

    for effect in effects: 
        combo = (effect.skill_id, effect.time_remaining)
        effects_time = combo

    return effects_time

### --- CHECK SKILLS --- ###
def IsSkillReadyById(skill_id):
    return IsSkillReadyBySlot(SkillBar.GetSlotBySkillID(skill_id))

def IsSkillReadyBySlot(skill_slot):
    skill = SkillBar.GetSkillData(skill_slot)
    return skill.recharge == 0

def HasEnoughEnergy(skill_id):
    player_agent_id = Player.GetAgentID()
    energy = Agent.GetEnergy(player_agent_id)
    max_energy = Agent.GetMaxEnergy(player_agent_id)
    energy_points = int(energy * max_energy)

    return Skill.Data.GetEnergyCost(skill_id) <= energy_points

def CanCast():
    return CanCast(Player.GetAgentID())

def CanCast(player_id):
    if not player_id:
        return False
    
    global aftercast
    aftercast.update()

    if (Agent.IsCasting(player_id) 
        or Agent.IsKnockedDown(player_id)
        or Agent.IsDead(player_id)
        or aftercast.in_aftercast):
        return False
    return True

def CastSkillById(skill_id):
    global aftercast
    SkillBar.UseSkill(SkillBar.GetSlotBySkillID(skill_id))
    aftercast.set_aftercast(skill_id)
 
def CastSkillBySlot(skill_slot):
    global aftercast
    SkillBar.UseSkill(skill_slot)
    aftercast.set_aftercast(SkillBar.GetSkillIDBySlot(skill_slot))

### --- CHECK ENEMY POSITION --- ###
def IsEnemyBehind (agent_id):
    player_agent_id = Player.GetAgentID()
    player_x, player_y = Agent.GetXY(player_agent_id)
    player_angle = Agent.GetRotationAngle(player_agent_id)  # Player's facing direction
    nearest_enemy = agent_id
    #if target is None:
    Player.ChangeTarget(nearest_enemy)
    #target = nearest_enemy
    nearest_enemy_x, nearest_enemy_y = Agent.GetXY(nearest_enemy)
                

    # Calculate the angle between the player and the enemy
    dx = nearest_enemy_x - player_x
    dy = nearest_enemy_y - player_y
    angle_to_enemy = math.atan2(dy, dx)  # Angle in radians
    angle_to_enemy = math.degrees(angle_to_enemy)  # Convert to degrees
    angle_to_enemy = (angle_to_enemy + 360) % 360  # Normalize to [0, 360]

    # Calculate the relative angle to the enemy
    angle_diff = (angle_to_enemy - player_angle + 360) % 360

    if angle_diff < 45 or angle_diff > 315:
        return True
    return False

### --- HEROES --- ###
# Check if hero in party
def IsHeroInParty(id: int):
    # Ensure the hero id is in deed a hero.
    if not Heroes.Exists(id):
        return False
    
    if Party.GetHeroCount() == 0:
        return False
    
    for _, hero in enumerate(Party.GetHeroes()):
        if hero.hero_id == id:
            return True
        
    return False

### --- HEROES --- ###

### --- REPORTS PROGRESS --- ###
class ReportsProgress():
    window = None    
    step_transition_threshold_timer = Timer()

    def __init__(self, window):
        if issubclass(type(window), BasicWindow):
            self.window = window
            
    def UpdateState(self, state):
        if issubclass(type(self.window), BasicWindow):
            self.window.UpdateState(state)

    def Log(self, text, msgType=Py4GW.Console.MessageType.Info):
        if issubclass(type(self.window_impl), BasicWindow):
            self.window.Log(text, msgType)

    def CanPickUp(self, agentId):
        return agentId != None and agentId != 0

    def GetNearestPickupItem(self):
        try:            
            items = AgentArray.GetItemArray()
            items = AgentArray.Filter.ByDistance(items, Player.GetXY(), GameAreas.Lesser_Earshot)
            items = AgentArray.Sort.ByDistance(items, Player.GetXY())

            if items != None and len(items) > 0:
                for item in items:
                    if self.CanPickUp(item):
                        return item
            
            return 0
        except exception as e:
            Py4GW.Console.Log("Utilities", f"GetNearestPickupItem error {e}")

    def ExecuteTimedStep(self, state, function):
        if not self.step_transition_threshold_timer.IsRunning():
            self.step_transition_threshold_timer.Start()

        self.ExecuteStep(state, function)

    def ExecuteStep(self, state, function):
        self.UpdateState(state)

        # Try to execute the function if present.        
        try:
            if callable(function):
                function()
        except:
            self.Log(f"Calling function {function.__name__} failed", Py4GW.Console.MessageType.Error)
    
    def ShouldForceTransitionStep(self, custom_threshold=300000):        
        if not self.step_transition_threshold_timer.IsRunning():
            self.step_transition_threshold_timer.Start()
            return False

        elapsed = self.step_transition_threshold_timer.HasElapsed(custom_threshold)

        if elapsed:
            self.Log("Forced Step Transition", Py4GW.Console.MessageType.Warning)
            self.step_transition_threshold_timer.Reset()
        return elapsed
    
### --- REPORTS PROGRESS --- ###

class SalvageFsm(FSM):
    inventoryHandler = PyInventory.PyInventory()   
    salvageItems = True

    def __init__(self, name="SalvageFsm", salvageItems=True):
        super().__init__(name)
        self.name = name
        self.salvageItems = salvageItems

        self.AddState("StartSalvage",
                        execute_fn=lambda: self.StartSalvage(),
                        transition_delay_ms=350)
        self.AddState("ContinueSalvage",
                        execute_fn=lambda: self.ContinueSalvage(),
                        transition_delay_ms=350)
        self.AddState("FinishSalvage",
                        execute_fn=lambda: self.FinishSalvage(),
                        transition_delay_ms=300)
        self.AddState("HandleSalvageLoop",
                        execute_fn=lambda: self.EndSalvageLoop())
        
    def StartSalvage(self):
        if not self.salvageItems:
            return True
        
        salvage_kit = Inventory.GetFirstSalvageKit()
        if salvage_kit == 0:
            return
    
        salvage_item_id = Inventory.GetFirstSalvageableItem()
        if salvage_item_id == 0:
            return False

        self.inventoryHandler.StartSalvage(salvage_kit, salvage_item_id)

    def ContinueSalvage(self):
        if not self.salvageItems:
            return True
        
        Keystroke.PressAndRelease(Key.Y.value)
        #this is a fix for salvaging with a lesser kit, it will press Y to confirm the salvage
        #this produces the default key for minions to open, need to implenet an IF statement 
        #to check wich type os salvaging youre performing
        #the game itself wont salvage an unidentified item, so be aware of that
        self.inventoryHandler.HandleSalvageUI()
        pass

    def FinishSalvage(self):        
        if not self.salvageItems:
            return True
        
        self.inventoryHandler.FinishSalvage()
        pass

    def EndSalvageLoop(self):
        if not self.salvageItems:
            return True
        
        if not self.IsFinishedSalvage():
            self.jump_to_state_by_name("StartSalvage")
        else:
            self.finished = True
    
    def IsFinishedSalvage(self):
        if not self.salvageItems:
            return True
        
        salvage_kit = Inventory.GetFirstSalvageKit()
        salvage_item_id = Inventory.GetFirstSalvageableItem()

        if salvage_kit == 0 or salvage_item_id == 0:
            return True

        return False
    
def GetSalvageRoutine(name="SalvageRoutine", logActions=False):
        salvage_routine = SalvageFsm(name, logActions)
        return salvage_routine

class InventoryFsm(FSM):
    idItems = False
    salvageItems = False
    sellItems = True
    sellWhites = True
    sellBlues = True
    sellGrapes = True
    sellGolds = True
    sellGreens = True
    sellMaterials = True

    gold_to_keep = 5000
    gold_to_store = 0
    gold_stored = 0
    gold_char_snapshot = 0
    gold_storage_snapshot = 0
    sell_item_count = 0

    inventory_handle_gold = "Handle Gold Onhand"
    inventory_buy_id_kits = "Buy ID Kits"
    inventory_sell_items = "Sell Items"

    action_timer = Timer()
    
    merchant_path = None
    merchant_map_id = Mapping.Kamadan
    movement_handler = Routines.Movement.FollowXY(50)

    salvager = None
    salvager_name = "SalvageFsm"

    # keeps list of inventory at time of creation, ensuring not to sell those items.
    current_Inventory = []

    # keeps the listed model ids in inventory, ensuring not to sell those items
    keep_items = []
    logFunc = None

    def __init__(self, name, merchantMapId, pathToMerchant, currentInventory=None, modelIdsToKeep=None, 
                 idItems = True, salvageItems = False, sellItems=True, sellWhites=True, sellBlues=True, 
                 sellGrapes=True, sellGolds=True, sellGreens=True, sellMaterials=False, goldToKeep=5000,
                 logFunc=None):
        super().__init__(name)

        self.merchant_map_id = merchantMapId
        self.merchant_path = Routines.Movement.PathHandler(pathToMerchant)
        self.current_Inventory = currentInventory
        self.keep_items = modelIdsToKeep
        self.idItems = idItems
        self.salvageItems = salvageItems
        self.sellItems = sellItems
        self.sellWhites = sellWhites
        self.sellBlues = sellBlues
        self.sellGrapes = sellGrapes
        self.sellGolds = sellGolds
        self.sellGreens = sellGreens
        self.sellMaterials = sellMaterials
        self.gold_to_keep = goldToKeep
        self.logFunc = logFunc
        
        self.salvager = SalvageFsm(self.salvager_name, self.salvageItems)
        
        self.AddState(name=self.inventory_handle_gold,
            execute_fn=lambda: self.CheckGold(),
            exit_condition=lambda: Inventory.GetGoldOnCharacter() == self.gold_to_keep or Inventory.GetGoldInStorage() == 0,
            transition_delay_ms=2000)
        
        self.AddState(name="Go to Merchant",
            execute_fn=lambda: Routines.Movement.FollowPath(self.merchant_path, self.movement_handler),
            exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.merchant_path, self.movement_handler),
            run_once=False)
        
        self.AddState(name="Target Merchant",
            execute_fn=lambda: self.TargetNearestNpc(),
            transition_delay_ms=1000)
        
        self.AddState(name="InteractMerchant",
            execute_fn=lambda: Routines.Targeting.InteractTarget(),
            exit_condition=lambda: Routines.Targeting.HasArrivedToTarget())
        
        self.AddState(name="Sell Materials to make Space",
            execute_fn=lambda: self.SellMaterials(),
            run_once=False,
            exit_condition=lambda: self.SellingMaterialsComplete())
        
        self.AddState(name=self.inventory_buy_id_kits,
            execute_fn=lambda: self.BuyIdKits(),
            run_once=False,
            exit_condition=lambda: self.BuyIdKitsComplete())
        
        # no need to add salvager routine if not salvaging
        self.AddState(name="Buy Salvage Kits",
            execute_fn=lambda: self.BuySalvageKits(),
            run_once=False,
            exit_condition=lambda: self.BuySalvageKitsComplete())
        
        self.AddState(name="Identify routine",
            execute_fn=lambda: self.IdentifyItems(),
            run_once=False,
            exit_condition=lambda: self.IdentifyItemsComplete())
        
        self.AddState(name=self.inventory_sell_items,
            execute_fn=lambda: self.SellItems(),
            run_once=False,
            exit_condition=lambda: self.SellItemsComplete())
        
        # no need to add salvager routine if not salvaging
        self.AddSubroutine(name="Salvage Subroutine",
            sub_fsm = self.salvager,
            condition_fn=lambda: not self.salvager.IsFinishedSalvage())
                
        self.AddState(name="Sell Materials",
            execute_fn=lambda: self.SellMaterials(),
            run_once=False,
            exit_condition=lambda: self.SellingMaterialsComplete())
        
        self.AddState(name="Deposit Items",
            execute_fn=lambda: self.DepositItems(),
            run_once=False,
            exit_condition=lambda: self.DepositItemsComplete())
        
    def Log(self, text, msgType=Py4GW.Console.MessageType.Info):
        if not self.logFunc:
            return
        self.logFunc(text, msgType)

    def TargetNearestNpc(self):
        npc_array = AgentArray.GetNPCMinipetArray()
        npc_array = AgentArray.Filter.ByDistance(npc_array,Player.GetXY(), 200)
        npc_array = AgentArray.Sort.ByDistance(npc_array, Player.GetXY())

        if len(npc_array) > 0:
            Player.ChangeTarget(npc_array[0])

    def SellItems(self):     
        if not self.sellItems:
            return
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()
        
        if not self.action_timer.HasElapsed(250):
            return
        
        self.action_timer.Reset()

        # Get items from inventory
        # current inventory is [bagNum, slotsFilled]
        items_to_sell = GetInventoryNonKeepItemsByBagSlot(self.current_Inventory)
        items_to_sell = GetInventoryNonKeepItemsByModelId(self.keep_items, items_to_sell)
        items_to_sell = GetItemIdList(items_to_sell)
        items_to_sell = ItemArray.Filter.ByCondition(items_to_sell, lambda item_id: not Item.Type.IsMaterial(item_id))
        items_to_sell = ItemArray.Filter.ByCondition(items_to_sell, lambda item_id: not Item.Type.IsRareMaterial(item_id))
            
        # Filter gold items
        if self.sellWhites:
            white_items = ItemArray.Filter.ByCondition(items_to_sell, Item.Rarity.IsWhite)
            
        if self.sellBlues:
            blue_items = ItemArray.Filter.ByCondition(items_to_sell, Item.Rarity.IsBlue)
            
        if self.sellGrapes:
            grape_items = ItemArray.Filter.ByCondition(items_to_sell, Item.Rarity.IsPurple)
            
        if self.sellGolds:
            gold_items = ItemArray.Filter.ByCondition(items_to_sell, Item.Rarity.IsGold)

        if self.sellGreens:
            green_items = ItemArray.Filter.ByCondition(items_to_sell, Item.Rarity.IsGreen)

        items_to_sell.clear()
        items_to_sell.extend(white_items)
        items_to_sell.extend(blue_items)
        items_to_sell.extend(grape_items)
        items_to_sell.extend(gold_items)
        items_to_sell.extend(green_items)
        
        self.sell_item_count = len(items_to_sell)

        # Sell the gold items if available and timer allows
        if self.sell_item_count > 0: 
            item_id = items_to_sell[0]
            quantity = Item.Properties.GetQuantity(item_id)
            value = Item.Properties.GetValue(item_id)
            cost = quantity * value

            Trading.Merchant.SellItem(item_id, cost)

    def SellItemsComplete(self):
        if not self.sellItems:
            return True

        # Check if there are no remaining gold items
        if self.sell_item_count == 0:
            self.action_timer.Stop()         
            return True

        return False
    
    def SellMaterials(self):
        if not self.sellMaterials:
            return
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        items_to_sell = GetInventoryNonKeepItemsByBagSlot(self.current_Inventory)
        items_to_sell = GetInventoryNonKeepItemsByModelId(self.keep_items, items_to_sell)
        items_to_sell = (item for item in items_to_sell if Item.Type.IsMaterial(item.item_id))
        items_to_sell = GetItemIdList(items_to_sell)

        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        items_to_sell = ItemArray.GetItemArray(bags_to_check)
        items_to_sell = ItemArray.Filter.ByCondition(items_to_sell, lambda item_id: Item.Type.IsMaterial(item_id))

        self.sell_item_count = len(items_to_sell)

        if self.sell_item_count > 0 and self.action_timer.HasElapsed(250):
            item_id = items_to_sell[0]
            quantity = Item.Properties.GetQuantity(item_id)
            value = Item.Properties.GetValue(item_id)
            cost = quantity * value
            Trading.Merchant.SellItem(item_id, cost)
            self.action_timer.Reset()

    def SellingMaterialsComplete(self):        
        if self.sell_item_count == 0:
            self.action_timer.Stop()
            return True

        return False

    def BuyIdKits(self):
        if not self.idItems:
            return
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()


        if not self.action_timer.HasElapsed(250):
            return
        
        kits_in_inv = Inventory.GetModelCount(Items.Id_Kit_Superior)

        if kits_in_inv == 0:
            merchant_item_list = Trading.Merchant.GetOfferedItems()
            merchant_item_list = ItemArray.Filter.ByCondition(merchant_item_list, lambda item_id: Item.GetModelID(item_id) == Items.Id_Kit_Superior)

            if len(merchant_item_list) > 0:
                item_id = merchant_item_list[0]
                value = Item.Properties.GetValue(item_id) * 2 # value is reported is sell value not buy value
                Trading.Merchant.BuyItem(item_id, value)
            else:
                Py4GW.Console.Log("Buy ID Kits", f"No ID kits available from merchant.",Py4GW.Console.MessageType.Info)

        
        self.action_timer.Reset()

    def BuyIdKitsComplete(self):
        if not self.idItems:
            return True
        
        kits_in_inv = Inventory.GetModelCount(Items.Id_Kit_Superior)

        if kits_in_inv >= 1:
            self.action_timer.Stop()
            return True

        return False

    def BuySalvageKits(self):
        if not self.salvageItems:
            return
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        kits_in_inv = Inventory.GetModelCount(Items.Salve_Kit_Basic)

        merchant_item_list = Trading.Merchant.GetOfferedItems()
        merchant_item_list = ItemArray.Filter.ByCondition(merchant_item_list, lambda item_id: Item.GetModelID(item_id) == Items.Salve_Kit_Basic)

        if kits_in_inv <= 1 and self.action_timer.HasElapsed(250):
            item_id = merchant_item_list[0]
            quantity = Item.Properties.GetQuantity(item_id)
            value = Item.Properties.GetValue(item_id) *2 # value is reported is sell value not buy value
            Trading.Merchant.BuyItem(item_id, value)
            self.action_timer.Reset()

    def BuySalvageKitsComplete(self):
        if not self.salvageItems:
            return True
        
        kits_in_inv = Inventory.GetModelCount(Items.Salve_Kit_Basic)

        if kits_in_inv >= 1:
            return True

        return False

    def CheckGold(self):        
        charGold = Inventory.GetGoldOnCharacter()

        if charGold < self.gold_to_keep:
            Inventory.WithdrawGold(self.gold_to_keep - charGold)
        else:
            Inventory.DepositGold(charGold - self.gold_to_keep)        

    """def WithdrawGold(self, gold):
        if gold == 0:
            return
        
        Inventory.WithdrawGold(gold)        

    def DepositGold(self, gold):
        if gold == 0:
            return
        
        Inventory.DepositGold(gold)

         if not self.action_timer.IsRunning():
            self.action_timer.Start()

        if not self.action_timer.HasElapsed(250):
            return
        
        charGold = Inventory.GetGoldOnCharacter()
        
        # gold was already deposited
        if charGold < self.gold_char_snapshot:
            return
        
        if charGold <= self.gold_to_keep:
            return
        
        if gold == -1:
            gold = charGold - self.gold_to_keep

        if gold > charGold:
            gold = charGold

        if charGold - gold < self.gold_to_keep:
            gold = charGold - self.gold_to_keep
        
        if gold == 0:
            return

        self.gold_char_snapshot = charGold

        storageGold = Inventory.GetGoldInStorage()

        if storageGold > self.gold_storage_snapshot:
            return
        
        if storageGold + gold > 1000000:
            gold = 1000000 - storageGold
        
        self.gold_storage_snapshot = storageGold
        
        Inventory.DepositGold(gold)
        self.action_timer.Reset()

    def DepositGoldComplete(self):
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        if not self.action_timer.HasElapsed(250):
            return
        
        charGold = Inventory.GetGoldOnCharacter()
        storageGold = Inventory.GetGoldInStorage()
        
        if charGold == 0 or charGold <= self.gold_to_keep or storageGold == 1000000 or (charGold < self.gold_char_snapshot and storageGold > self.gold_storage_snapshot):
            self.gold_char_snapshot = 0
            self.gold_storage_snapshot = 0
            self.action_timer.Reset()
            return True
        
        return False """

    def DepositItems(self):
        # selling so no deposit
        if self.sellItems:
            return
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        if not self.action_timer.HasElapsed(250):
            return
        
        items, space = Inventory.GetStorageSpace()

        if items == space:
            return True
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        items_to_deposit = ItemArray.GetItemArray(bags_to_check)

        banned_models = {Items.Id_Kit_Basic,Items.Salve_Kit_Basic}
        items_to_deposit = ItemArray.Filter.ByCondition(items_to_deposit, lambda item_id: Item.GetModelID(item_id) not in banned_models)


        if len(items_to_deposit) > 0:
            Inventory.DepositItemToStorage(items_to_deposit[0])
            self.action_timer.Reset()

    def DepositItemsComplete(self):
        # selling so no deposit
        if self.sellItems:
            return True
        items, space = Inventory.GetStorageSpace()

        if items == space:
            return True

        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        items_to_deposit = ItemArray.GetItemArray(bags_to_check)

        banned_models = {Items.Id_Kit_Basic,Items.Salve_Kit_Basic}
        items_to_deposit = ItemArray.Filter.ByCondition(items_to_deposit, lambda item_id: Item.GetModelID(item_id) not in banned_models)

        if len(items_to_deposit) == 0:
            return True

        return False

    def IdentifyItems(self):
        if not self.idItems:
            return True
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        if not self.action_timer.HasElapsed(250):
            return
        
        id_kit = Inventory.GetFirstIDKit()

        if id_kit == 0:
            self.jump_to_state_by_name(self.inventory_buy_id_kits)
            return

        unidentified_items = self.FilterItemsToId()
        
        if len(unidentified_items) >0 and self.action_timer.HasElapsed(250):
            Inventory.IdentifyItem(unidentified_items[0], id_kit)
            self.action_timer.Reset()

    def IdentifyItemsComplete(self):                      
        if not self.idItems:
            return True
        
        if not self.action_timer.IsRunning():
            self.action_timer.Start()

        if self.action_timer.HasElapsed(250):                              
            unidentified_items = self.FilterItemsToId()

            if len(unidentified_items) == 0:
                self.action_timer.Reset()
                return True

        return False
    
    def FilterItemsToId(self):
        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        unidentified_items = ItemArray.GetItemArray(bags_to_check)
        unidentified_items = ItemArray.Filter.ByCondition(unidentified_items, lambda item_id: Item.Usage.IsIdentified(item_id) == False)
        unidentified_items = ItemArray.Filter.ByCondition(unidentified_items, lambda item_id: Item.Rarity.IsWhite(item_id) == False)

        return unidentified_items

    def Reset(self):
        self.reset()
        
        if self.merchant_path:
            self.merchant_path.reset()

        if self.movement_handler:
            self.movement_handler.reset()
'''
    keepItems should be [modelId] regardless of slot
'''
def GetInventoryNonKeepItemsByModelId(keepItems = [], input = None):
    if isinstance(input, list):
        items = input
    else:
        items = GetItems(ItemArray.CreateBagList(1, 2, 3, 4))

    sell_items = []

    for item in items:
        model = Item.GetModelID(item.item_id)

        if model in keepItems:
            continue

        sell_items.append(item)

    return sell_items

'''
    keepSlots should be [bagNum, slots].
'''
def GetInventoryNonKeepItemsByBagSlot(keepSlots = [], logFunc = None):    
    all_item_ids = []  # To store item IDs from all bags

    bags = ItemArray.CreateBagList(1, 2, 3, 4)

    if logFunc != None:
        logFunc(f"{type(keepSlots)}")

    for bag_enum in bags:
        try:
            # Create a Bag instance
            bag_instance = PyInventory.Bag(bag_enum.value, bag_enum.name)
        
            # Get all items in the bag
            items_in_bag = bag_instance.GetItems()

            for (keepBag, keeps) in keepSlots:
                if keepBag == bag_enum.value:
                    # this is a slot in the bag
                    if isinstance(keeps, list):
                        for item in items_in_bag:
                            # this item slot not in the keeps pile, so mark it for sale
                            if item.slot not in keeps:
                                all_item_ids.append(item)

        except exception as e:
            Py4GW.Console.Log("GetInventoryItemsToSellByBagSlot", "error in function", Py4GW.Console.MessageType.Error)

    return all_item_ids

def GetItemIdList(input):
    if not isinstance(input, list):
        return

    item_id_list = []

    for item in input:
        item_id_list.append(item.item_id)
        
    return item_id_list

def GetItems(bags):
    all_item_ids = []  # To store item IDs from all bags

    for bag_enum in bags:
        try:
            # Create a Bag instance
            bag_instance = PyInventory.Bag(bag_enum.value, bag_enum.name)
        
            # Get all items in the bag
            items_in_bag = bag_instance.GetItems()
        
            all_item_ids.extend(items_in_bag)
        
        except Exception as e:
            Py4GW.Console.Log(e)

    return all_item_ids

def GetItemBagSlotList(bags):
    all_item_ids = []  # To store item IDs from all bags

    for bag_enum in bags:
        try:
            # Create a Bag instance
            bag_instance = PyInventory.Bag(bag_enum.value, bag_enum.name)
        
            # Get all items in the bag
            items_in_bag = bag_instance.GetItems()
            
            slots = []

            for item in items_in_bag:
                slots.append(item.slot)

            # output should be [int, list]
            all_item_ids.append((bag_enum.value, slots))
                
        except Exception as e:
            Py4GW.Console.Log(e)

    return all_item_ids

def CheckIfKeepItemsInInventory(keepItems = [], bagSlots = []):
    if bagSlots == None:
        bagSlots = GetItemBagSlotList(ItemArray.CreateBagList(1,2,3,4))

    for bag, items in bagSlots:
        pass


def GetInventoryItemSlots(bags=None):
    if bags == None:
        bags = ItemArray.CreateBagList(1, 2, 3, 4)

    all_item_ids = []  # To store item IDs from all bags [bagNum, slotNum]

    for bag_enum in bags:
        try:
            # Create a Bag instance
            bag_instance = PyInventory.Bag(bag_enum.value, bag_enum.name)
        
            # Get all items in the bag
            items_in_bag = bag_instance.GetItems()

            slots = []

            for item in items_in_bag:
                slots.append(item.slot)

            # output should be [int, list]
            all_item_ids.append((bag_enum.value, slots))
        
        except Exception as e:
            Py4GW.Console.Log(e)

    return all_item_ids
