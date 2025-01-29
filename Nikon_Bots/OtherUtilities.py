
def IsChestInRange(max_distance=2500):
    return Routines.Targeting.GetNearestChest(max_distance) != 0


# Ensure only selected hero is in party
def EnsureOnlyHeroInParty(hero_id):
    # Ensure the hero id is in deed a hero.
    if not Heroes.Exists(hero_id):
        return
    
    # Check if Koss already in party
    if pyParty.party_hero_count > 1 or not IsHeroInParty(hero_id):
        pyParty.LeaveParty()

    pyParty.AddHero(hero_id)  



    @staticmethod
    def AcceptUnclaimedItems():
        """
            This function will attempt to move all items from the unclaimed items bag (7) to the player bags.            
            @returns bool, list(items) -> true/false for success, list of items claimed.
        """
        try:
            unclaimed = ItemArray.CreateBagList(7)            
            unclaimed_bag = PyInventory.Bag(unclaimed[0].value, unclaimed[0].name)            
            unclaimed_count = unclaimed_bag.GetSize()
            
            if unclaimed_count == 0:
                return True
                
            unclaimed_items = unclaimed_bag.GetItems()
            
            freeSlots = list()
            
            
            # Go through each unclaimed item.
            for unclaimed_item in unclaimed_items: 
                # now get player bags and see if there is a slot matching the item AND has space.                
                invBags = ItemArray.CreateBagList(1,2,3,4)
                
                for _, bag in enumerate(invBags):
                    bag_instance = PyInventory.Bag(bag.value, bag.name)
                    
                    freeSlots = Inventory.GetFreeSlotList(bag.value)
                    
                    if freeSlots == None:
                        Py4GW.Console.Log("AcceptUnclaimedItems", f"Slots == None for bag {bag.name}")
                        continue
                        
                    if len(freeSlots) == 0:
                        Py4GW.Console.Log("AcceptUnclaimedItems", f"Zero slots in bag {bag.name}")
                        continue                    

                    Py4GW.Console.Log("AcceptUnclaimedItems", f"{bag.name} has {len(freeSlots)} free.")                
                    invItems = bag_instance.GetItems()    
                               
                    match = False
                    
                    # Now check every inventory item for the match.
                    for invItem in invItems:
                        Py4GW.Console.Log("AcceptUnclaimedItems", f"Item stackable {unclaimed_item.is_stackable}, id {unclaimed_item.model_id} - inv {invItem.model_id}, quant {unclaimed_item.quantity}, invQ {invItem.quantity}")
                        # if stackable, see if inventory has a stack with space for the unclaimed stack
                        if invItem.model_id == unclaimed_item.model_id and invItem.quantity <= (250 - unclaimed_item.quantity):                        
                            Py4GW.Console.Log("AcceptUnclaimedItems", f"Found in bag, moving item to bag {bag.value} slot {invItem.slot}")
                            Inventory.MoveItem(unclaimed_item.item_id, bag.value, invItem.slot, unclaimed_item.quantity)
                            match = True
                            break
                            
                    # no match, put in first free slot.    
                    if not match:
                        if len(freeSlots) > 0:
                            Py4GW.Console.Log("AcceptUnclaimedItems", f"moving item to bag {bag.value} slot {freeSlots[0]}")
                            Inventory.MoveItem(unclaimed_item.item_id, bag.value, freeSlots[0], unclaimed_item.quantity)
                            freeSlots.remove(freeSlots[0])
                                
            return True
        
        except Exception as e:
            Py4GW.Console.Log(
                "AcceptUnclaimedItems",
                f"Error during accept unclaimed items {e}."
            )
            
        Py4GW.Console.Log(
            "AcceptUnclaimedItems",
            f"No free slots available to accept unclaimed items."
        )
        return False  # Unable to accept unclaimed items

    @staticmethod
    def GetFreeSlotList(bagNum):
        """
            This function will attempt to get all available slots from the specified bag.           
            @returns list(int) --> list of free slots for the bag.
        """
        bagList = ItemArray.CreateBagList(bagNum)   
        bag = PyInventory.Bag(bagList[0].value, bagList[0].name)
        
        count = bag.GetSize()
        items = bag.GetItems()
        
        if count == 0:
            return 0
            
        slots = []
        
        for slot in range(count):
            slots.append(slot)
            
        for item in items:
            slots.remove(Item.GetSlot(item.item_id))

        return slots
    
    @staticmethod    
    def BagContainsItem(bagNum, modelId):
        try:
            bag = ItemArray.CreateBagList(bagNum)            
            bag_bag = PyInventory.Bag(bag[0].value, bag[0].name)
            
            if bag_bag.GetSize() == 0:
                return True
                
            bag_items = bag_bag.GetItems()
            
            for item in bag_items:
                if item.model_id == modelId:
                    return True
        except:
            Py4GW.Console.Log("BagContainsItem", f"Error checking if bag has item: {modelId}")
                    
        return False
