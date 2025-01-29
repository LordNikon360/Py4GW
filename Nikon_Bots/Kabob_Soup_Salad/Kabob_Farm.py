from logging import exception
from Py4GWCoreLib import *
from BotUtilities import *
from WindowUtilites import *

import Mapping
import Items

bot_name = "Nikons Kabob Farm"

kabob_selected = True
kabob_input = 5

class Kabob_Window(BasicWindow):
    def __init__(self, window_name="Basic Window", window_size = [350.0, 400.0], show_logger = True, show_state = True):
        super().__init__(window_name, window_size, show_logger, show_state)

    def ShowControls(self):
        global kabob_selected, kabob_input 
        
        PyImGui.text("Collect:")

        if PyImGui.begin_table("Collect_Inputs", 2):  # Use begin_table for starting a table
            # Drake Kabob
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            kabob_selected = PyImGui.checkbox("Draka Kabob", kabob_selected)  
            PyImGui.table_next_column()
            kabob_input = PyImGui.input_int("# Kabobs", kabob_input) if kabob_input >= 0 else 0

            PyImGui.table_next_row()
            PyImGui.end_table()
        
        PyImGui.separator()
        PyImGui.text("Results:")

        if PyImGui.begin_table("Runs_Results", 5):
            kabob_data = GetKabobData()
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            PyImGui.text(f"Runs: {kabob_data[0]}")
            PyImGui.table_next_column()
            PyImGui.text(f"Success: ")
            PyImGui.table_next_column()
            PyImGui.text_colored(f"{kabob_data[1]}", [0, 1, 0, 1])
            PyImGui.table_next_column()
            PyImGui.text(f"Fails:")
            PyImGui.table_next_column()
            fails = kabob_data[0] - kabob_data[1]

            if fails > 0:
                PyImGui.text_colored(f"{fails}", [1, 0, 0, 1])
            else:
                PyImGui.text(f"{fails}")

            PyImGui.table_next_row()
            PyImGui.end_table()

        if PyImGui.begin_table("Collect_Results", 3):  # Use begin_table for starting a table
            # Drake Kabob
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            PyImGui.text("Kabobs:")
            PyImGui.table_next_column()
            if kabob_selected and kabob_input > 0 and GetKabobCollected() == 0:            
                PyImGui.text_colored(f"{GetKabobCollected()}", [1, 0, 0, 1])
            else:
                PyImGui.text_colored(f"{GetKabobCollected()}", [0, 1, 0, 1])
            PyImGui.table_next_column()
            PyImGui.text(f"collected of {kabob_input}")

            PyImGui.table_next_row()
            PyImGui.end_table()

        if PyImGui.begin_table("Bot_Controls", 4):  # Use begin_table for starting a table
            # Drake Kabob
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            if PyImGui.button("Start Farm"):
                StartBot()
            PyImGui.table_next_column()            
            if PyImGui.button("Stop Farm"):
                StopBot()     
                
            PyImGui.table_next_column()            
            if PyImGui.button("Reset"):
                ResetBot()  

            PyImGui.table_next_column()            
            if PyImGui.button("Print Saved Slots"):
                PrintData()   

            PyImGui.table_next_row()
            PyImGui.end_table()

class Kabob_Farm(ReportsProgress):
    class Kabob_Skillbar:    
        def __init__(self):
            self.sand_shards = SkillBar.GetSkillIDBySlot(1)
            self.vos = SkillBar.GetSkillIDBySlot(2)
            self.staggering = SkillBar.GetSkillIDBySlot(3)
            self.eremites = SkillBar.GetSkillIDBySlot(4)
            self.intimidating = SkillBar.GetSkillIDBySlot(5)
            self.sanctity = SkillBar.GetSkillIDBySlot(6)
            self.regen = SkillBar.GetSkillIDBySlot(7)
            self.hos = SkillBar.GetSkillIDBySlot(8)

    Kabob_Routine = FSM("Kabob_Main")
    Kabob_Skillbar_Code = "Ogek8Np5Kzmj59brdbu731L7FBC"
    Kabob_Hero_Skillbar_Code = "OQkiUxm8sjJxsYAAAAAAAAAA"

    kabob_inventory_routine = "DoInventoryRoutine"
    kabob_initial_check_inventory = "Kabob- Inventory Check"
    kabob_check_inventory_after_handle_inventory = "Kabob- Inventory Handled?"
    kabob_travel_state_name = "Kabob- Traveling to Rihlon"
    kabob_set_normal_mode = "Kabob- Set Normal Mode"
    kabob_add_hero_state_name = "Kabob- Adding Koss"
    kabob_load_skillbar_state_name = "Kabob- Load Skillbar"
    kabob_pathing_1_state_name = "Kabob- Leaving Outpost 1"
    kabob_resign_pathing_state_name = "Kabob- Setup Resign"
    kabob_pathing_2_state_name = "Kabob- Leaving Outpost 2"
    kabob_waiting_map_state_name = "Kabob- Farm Map Loading"
    kabob_kill_koss_state_name = "Kabob- Killing Koss"
    kabob_waiting_run_state_name = "Kabob- Move to Farm Spot"
    kabob_waiting_kill_state_name = "Kabob- Killing Drakes"
    kabob_looting_state_name = "Kabob- Picking Up Loot"
    kabob_resign_state_name = "Kabob- Resigning"
    kabob_wait_return_state_name = "Kabob- Wait Return"
    kabob_inventory_state_name = "Kabob- Handle Inventory"
    kabob_end_state_name = "Kabob- End Routine"
    kabob_outpost_portal = [(-15022, 8470)] # Used by itself if spawn close to Floodplain portal
    kabob_outpost_pathing = [(-15480, 11138), (-16009, 10219), (-15022, 8470)] # Used when spawn location is near xunlai chest or merchant
    kabob_farm_run_pathing = [(-14512, 8238), (-12469, 9387), (-12243, 10163), (-11893, 10517), (-10317, 11055), (-9595, 11343), (-8922, 11625), (-8501, 11756)]
    kabob_outpost_resign_pathing = [(-15743, 9784)]
    kabob_merchant_position = [(-15082, 11368)]
    kabob_pathing_portal_only_handler_1 = Routines.Movement.PathHandler(kabob_outpost_portal)
    kabob_pathing_portal_only_handler_2 = Routines.Movement.PathHandler(kabob_outpost_portal)
    kabob_pathing_resign_portal_handler = Routines.Movement.PathHandler(kabob_outpost_resign_pathing)
    kabob_pathing_move_to_portal_handler = Routines.Movement.PathHandler(kabob_outpost_pathing)
    kabob_pathing_move_to_kill_handler = Routines.Movement.PathHandler(kabob_farm_run_pathing)
    movement_Handler = Routines.Movement.FollowXY(50)
    
    keep_list = []
    keep_list.extend(Items.Id_Salve_Kit_List)
    keep_list.append(Items.Drake_Flesh)

    kabob_first_after_reset = False
    kabob_wait_to_kill = False
    kabob_ready_to_kill = False
    kabob_killing_staggering_casted = False
    kabob_killing_eremites_casted = False

    player_stuck = False
    player_stuck_hos_count = 0

    kabob_collected = 0
    kabob_required = 0
    minimum_slots = 2
    add_koss_tries = 0
    current_lootable = 0
    current_loot_tries = 0
    blocked_loots = []
    
    kabob_runs = 0
    kabob_success = 0
    kabob_fails = 0
    
    second_timer_elapsed = 1000
    loot_timer_elapsed = 1500

    skillBar = None
    
    pyParty = PyParty.PyParty() 
    kabob_second_timer = Timer() 
    kabob_stuck_timer = Timer()
    kabob_loot_timer = Timer()
    kabob_loot_done_timer = Timer()
    kabob_stay_alive_timer = Timer()

    inventoryRoutine = None   

    current_inventory = []
    stuckPosition = []

    ### --- SETUP --- ###
    def __init__(self, window):
        super().__init__(window)

        self.current_inventory = GetInventoryItemSlots()
        self.inventoryRoutine = InventoryFsm(self.kabob_inventory_routine, Mapping.Rilohn_Refuge, self.kabob_merchant_position, self.current_inventory, self.keep_list, logFunc=self.Log)
        
        self.skillBar = self.Kabob_Skillbar()
        self.Kabob_Routine.AddState(self.kabob_travel_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_travel_state_name, Routines.Transition.TravelToOutpost(Mapping.Rilohn_Refuge)),
                       exit_condition=lambda: Routines.Transition.HasArrivedToOutpost(Mapping.Rilohn_Refuge),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_initial_check_inventory, execute_fn=lambda: self.CheckInventory())
        self.Kabob_Routine.AddState(self.kabob_set_normal_mode,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_set_normal_mode, Party.SetNormalMode()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_add_hero_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_add_hero_state_name, self.PutKossInParty()), # Ensure only one hero in party
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_load_skillbar_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_load_skillbar_state_name, self.LoadSkillBar()), # Ensure only one hero in party                       
                       exit_condition=lambda: self.IsSkillBarLoaded(),
                       transition_delay_ms=1500)
        self.Kabob_Routine.AddState(self.kabob_pathing_1_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_pathing_1_state_name, Routines.Movement.FollowPath(self.kabob_pathing_portal_only_handler_1, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_pathing_portal_only_handler_1, self.movement_Handler) or Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon,
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_resign_pathing_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_resign_pathing_state_name, Routines.Movement.FollowPath(self.kabob_pathing_resign_portal_handler, self.movement_Handler)),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded(), # or Routines.Movement.IsFollowPathFinished(kabob_pathing_resign_portal_handler, movement_Handler) or Map.GetMapID() == Mapping.Rilohn_Refuge,
                       run_once=False)
        self.Kabob_Routine.AddSubroutine(self.kabob_inventory_state_name,
                       sub_fsm = self.inventoryRoutine, # dont add execute function wrapper here
                       condition_fn=lambda: not self.kabob_first_after_reset and Inventory.GetFreeSlotCount() <= self.minimum_slots)        
        self.Kabob_Routine.AddState(self.kabob_check_inventory_after_handle_inventory, execute_fn=lambda: self.CheckInventory())
        self.Kabob_Routine.AddState(self.kabob_pathing_2_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_pathing_2_state_name, Routines.Movement.FollowPath(self.kabob_pathing_portal_only_handler_2, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_pathing_portal_only_handler_2, self.movement_Handler) or Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon,
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_waiting_map_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_waiting_map_state_name, Routines.Transition.IsExplorableLoaded()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_kill_koss_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_kill_koss_state_name, self.KillKoss()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_waiting_run_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_waiting_run_state_name, self.TimeToRunToDrakes()),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_pathing_move_to_kill_handler, self.movement_Handler) or self.CheckSurrounded() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_waiting_kill_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_waiting_kill_state_name, self.KillLoopStart()),
                       exit_condition=lambda: self.KillLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_looting_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_looting_state_name, self.LootLoopStart()),
                       exit_condition=lambda: self.LootLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_resign_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_resign_state_name, Player.SendChatCommand("resign")),
                       exit_condition=lambda: Agent.IsDead(Player.GetAgentID()) or Map.GetMapID() == Mapping.Rilohn_Refuge,
                       transition_delay_ms=3000)
        self.Kabob_Routine.AddState(self.kabob_wait_return_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_wait_return_state_name, Party.ReturnToOutpost()),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded() or self.ShouldForceTransitionStep(),
                       transition_delay_ms=3000)
        self.Kabob_Routine.AddState(self.kabob_end_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_end_state_name, self.CheckKabobRoutineEnd()),
                       transition_delay_ms=1000)
            
    # Start the kabob routine from the first state after soft reset in case player moved around.
    def Start(self):
        if not self.Kabob_Routine.is_started():
            self.SoftReset()
            self.Kabob_Routine.start()
            self.window.StartBot()

    # Stop the kabob routine.
    def Stop(self):
        if self.Kabob_Routine.is_started():
            self.Kabob_Routine.stop()
            self.window.StopBot()

    def PrintData(self):
        if self.current_inventory != None:
            totalSlotsFull = 0
            for (bag, slots) in self.current_inventory:
                if isinstance(slots, list):
                    totalSlotsFull += len(slots)
                    for slot in slots:
                        self.Log(f"Bag: {bag}, Slot: {slot}")
            self.Log(f"Total Slots Full: {totalSlotsFull}")

    def Reset(self):        
        self.Kabob_Routine.reset()
        self.Kabob_Routine.stop()
        
        self.kabob_collected = 0    
        self.kabob_runs = 0
        self.kabob_success = 0
        self.kabob_fails = 0
        self.minimum_slots = 3

        self.kabob_first_after_reset = True 

        self.SoftReset()

        # Get new set of inventory slots to keep around in case player went and did some shit, then came back
        self.current_inventory = GetInventoryItemSlots()
        self.inventoryRoutine = InventoryFsm(self.kabob_inventory_routine, Mapping.Rilohn_Refuge, self.kabob_merchant_position, self.current_inventory, 
                                             self.keep_list,
                                             logFunc=self.Log)
        self.window.ResetBot()

    def SoftReset(self):        
        self.player_stuck = False
        self.kabob_wait_to_kill = False
        self.kabob_ready_to_kill = False
        self.kabob_killing_staggering_casted = False
        self.kabob_killing_eremites_casted = False
        self.step_transition_threshold_timer.Reset()
        
        self.add_koss_tries = 0
        self.player_stuck_hos_count = 0
        self.current_lootable = 0
        self.current_loot_tries = 0
        self.blocked_loots.clear()

        self.inventoryRoutine.Reset()
        
        self.ResetPathing()

    def ResetPathing(self):        
        self.movement_Handler.reset()
        self.kabob_loot_timer.Stop()
        self.kabob_stuck_timer.Stop()
        self.kabob_second_timer.Stop()
        self.kabob_stay_alive_timer.Stop()
        self.kabob_pathing_move_to_kill_handler.reset()
        self.kabob_pathing_resign_portal_handler.reset()
        self.kabob_pathing_portal_only_handler_1.reset()
        self.kabob_pathing_portal_only_handler_2.reset()
        self.kabob_pathing_move_to_portal_handler.reset()

    def IsBotRunning(self):
        return self.Kabob_Routine.is_started() and not self.Kabob_Routine.is_finished()

    def Update(self):
        if self.Kabob_Routine.is_started() and not self.Kabob_Routine.is_finished():
            self.Kabob_Routine.update()

    def Resign(self):
        if self.Kabob_Routine.is_started():
            self.kabob_runs += 1
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_resign_state_name)

    def SuccessResign(self):
        self.Resign()
        self.kabob_success += 1

    def FailResign(self):
        self.Resign()
        self.kabob_fails += 1

    def SetKabobCollectCount(self, numberToCollect):        
        if isinstance(numberToCollect, int):
            self.kabob_required = numberToCollect
        else:
            self.Log("Kabob amount must be integral")

    def CheckSurrounded(self):
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), GameAreas.Lesser_Earshot)
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')

        return len(enemy_array) > 7 or self.player_stuck
    
    def CheckInventory(self):
        if Inventory.GetFreeSlotCount() <= self.minimum_slots:
            self.Log("Bags Full - Manually Handle")
            self.Stop()

    def Log(self, text, msgType=Py4GW.Console.MessageType.Info):
        if self.window:
            self.window.Log(text, msgType)
    ### --- SETUP --- ###

    ### --- ROUTINE FUNCTIONS --- ###
    def LoadSkillBar(self):
        primary_profession, _ = Agent.GetProfessionNames(Player.GetAgentID())

        if primary_profession != "Dervish":
            self.Log("Bot Requires Dervish Primary")
            self.Stop()
        else:
            SkillBar.LoadSkillTemplate(self.Kabob_Skillbar_Code)
            SkillBar.LoadHeroSkillTemplate (1, self.Kabob_Hero_Skillbar_Code)
    
    def IsSkillBarLoaded(self):
        primary_profession, _ = Agent.GetProfessionNames(Player.GetAgentID())
        if primary_profession != "Dervish":        
            self.Log("Bot Requires Dervish Primary", Py4GW.Console.MessageType.Error)
            self.stop()
            return False        
        
        return True

    def PutKossInParty(self):
        self.pyParty.LeaveParty()
        self.pyParty.AddHero(Heroes.Koss)

    def IsKossInParty(self):
        if not IsHeroInParty(Heroes.Koss):
            self.add_koss_tries += 1

        # If Koss not added after ~5 seconds, fail and end kabob farming.
        if self.add_koss_tries >= 5:
            self.Log("Unable to add Koss to Party!")
            self.Kabob_Routine.stop()
            return True
        
        return False
    
    def KillKoss(self):
        agent_id = Player.GetAgentID()
        SkillBar.HeroUseSkill(agent_id, 2, 1)
        SkillBar.HeroUseSkill(agent_id, 3, 1)
        SkillBar.HeroUseSkill(agent_id, 1, 1)
        
        self.pyParty.FlagHero(pyParty.GetHeroAgentID(1), -16749, 5382)

    def TimeToRunToDrakes(self):
        if not self.kabob_second_timer.IsRunning():
            self.kabob_second_timer.Start()

        if not self.kabob_second_timer.HasElapsed(100):
            return
                
        # Start waiting to kill routine. 
        player_id = Player.GetAgentID()

        if Agent.IsDead(player_id):
            self.FailResign()
            return
            
        # Checking whether the player is stuck
        self.HandleStuck()

        # Run the stay alive script.
        self.StayAliveLoop()

        # Try to follow the path based on pathing points and movement handler.
        Routines.Movement.FollowPath(self.kabob_pathing_move_to_kill_handler, self.movement_Handler)
        
        self.kabob_second_timer.Reset()

    def KillLoopStart(self):        
        self.StayAliveLoop()
        self.Kill()

    # Stay alive using all heal buffs and hos if available
    def StayAliveLoop(self):
        if not self.kabob_stay_alive_timer.IsRunning():
            self.kabob_stay_alive_timer.Start()

        if not self.kabob_stay_alive_timer.HasElapsed(1000):
            return
        
        self.kabob_stay_alive_timer.Reset()

        try:            
            # Start waiting to kill routine. 
            player_id = Player.GetAgentID()

            if Agent.IsDead(player_id):
                self.FailResign()
                return
                
            if not CanCast(player_id):
                return
             
            if self.kabob_killing_staggering_casted:
                return

            enemies = AgentArray.GetEnemyArray()
            enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Spellcast)
            enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

            if len(enemies) > 0:
                # Cast stay alive spells if needed.
                maxHp = Agent.GetMaxHealth(player_id)                
                hp = Agent.GetHealth(player_id) * maxHp
                dangerHp = .7 * maxHp
                
                # Cast HOS is available but find enemy behind if able, otherwise just use since need to heal.
                if self.player_stuck or hp < dangerHp:
                    if not IsEnemyBehind(enemies[0]):
                        for enemy in enemies:
                            if IsEnemyBehind(enemy):
                                break

                    if HasEnoughEnergy(self.skillBar.hos) and IsSkillReadyById(self.skillBar.hos):
                        CastSkillById(self.skillBar.hos)

                        if self.player_stuck:
                            self.player_stuck_hos_count += 1

                            if self.player_stuck_hos_count > 2:
                                # kill shit then if not already
                                self.kabob_ready_to_kill = True
                                self.Kabob_Routine.jump_to_state_by_name(self.kabob_waiting_kill_state_name)
                                
                                return
                        return
                    
                regen_time_remain = 0
                intimidate_time_remain = 0
                sanctity_time_remain = 0 
                                    
                player_buffs = Effects.GetEffects(player_id)

                for buff in player_buffs:
                    if buff.skill_id == self.skillBar.regen:
                        regen_time_remain = buff.time_remaining
                    if buff.skill_id == self.skillBar.intimidating:
                        intimidate_time_remain = buff.time_remaining
                    if buff.skill_id == self.skillBar.sanctity:
                        sanctity_time_remain = buff.time_remaining                    

                if regen_time_remain < 3000 and HasEnoughEnergy(self.skillBar.regen) and IsSkillReadyById(self.skillBar.regen):
                    CastSkillById(self.skillBar.regen)
                    return
                
                hasShards = HasBuff(player_id, self.skillBar.sand_shards)

                if not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                    CastSkillById(self.skillBar.sand_shards)
                    return
                                 
                # Only cast these when waiting for the killing to start.
                if self.Kabob_Routine.get_current_step_name() == self.kabob_waiting_kill_state_name or hp < dangerHp:
                    if intimidate_time_remain < 3000 and HasEnoughEnergy(self.skillBar.intimidating) and IsSkillReadyById(self.skillBar.intimidating):
                        CastSkillById(self.skillBar.intimidating)
                        return

                    if sanctity_time_remain < 3000 and HasEnoughEnergy(self.skillBar.sanctity) and IsSkillReadyById(self.skillBar.sanctity):
                        CastSkillById(self.skillBar.sanctity)
        except exception as e:
            Py4GW.Console.Log("StayAlive", str(e), Py4GW.Console.MessageType.Error)
            self.Log("Error Staying Alive.", Py4GW.Console.MessageType.Error)

    def Kill(self):
        if not self.kabob_second_timer.IsRunning():
            self.kabob_second_timer.Start()

        if not self.kabob_second_timer.HasElapsed(1000):
            return
        
        self.kabob_second_timer.Reset()

        try:  
            # Start waiting to kill routine. 
            player_id = Player.GetAgentID()
            
            if Agent.IsDead(player_id):
                self.FailResign()
                return
                        
            if not CanCast(player_id):
                return              

            if (Map.IsMapReady() and not Map.IsMapLoading()):
                if (Map.IsExplorable() and Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon and Party.IsPartyLoaded()):
                    enemies = AgentArray.GetEnemyArray()
                    enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Area)
                    enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

                    if len(enemies) == 0:
                        return
                                                            
                    if not self.kabob_ready_to_kill:
                        if len(enemies) < 7 and not self.player_stuck:
                            return
                        
                        self.kabob_ready_to_kill = True

                        if not IsEnemyBehind(enemies[0]):
                            for enemy in enemies:
                                if IsEnemyBehind(enemy):
                                    break

                        if HasEnoughEnergy(self.skillBar.hos) and IsSkillReadyById(self.skillBar.hos):
                            CastSkillById(self.skillBar.hos)
                            return
                    
                    target = Player.GetTargetID()

                    if target not in enemies:
                        target = enemies[0]

                    Player.ChangeTarget(target)
                        
                    if self.kabob_killing_staggering_casted and IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):  
                        self.kabob_killing_staggering_casted = False
                        # self.Log("eremites")
                        CastSkillById(self.skillBar.eremites)
                        return                    
                    
                    vos_time_remain = 0

                    # Cast stay alive spells if needed.      
                    player_buffs = Effects.GetEffects(player_id)
                    
                    for buff in player_buffs:
                        if buff.skill_id == self.skillBar.vos:
                            vos_time_remain = buff.time_remaining
                                                
                    hasShards = HasBuff(player_id, self.skillBar.sand_shards)

                    if not self.kabob_killing_staggering_casted and not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                        # self.Log("shards")
                        CastSkillById(self.skillBar.sand_shards)
                        return
                                            
                    # Get Ready for killing
                    # Need find a way to change weapon set.
                    # For now assume we're good to go.
                    if not self.kabob_killing_staggering_casted and vos_time_remain < 3000 and IsSkillReadyById(self.skillBar.vos) and HasEnoughEnergy(self.skillBar.vos):                        
                        # self.Log("vos")
                        CastSkillById(self.skillBar.vos)
                        return
                        
                    if IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):
                        if IsSkillReadyById(self.skillBar.staggering) and HasEnoughEnergy(self.skillBar.staggering):
                            self.kabob_killing_staggering_casted = True
                            # self.Log("stagger")
                            CastSkillById(self.skillBar.staggering)
                    elif not Agent.IsAttacking(player_id) and not Agent.IsCasting(player_id):
                        # Normal Attack
                        #self.Log("attack")
                        Player.Interact(target)
        except exception as e:
            Py4GW.Console.Log("Kill Loop Error", "Kill Loop Error {e}", Py4GW.Console.MessageType.Error)

    def KillLoopComplete(self):
        try:
            if Agent.IsDead(Player.GetAgentID()):
                self.FailResign()
                return False
        
            enemies = AgentArray.GetEnemyArray()
            enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Lesser_Earshot)
            enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

            if len(enemies) == 0:
                return True

            return False
        except:
            self.Log("Kill Loop Error", Py4GW.Console.MessageType.Error)

    def LootLoopStart(self):
        try:
            if not self.kabob_loot_timer.IsRunning():
                self.kabob_loot_timer.Start()

            if self.kabob_loot_timer.HasElapsed(self.loot_timer_elapsed):                
                self.kabob_loot_timer.Reset()
                
                item = self.GetNearestPickupItem()

                if item == 0 or item == None:
                    self.current_lootable = 0
                    return

                if self.current_lootable != item:
                    self.current_lootable = item
                # else:
                self.current_loot_tries += 1

                if self.current_loot_tries > 120:
                    self.Log("Loot- 1000 meters away? Frig it.")
                    self.SuccessResign()
                    return                

                # if self.current_lootable == None:
                #     return
                
                target = Player.GetTargetID()

                if target != self.current_lootable and self.current_lootable != 0:
                    Player.ChangeTarget(self.current_lootable)
                    #return

                model = Item.GetModelID(Agent.GetItemAgent(self.current_lootable).item_id)

                if model == Items.Drake_Flesh:
                    self.kabob_collected += 1

                Keystroke.PressAndRelease(Key.Space.value)
        except exception as e:
            Py4GW.Console.Log("Loot Loop", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)

    def LootLoopComplete(self):
        try:
            if not self.kabob_loot_done_timer.IsRunning():
                self.kabob_loot_done_timer.Start()

            if self.kabob_loot_done_timer.HasElapsed(self.loot_timer_elapsed):
                self.kabob_loot_done_timer.Reset()

                item = self.GetNearestPickupItem()        

                if item == 0 or item == None or Inventory.GetFreeSlotCount() == 0:
                    self.kabob_runs += 1
                    self.kabob_success += 1
                    return True

            return False
        except exception as e:
            Py4GW.Console.Log("Loot Loop Complete", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)
    
    def GetKabobLootableItems(self):
        try:
            # Get all items in the area
            item_array = AgentArray.GetItemArray()
            
            filtered_items = []

            for item in item_array:
                agent = Agent.GetItemAgent(item)
                combo = (agent.agent_id, agent.item_id)
                filtered_items.append(combo)
            
            return filtered_items
            '''
            # Get the agent IDs corresponding to the filtered item IDs
            filtered_agent_ids = [
                agent_id for agent_id, item_id in agent_to_item_map.items()
                if item_id in filtered_items
            ]

            # Map agent IDs to item data
            #agent_to_item_map = [agent for Agent.GetItemAgent(agent).agent_id in item_array]

            # Extract all item IDs for filtering
            #filtered_items = agent_to_item_map

            # Apply filters based on loot preferences        
            #banned_models = {}
            #filtered_items = ItemArray.Filter.ByCondition(list(agent_to_item_map.values()), lambda item_id: Item.GetModelID(item_id) not in banned_models)

            if not bot_vars.config_vars.loot_event_items:
                banned_models = {28435,28436}
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.GetModelID(item_id) not in banned_models)
            if not bot_vars.config_vars.loot_charr_battle_plans:
                banned_models = {24629, 24630, 24631, 24632}
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.GetModelID(item_id) not in banned_models)
            if not bot_vars.config_vars.loot_glacial_stones:
                banned_models = {27047}
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.GetModelID(item_id) not in banned_models)
            if not bot_vars.config_vars.loot_dyes:
                banned_models = {146}
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.GetModelID(item_id) not in banned_models)
            if not bot_vars.config_vars.loot_tomes:
                banned_models = {21797}
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.GetModelID(item_id) not in banned_models)
            if not bot_vars.config_vars.loot_whites:
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.Rarity.IsWhite(item_id) == False)
            if not bot_vars.config_vars.loot_blues:
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.Rarity.IsBlue(item_id) == False)
            if not bot_vars.config_vars.loot_purples:
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.Rarity.IsPurple(item_id) == False)
            if not bot_vars.config_vars.loot_golds:
                filtered_items = ItemArray.Filter.ByCondition(filtered_items, lambda item_id: Item.Rarity.IsGold(item_id) == False) """

            # Get the agent IDs corresponding to the filtered item IDs
            #filtered_agent_ids = [
            #    agent_id for agent_id, item_id in agent_to_item_map.items()
            #    if item_id in filtered_items
            #]

            #return filtered_items'''
        
            return filtered_agent_ids
        except Exception as e:
            current_function = inspect.currentframe().f_code.co_name
            Py4GW.Console.Log(bot_name, f"Error in {current_function}: {str(e)}", Py4GW.Console.MessageType.Error)    

    def GetKabobCollected(self):
        return self.kabob_collected

    def GetKabobStats(self):
        return (self.kabob_runs, self.kabob_success)
    
    # Jump back to output pathing if not done collecting
    def CheckKabobRoutineEnd(self):
        # Don't reset the kabob count
        self.SoftReset()

        if self.kabob_first_after_reset:
            self.kabob_first_after_reset = False

        if self.kabob_collected < self.kabob_required:

            # mapping to outpost may have failed OR the threshold was reached. Try to map there and start over.
            if Map.GetMapID() != Mapping.Rilohn_Refuge:
                self.Kabob_Routine.jump_to_state_by_name(self.kabob_travel_state_name)
            else:
                # already at outpost, check slot count, handle inv or continue farm
                if Inventory.GetFreeSlotCount() <= self.minimum_slots:
                    self.Kabob_Routine.jump_to_state_by_name(self.kabob_inventory_state_name)
                else:
                    self.Kabob_Routine.jump_to_state_by_name(self.kabob_pathing_2_state_name)
        else:
            self.Log("Kabob Count Matched - AutoStop")
            self.Stop()
    
    def HandleStuck(self):  
        if (Map.IsExplorable() and Party.IsPartyLoaded()):
            if not self.kabob_stuck_timer.IsRunning():
                self.kabob_stuck_timer.Start()

            currentStep = self.Kabob_Routine.get_current_step_name()

            playerId = Player.GetAgentID()
            localPosition = Player.GetXY()

            if currentStep == self.kabob_waiting_run_state_name and self.stuckPosition:                
                if not Agent.IsCasting(playerId) and not Agent.IsKnockedDown(playerId) and not Agent.IsMoving(playerId) or (abs(localPosition[0] - self.stuckPosition[0]) <= 20 and abs(localPosition[1] - self.stuckPosition[1]) <= 20):
                    if self.kabob_stuck_timer.HasElapsed(4000):
                        self.player_stuck = True
                        self.kabob_stuck_timer.Reset()
                else:                    
                    self.kabob_stuck_timer.Stop()
                    self.player_stuck = False

            self.stuckPosition = localPosition
            # if not Agent.IsMoving(Player.GetAgentID()) and currentStep != self.kabob_waiting_kill_state_name and currentStep != self.kabob_looting_state_name:
            #     if self.kabob_stuck_timer.HasElapsed(3000):
            #         self.player_stuck = True
            #         self.kabob_stuck_timer.Reset()
            # else:
            #     self.kabob_stuck_timer.Stop()
            #     self.player_stuck = False
        else:
            self.kabob_stuck_timer.Stop()
            self.kabob_stuck_timer.Reset()
            self.player_stuck = False
  ### --- ROUTINE FUNCTIONS --- ###
  #   

def GetKabobCollected():
    return bot_routine.GetKabobCollected()

def GetKabobData():
    return bot_routine.GetKabobStats()

main_window = Kabob_Window(bot_name)
bot_routine = Kabob_Farm(main_window)

def StartBot():
    bot_routine.SetKabobCollectCount(kabob_input)
    bot_routine.Start()

def StopBot():
    if bot_routine.IsBotRunning():
        bot_routine.Stop()

def ResetBot():
    # Stop the main state machine  
    bot_routine.Stop()
    bot_routine.Reset()

def PrintData():
    bot_routine.PrintData()

### --- MAIN --- ###
def main():
    try:
        if main_window:
            main_window.Show()

        if Party.IsPartyLoaded():
            if bot_routine and bot_routine.IsBotRunning():
                bot_routine.Update()
                
    except ImportError as e:
        Py4GW.Console.Log(bot_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(bot_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(bot_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(bot_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == "__main__":
    main()

### -- MAIN -- ###