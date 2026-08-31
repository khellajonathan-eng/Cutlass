import random, sys, time, ast, os, pickle
from copy import deepcopy
v1 = "Fixed a few bugs" #x.x.x.V
v2 = "Made into variable accessible for when player.mlocation is None, which accepts a tuple (map, room)" #x.x.V.x
v3 = "Added Save/Load system." #x.V.x.x
v4 = "Now in beta testing."#V.x.x.x
vs = [v1, v2, v3, v4][::-1]
class UNIFile:
    @staticmethod
    def getfile():
        return __file__ if "__file__" in globals() else sys.argv[0]
#created by airbreather5277 aka mynameisajoke
#ps: this is my first time dealing with generation, so if you dont like the code then screw you
class Panic(Exception):
    pass
#purely for scope ensurement, but now that i made it, it could have some other uses too
class EVMeta(type):
    def __setattr__(cls, name, value):
        print(name, value)
        if name.startswith("on"):
            if not callable(value):
                print("Error 31: Must set an event to a callable function")
                sourcefile = UNIFile.getfile()
                with open(sourcefile, "r") as f:
                    lines = f.read().splitlines()
                    for i, l in enumerate(lines, 1):
                        if "Error 31: Must set an event to a callable function" in l:
                            lineno = i
                            break
                    else:
                        lineno = "unknown"
                print(lineno)
                EventHook.onanyerror(error=0, reason="Must set an event to a callable function", ofkind="normal", line=lineno)
                return
        super().__setattr__(name, value)
class EventHook(metaclass=EVMeta):
    @staticmethod
    def key():
        print("on (to show something is happening) obj (the object which the event is attatched to) action (what happens in order to trigger the event). if obj is any, then it means it belongs to no one subject.")
        vars = []
        funcs = []
        for k, v in EventHook.__dict__.items():
            if k.startswith("on") and callable(v):
                vars.append(k)
                funcs.append(v)
        return dict(zip(vars, funcs))
    @staticmethod
    def defaultfunc(*args, **kwargs):
        pass
    onmapenter = defaultfunc#done
    onmapchange = defaultfunc#done
    onroomkill = defaultfunc#done
    onroommove = defaultfunc#done
    onmapkill = defaultfunc#done
    onitemget = defaultfunc#done
    oncreditsget = defaultfunc#done
    oneventtriggered = defaultfunc#done
    onmapcreate = defaultfunc#done
    onroomcreate = defaultfunc#done
    onmapgenerated = defaultfunc#done
    onanyerror = defaultfunc#done
    onanywarning = defaultfunc
    onitemuse = defaultfunc#done
    oneventadd = defaultfunc#done
    onmodload = defaultfunc#done
    onroomleft = defaultfunc#done
    onmapcleanup = defaultfunc#done
class Error:
    @staticmethod
    def error(msg, errtype="normal", killsys=False, sourcefile=None, finderror=False, debug=False):
        #killsys just kills the system
        #wanted to call it something like slam down the hammer but then i realized could be a bit confusing so no :(
        if finderror:
            lineno = "unknown"
            lineerror = ""
            if sourcefile is None:
                sourcefile = UNIFile.getfile()
            with open(sourcefile, "r") as f:
                source = f.read().splitlines()
                if debug:
                    print(UNIFile.getfile())
            for i, l in enumerate(source):
                if msg in l:
                    lineno = i + 1
                    lineerror = l
        else:
            lineno = ""
        if finderror:
            print(f"\033[91m{lineerror}\033[0m")
        try:
            if ":" not in msg:
                raise Panic("Error message must have a colon for seperation of error and message!")
            errornum = msg.split(":")[0].split(" ")[-1]
            fixed = []
            for char in errornum:
                if char.isdigit():
                    fixed.append(char)
            if not fixed:
                raise Panic("Error number must be a number!")
            message = msg.split(":", 1)[-1]
            EventHook.onanyerror(error=errornum, reason=message, ofkind=errtype, line=lineno)
        except Exception as e:
            print(f"Error 7: While handling an error, another error occured: {e}")
            return
        finally:
            if not killsys:
                print((f"\033[32m{errtype} " if errtype != "normal" else "") + ("\033[31m" if killsys else "") + f"{msg}\033[0m", (f"\033[96merror at {lineno}\033[0m" if finderror else ""))
            else:
                if errtype != "normal":
                    exerror = type(f"{errtype} Error {errornum}", (Panic,), {"reason": message, "number": errornum, "kind": errtype})
                    raise exerror(message.strip())
                else:
                    exerror = type(f"Error {errornum}", (Panic,), {"reason": message, "number": errornum, "kind": errtype})
                    raise exerror(message.strip())
    @staticmethod
    def warn(warning):
        try:
            w = warning.split(":", 1)[1].strip()
            n = warning.split(":")[0]
            if "W" not in n:
                raise Panic("W must be in the warning number to show it is a warning!")
            n = n.strip("W")
            if n == "":
                raise Panic("Warning number must have a number!")
            EventHook.onanywarning(number=n, message=w)
        except Exception as e:
            Error.error(f"Error 36: {e}", errtype="Unknown")
            return
        finally:
            print(warning)
class Player:
    def __init__(self, name):
        self.inventory = []
        self.credits = 0
        self.name = name
        self.roomscrossed = []
        self.numroomscrossed = 0
        self.rlocation = None
        self.mlocation = None
    def changemaps(self):
        EventHook.onmapchange(frommap=self.mlocation)
        self.mlocation = None
        self.rlocation = None
    def has(self, item):
        if isinstance(item, str):
            if item in self.inventory:
                return True
            else:
                return False
        elif isinstance(item, int):
            if self.credits >= item:
                return True
            else:
                return False
        else:
            return None
    def give(self, item):
        if isinstance(item, str):
            self.inventory.append(item)
            EventHook.onitemget(given=item)
        elif isinstance(item, int):
            self.credits += item
            EventHook.oncreditsget(given=item)
        else:
            Error.error("Error 19: Item must be a string (for adding to the inventory) or an integer (for adding credits).")
player = Player("Bob")
class Map:
    showattrs = True
    mapsnames = {}
    maps = []
    def __init__(self, name):
        self.name = name
        self.lor = [] #short for list of rooms
        self.active = True
        Map.mapsnames[self.name] = self
        Map.maps.append(self)
        EventHook.onmapcreate(n=name)
    def  __getattr__(self, name):
        if name.endswith("_check"):
            rname = name.replace("_check", "")
            try:
                object.__getattribute__(self, rname)
                exists = True
            except AttributeError:
                exists = False
            def runcheck(*args, **kwargs):
                if exists:
                    if Map.showattrs:
                        print(rname, "exists!")
                        return True
                    else:
                        return True
                else:
                    if Map.showattrs:
                        print(rname, "does not exist!")
                        return False
                    else:
                        return False
            return runcheck
        raise AttributeError(name)
    def __getattribute__(self, name):
        if name in ["active", "name"]:
            return object.__getattribute__(self, name)
        if name.startswith("__") and name.endswith("__"):
            return object.__getattribute__(self, name)
        if not object.__getattribute__(self, "active"):
            n = object.__getattribute__(self, "name")
            def denied(*args, **kwargs):
                Error.error(f"Error 15: {n} is offline.\033[0m")
                return f"\033[31mFatal Error 15: {n} is offline.\033[0m"
            return denied
        return object.__getattribute__(self, name)
    class Room:
        roomsnames = {}
        rooms = []
        def __init__(self, name, *outs, hide=False, need=None, loots=None, merchant=False, trulyhidden=False, besoin=None):
            if need is None:
                need = []
            if loots is None:
                loots = []
            if besoin is None:
                besoin = []
            object.__setattr__(self, "eventcds", {})
            object.__setattr__(self, "events", {})
            object.__setattr__(self, "allhidden", trulyhidden)
            self.merchant = merchant
            object.__setattr__(self, "need", need)
            object.__setattr__(self, "besoin", besoin)
            object.__setattr__(self, "loot", loots)
            self.hide = hide
            self.name = name
            object.__setattr__(self, "out", outs)
            self.active = True
            Map.Room.roomsnames[self.name] = self
            Map.Room.rooms.append(self)
            object.__setattr__(self, "gridcoords", ())
            object.__setattr__(self, "neighbors", [])
        def __getattr__(self, name):
            if name.endswith("_check"):
                rname = name.replace("_check", "")
                try:
                    object.__getattribute__(self, rname)
                    exists = True
                except AttributeError:
                    exists = False
                def runcheck(*args, **kwargs):
                    if exists:
                        if Map.showattrs:
                            print(rname, "exists!")
                            return True
                        else:
                            return True
                    else:
                        if Map.showattrs:
                            print(rname, "does not exist!")
                            return False
                        else:
                            return False
                return runcheck
            raise AttributeError(name)
        def __getattribute__(self, name):
            attr = object.__getattribute__(self, name)
            if name.startswith("__") and name.endswith("__"):
                return attr
            try:
                active = object.__getattribute__(self, "active")
            except AttributeError:
                return attr
            if not active:
                n = object.__getattribute__(self, "name")
                def deniedr(*args, **kwargs):
                    Error.error(f"Error 15: {n} is offline.\033[0m", "Fatal")
                    return f"\033[31mFatal Error 15: {n} is offline.\033[0m"
                return deniedr
            return attr
        @classmethod
        def createroom(cls, name, *outs, hide=False, addloot=None, req=None, merchant=False, bes=None, pasvoir=False):
            o = []
            if addloot is None:
                addloot = []
            if req is None:
                req = []
            if bes is None:
                bes = []
            for ou in outs:
                if isinstance(ou, list):
                    for oo in ou:
                        o.append(oo)
                else:
                    o.append(ou)
            EventHook.onroomcreate(n=name, exits=outs, ishidden=hide, lootgiven=addloot, reqs=req, ismerchant=merchant, hidereqs=bes, invis=pasvoir)
            return cls(name, *o, hide=hide, loots=addloot, need=req, merchant=merchant, besoin=bes, trulyhidden=pasvoir)
        @classmethod
        def diffroom(cls, *, default=False, into=None, show=True):
            a = True
            for r in Map.Room.rooms:
                if r.allhidden:
                    if not all([True if n in player.inventory else False for n in r.besoin]):
                        r.allhidden = True
                    else:
                        r.allhidden = False
            #the two if trues are just me being lazy so i dont need to indent it all over again
            if True:
                if True:
                    def runevents(r):
                        if not r.events:
                            return
                        for e in dict(r.events):
                            if r.events[e] == "N":
                                e()
                                r.events.pop(e)#n is the default value which means no modifications.
                                EventHook.oneventtriggered(event=e)
                            else:
                                cp = r.events[e] #stands for custom parameters for modification
                                if cp:
                                    chancepointer = [c for c in cp if c.startswith("chance:")]
                                    chance = float(chancepointer[0].split(": ")[1].strip()) if chancepointer else 1.0
                                    stay = True if "stay" in cp else False
                                    delaypointer = [c for c in cp if c.startswith("delay:")]
                                    delay = float(delaypointer[0].split(": ")[1].strip()) if delaypointer else 0
                                    tpointer = [c for c in cp if c.startswith("tpto:")]
                                    tp = Map.Room.roomsnames[tpointer[0].split(":", 1)[1].strip()] if tpointer and player.rlocation in player.mlocation.lor else player.rlocation
                                    needspointer = [c for c in cp if c.startswith("besoins")]
                                    lbesoins = needspointer[0].split(":", 1)[1].strip() if needspointer else []
                                    cd = r.eventcds[r][0]
                                    if lbesoins:
                                        lbesoins = lbesoins.split(", ")
                                    if random.random() < chance:
                                        if all([True if l in player.inventory else False for l in lbesoins]):
                                            if cd <= 0:
                                                player.rlocation = tp
                                                time.sleep(delay)
                                                try:
                                                    e()
                                                    r.eventcds[r][0] = r.eventcds[r][1] 
                                                    if not stay:
                                                        r.events.pop(e)
                                                    EventHook.oneventtriggered(event=e)
                                                except Exception as ex:
                                                    Error.error("Error in runevents() of the diffroom function when trying to execute the events. Error:" + str(ex), "Unknown")
                                            else:
                                                r.eventcds[r][0] -= 1
            if player.mlocation is None:
                if not Map.maps:
                    if show:
                    	Error.error("Error 5: No maps detected")
                    else:
                    	return 5
                    return
                if not Map.Room.rooms:
                    if show:
                    	Error.error("Error 6: No rooms detected")
                    else:
                    	return 6
                    return
                if default:
                	player.mlocation = Map.maps[0]
                	player.rlocation = Map.maps[0].lor[0]
                	return
                player.rlocation = None
                mapss = [map.name for map in Map.maps]
                if not isinstance(into, tuple):
                    ans = input(f"{", ".join(mapss)} \nWhich map would you like to enter? (case-sensitive)\n")
                else:
                    ans = into[0]
                for m in mapss:
                    if m == ans:
                        EventHook.onmapenter(to=m)
                        player.mlocation = Map.mapsnames[m]
                        if not isinstance(into, tuple):
                            roomss = [str(r.name) if not isinstance(r, Map.Room) else str(r.name) for r in player.mlocation.lor]
                            roomss = [r if not Map.Room.roomsnames[r].hide else "" for r in roomss]
                            roomss = [r for r in roomss if r != ""]
                            roomss = [r for r in roomss if not Map.Room.roomsnames[r].allhidden]
                            ans = input(f"{", ".join(roomss)} \nWhich room would you like to enter? (case-sensitive)\n")
                        else:
                            ans = into[1]
                        for r in roomss:
                            access = None
                            if r == ans:
                                if Map.Room.roomsnames[r].need:
                                    for n in Map.Room.roomsnames[r].need:
                                        if n not in player.inventory:
                                            access = False
                                            if isinstance(n, int):
                                                if player.credits >= n:
                                                    access = True
                                                    player.credits -= n
                                                    EventHook.onitemuse(used=n)
                                            if access == False:
                                                break
                                        else:
                                            access = True
                                            EventHook.onitemuse(used=n)
                                            player.inventory.remove(n)
                                if access == False:
                                    if show:
                                        print("Access rejected!")
                                    break
                                if Map.Room.roomsnames[r].loot[:]:
                                    if Map.Room.roomsnames[r].merchant:
                                        print("Would you like to see my wares?")
                                        print("\n---".join(Map.Room.roomsnames[r].loot))
                                        ans = input(">")
                                        for l in Map.Room.roomsnames[r].loot:
                                            if ans == l:
                                                EventHook.onitemget(given=l)
                                                player.inventory.append(Map.Room.roomsnames[r].loot.pop(Map.Room.roomsnames[r].loot.index(l)))
                                    if not Map.Room.roomsnames[r].merchant:
                                        for l in Map.Room.roomsnames[r].loot[:]:
                                            if isinstance(l, int):
                                                if show:
                                                    print("You got", l, "credits!")
                                                player.credits += l
                                                EventHook.oncreditsget(given=l)
                                            else:
                                                player.inventory.append(Map.Room.roomsnames[r].loot.pop(0))
                                                if show:
                                                    print("Acquired", l)
                                                EventHook.onitemget(given=l)
                                player.rlocation = Map.Room.roomsnames[r]
                                EventHook.onroommove(to=player.rlocation)
                                runevents(player.rlocation)
                        if player.rlocation is None:
                            Error.error("\033[31mFatal Error 404: nonexistent room detected. restart the script.\033[0m", killsys=True)
                return
            elif player.mlocation is not None and player.rlocation is None:
                roomss = [r.name for r in player.mlocation.lor]
                roomss = [r for r in roomss if not Map.Room.roomsnames[r].allhidden]
                if into is not None:
                    ans = input(f"{", ".join(roomss)} \nWhich room would you like to enter? (case-sensitive)\n")
                else:
                    ans = into
                for r in roomss:
                    if r == ans:
                        if Map.Room.roomsnames[r].need:
                            for n in Map.Room.roomsnames[r].need:
                                if n not in player.inventory:
                                    access = False
                                    if isinstance(n, int):
                                        if player.credits >= n:
                                            access = True
                                            player.credits -= n
                                            EventHook.onitemuse(used=n)
                                    break
                                else:
                                    EventHook.onitemuse(used=n)
                                    player.inventory.remove(n)
                                    access = True
                        if not access:
                            if show:
                                print("Access rejected!")
                            break
                        if Map.Room.roomsnames[r].loot[:]:
                            if Map.Room.roomsnames[r].loot[:]:
                                    if Map.Room.roomsnames[r].merchant:
                                        print("Would you like to see my wares?")
                                        print("\n---".join(Map.Room.roomsnames[r].loot))
                                        ans = input(">")
                                        for l in Map.Room.roomsnames[r].loot:
                                            if ans == l:
                                                player.inventory.append(Map.Room.roomsnames[r].loot.pop(Map.Room.roomsnames[r].loot.index(l)))
                            if not Map.Room.roomsnames[r].merchant:
                                for l in Map.Room.roomsnames[r].loot:
                                    if isinstance(l, int):
                                        player.credits += l
                                        if show:
                                            print("You got", l, "credits!")
                                    else:
                                        if show:
                                            print("Acquired", l)
                                        player.inventory.append(Map.Room.roomsnames[r].loot.pop(0))
                            EventHook.onroomleft(left=player.rlocation)
                            player.rlocation = Map.Room.roomsnames[r]
                            EventHook.onroommove(to=player.rlocation)
                            runevents(player.rlocation)
                return
            else:
                access = None
                if into == None:
                	print("Where is your destination?")
                	li = [str(o) if not isinstance(o, Map.Room) else str(o.name) for o in player.rlocation.out]
                	li = [ll for ll in li if not isinstance(ll, bool)]
                	li = [ll for ll in li if not Map.Room.roomsnames[ll].allhidden]
                	ans = input(f"{", ".join(li)} (case-sensitive)\n")
                else:
                	ans = into
                for r in Map.Room.rooms:
                    if ans == r.name and r.name in player.rlocation.out:
                        old = player.rlocation.name
                        player.rlocation = r
                        if player.rlocation.need:
                            for n in player.rlocation.need:
                                if n not in player.inventory:
                                    access = False
                                    if isinstance(n, int):
                                        if player.credits >= n:
                                            access = True
                                            player.credits -= n
                                            EventHook.onitemuse(used=n)
                                else:
                                    EventHook.onitemuse(used=n)
                                    player.inventory.remove(n)
                                    access = True
                        if access == False:
                            if show:
                                print("Access rejected!")
                            player.rlocation = Map.Room.roomsnames[old]
                            break
                        runevents(player.rlocation)
                        if player.rlocation.loot:
                            if player.rlocation.loot: #probably some wierd duplicate glitch, cant be bothered to remove it though since it does no harm
                                if player.rlocation.merchant:
                                    print("Would you like to see my wares?")
                                    print("\n---".join(player.rlocation.loot))
                                    ans = input(">")
                                    for l in player.rlocation.loot:
                                        if ans == l:
                                            player.inventory.append(player.rlocation.loot.pop(player.rlocation.loot.index(l)))
                            if not player.rlocation.merchant:
                                for l in player.rlocation.loot[:]:
                                    if isinstance(l, int):
                                        player.credits += l
                                        if show:
                                            print("You got", l, "credits!")
                                    else:
                                        player.inventory.append(player.rlocation.loot.pop(0))
                                        if show:
                                            print("Acquired", l)
                        player.roomscrossed.append(r.name)
                        player.numroomscrossed += 1
                        EventHook.onroommove(to=player.rlocation)
                        EventHook.onroomleft(left=Map.Room.roomsnames[old])
                        if show:
                        	print(f"Welcome to {r.name}!")
                        break
    def cleanup(self):
        for r in self.lor:
            cleaned = []
            for connection in r.out:
                name = connection.name if isinstance(connection, Map.Room) else connection
                if name not in cleaned:
                    cleaned.append(name)
            r.out = tuple(cleaned)
        EventHook.onmapcleanup(m=self)
    def generaterooms(self, num=2, *ro, debug=False, hidden=None, showit=False, loot=None, needs=None, buys=None, truehide=None, mode="default"):
        #for reference of the original: def generaterooms(self, num=2, *ro, debug=False, hidden=[], showit=False, loot={}, needs={}, buys=[], truehide={}, mode="default", rules={}):
        if hidden is None:
            hidden = []
        if loot is None:
            loot = {}
        if needs is None:
            needs = {}
        if buys is None:
            buys = []
        if truehide is None:
            truehide = {}
        mode = str(mode)
        if not ro:
        	ro = ["room a", "room b", "room c", "room d", "room e"]
        if "enter" in ro:
            Error.error("Error 7: Cannot use softlocked generation keywords!")
            return
        nocs = [r.name for r in self.lor]
        if any([True if r in [rr.name for rr in self.lor] else False for r in ro]):
            Error.error("Error 10: Cannot have duplicate rooms")
            return
        roms = list(ro) + self.lor
        if mode != "default":#dev note: this took so long i swear it crashed at every nook and cranny finally fixed it tho
            if not roms:
                Error.error("Error 6: No rooms detected")
                return
            nosrobots = []
            roms = [r.name if isinstance(r, Map.Room) else r for r in roms]
            for r in roms:
                if r in hidden:
                    h = True
                else:
                    h = False
                if r in loot.keys():
                    l = True
                    lootgiven = loot[r]
                else:
                    l = False
                    lootgiven = []
                if r in needs.keys():
                    n = True
                    needsgiven = needs[r]
                else:
                    n = False
                    needsgiven = []
                if r in buys:
                    m = True
                else:
                    m = False
                if r in truehide.keys():
                    th = True
                    condsgiven = truehide[r]
                else:
                    th = False
                    condsgiven = []
                nosrobots.append(Map.Room.createroom(r, hide=h, addloot=lootgiven, req=needsgiven, merchant=m, bes=condsgiven, pasvoir=th))
            #second check just to be safe :D
            if not nosrobots:
                Error.error("Error 6: No rooms detected")
                return
            if len(nosrobots) < 4:
                Error.error("Error 28: Not enough rooms for custom generation!")
                return
            basemode = mode.split("/")[0]
            if basemode == "tree":
                options = mode.split("/") if "/" in mode else []
                connected = [nosrobots[0]]
                unconnected = nosrobots[1:]
                while unconnected and remainingmax > 0:
                    entry = random.choice(connected)
                    exit = random.choice(unconnected)
                    entry.out += (exit.name,)
                    connected.append(unconnected.pop(unconnected.index(exit)))
                if "/" in mode:
                    if "random" in options:
                        for n in nosrobots:
                            rc = random.choice(nosrobots).name
                            while rc == n.name:
                                rc = random.choice(nosrobots).name
                            n.out += (rc,)
            elif basemode == "linear":
                options = mode.split("/") if "/" in mode else []
                if "/" in mode:
                    if "shuffled" in options:
                        random.shuffle(nosrobots)
                for i in range(len(nosrobots)):
                    if nosrobots[i] != nosrobots[-1]:
                        nosrobots[i].out += (nosrobots[i + 1].name,)
                if "/" in mode:
                    if "twoway" in options:
                        for i in range(len(nosrobots)):
                            if nosrobots[i] != nosrobots[0]:
                                nosrobots[i].out += (nosrobots[i - 1].name,)
            elif basemode == "hub":
                options = mode.split("/") if "/" in mode else []
                if "." not in mode:
                    Error.error("Error 25: Must have a central point")
                    return
                else:
                    central = [n for n in nosrobots if n.name == mode.split(".", 1)[1].split("/")[0]]
                    remaining = [n for n in nosrobots if n not in central]
                    if not central:
                        Error.error("Error 26: Invalid central room")
                        return
                    else:
                        central = central[0]
                    for n in nosrobots:
                        if n != central:
                            n.out += (central.name,)
                    if "/" in mode:
                        if "connectall" in options:
                            for n in nosrobots:
                                if n != central and n in remaining:
                                    connection = random.choice(nosrobots)
                                    while connection == central or connection == n:
                                        connection = random.choice(nosrobots)
                                    n.out += (connection.name,)
                                    remaining.remove(n)
                        if "twoway" in options:
                            for n in nosrobots:
                                if n != central and n.name in central.out:
                                    n.out += (central.name,)
            elif basemode == "grid":
                options = mode.split("/")[3:]
                grid = {}
                try:
                    x, y = int(mode.split("/")[1]), int(mode.split("/")[2])
                except Exception as e:
                    Error.error("Error 29: X and Y values were not handled properly")
                    return
                if x < 0 or y < 0:
                    Error.error("Error 33: X and Y must not be negatives!")
                if len(nosrobots) > x * y:
                    Error.error("Error 30: Amount of rooms must be lower than the amount of coordinates given.")
                    return
                print(f"Grid Mode coordinates: x {x}, y {y}")
                neighborsmode = False
                def isadjacent(a, b):
                    try:
                        return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                    except Exception as e:
                        Error.error(f"Error 999999999: its in isadjacent! exception = {e}", finderror=True, type="Test")# = {e} a = {a} b = {b}", finderror=True)
                if "neighbors" in options:
                    neighborsmode = True
                    #THE FIVE RULES: A COORDINATE IS x, y, THE VALUE OF grid[(x, y,)] SHOULD EITHER BE A ROOM OR NONE, EVERY ROOM HAS ONE gridcoords, USE MANHATTAN DISTANCE (which i HAVE to put in a function otherwise my hands will D I E), AND A ROOM MUST BE PUT IN AN EMPTY COORDINATE
                    #the initialization of the grid coordinates
                    gx, gy = 0, 0
                    for i in range(x * y):
                        grid[(gx, gy,)] = None
                        if gx  + 1>= x:
                            gy += 1
                            gx = 0
                        else:
                            gx += 1
                    #then the assignment of a coordinate
                    previous = None
                    previousinstance = None
                    taken = []
                    for n in nosrobots:
                        if previous is None:
                            n.gridcoords = (x // 2, y // 2)
                            grid[n.gridcoords] = n
                            taken.append((n, n.gridcoords))
                            previous = n.gridcoords
                            previousinstance = n
                            continue
                        neighbors = []
                        for pos, room in grid.items():
                            if room is None and isadjacent(pos, previous):
                                neighbors.append(pos)
                        mandswitch = False
                        if not neighbors:
                           mandswitch = True
                           if "branches" not in options:
                               options.append("branches")
                        if not mandswitch:
                            chosen = random.choice(neighbors)
                            n.gridcoords = chosen
                            grid[chosen] = n
                            #then finally the connection
                            n.out += (grid[previous],)
                            grid[previous].out += (n.name,)
                            previous = chosen
                            taken.append((n, previous))
                        candidates = taken.copy()
                        if "branches" in options and not n.out:
                            chosenneighbors = []
                            if random.random() < 0.1 or mandswitch:
                                while not chosenneighbors and candidates:
                                    chosenbranchplace = random.choice(candidates)
                                    chosenbranch = chosenbranchplace[1]
                                    for pos, room in grid.items():
                                        if room is None and isadjacent(pos, chosenbranch):
                                            chosenneighbors.append(pos)
                                    candidates.remove(chosenbranchplace)
                                if chosenneighbors:
                                    chosen = random.choice(chosenneighbors)
                                    n.gridcoords = chosen
                                    grid[chosen] = n
                                    n.out += (chosenbranchplace[0].name,)
                                    chosenbranchplace[0].out += (n.name,)
                                    previous = chosenbranch
                                    taken.append((n, previous))
                                else:
                                    Error.warn("W3: Branching was not possible.")
                                    #may you rest in peace, previous = previous
                            if mandswitch:
                                options.remove("branches")
                if not options:
                    gx, gy = 0, 0
                    for i in range(x * y):
                        grid[(gx, gy)] = None
                        if gx >= x:
                            gy += 1
                            gx = 0
                        else:
                            gx += 1
                    available = [pos for pos, room in grid.items() if room is None]
                    for n in nosrobots:
                        if not available:
                            break
                        found = random.choice(available)
                        grid[found] = n
                        n.gridcoords = found
                        available.remove(found)
                for n in nosrobots:
                    if n.gridcoords == ():
                        print(n.name, f"has empty coordinates! {n.gridcoords}")
                for n in nosrobots:
                    for nn in nosrobots:
                        if debug:
                            print(n.gridcoords, nn.gridcoords)
                        if isadjacent(n.gridcoords, nn.gridcoords):
                            nn.out += (n.name,)
            else:
                Error.error("Error 27: Invalid mode")
                return
            self.lor = nosrobots
            self.cleanup()
            EventHook.onmapgenerated(m=mode, de=debug, shown=showit, exits=num)
            return
        saved = [s for s in roms if isinstance(s, dict)]
        if debug:
            for s in saved:
                for k, v in s.items():
                    print(k, v, end="")
                    k = "".join(k)
                    print(k, v, end="")
        roms = [str(r.name) if isinstance(r, Map.Room) else str(r) if not isinstance(r, dict) else None for r in roms]
        roms = [r for r in roms if r is not None]
        for l in loot.keys():
            if l not in roms:
                Error.error("Error 11: Unknown room detected to give items to")
                return
        for n in needs.keys():
            if n not in roms:
                Error.error("Error 12: Unknown room detected to add access requirements to")
                return
        for b in buys:
            if b not in roms:
                Error.error("Error 13: Unknown room detected to make into a merchant room!")
                return
        if saved and not roms:
            Error.error("Error 8: Must have a different room in order to create a pre-set room")
            return
        hasdict = None
        special = None
        if saved:
            hasdict = True
            if any([True if len(s.keys()) > 1 else False for s in saved]):
                Error.error("Error 0: Dictionaries cannot have keys longer than 1.")
                return
        else:
            hasdict = False
        if debug:
            print(hasdict)
        if hasdict:
        	special = random.choice(roms)
        	if debug:
        	    print(special)
        	n = roms.index(special)
        	roms.append("enter")
        needed = num + 2 if not hasdict else num + 3
        if len(roms) < needed:
            Error.error(f"Error 9: Need at least {needed} rooms in order to generate them")
            return
        nosrobots = []
        for r in roms:
            if r in hidden:
                ishidden = True
            else:
                ishidden = False
            if r in loot:
                given = loot[r]
                hasloot = True
            else:
                hasloot = False
                given = []
            if r in needs:
                wneeded = needs[r] #short for whats needed
                hasneeds = True
            else:
                wneeded = []
                hasneeds = False
            if r in buys:
                buyer = True
            else:
                buyer = False
            if r in truehide.keys():
                avoirlesbesoins = True
                lesbesoins = truehide[r]
            else:
                avoirlesbesoins = False
                lesbesoins = []
            if showit:
            	print(f"Loading {r}" + f" with loot {given}" if hasloot else "" + f" with a need of {wneeded}" if hasneeds else "" + " and is hidden in menu" if ishidden else "" + " and is a merchant" if buyer else "" + " and is hidden by condition(s) {lesbesoins} " if avoirlesbesoins else "" + "...", end="\r")
            if not isinstance(r, dict): #just to be safe!
                rom = random.sample(roms, num)
                while r in rom:
                    rom = random.sample(roms, num)
                if r == special and hasdict:
                    rom = ["enter"]
                if r == "enter" and hasdict:
                    for s in saved:
                        for k, v in s.items():
                            rom = k
                if r in hidden:
                    nosrobots.append(Map.Room.createroom(r, rom, hide=True, addloot=given, req=wneeded, merchant=buyer, pasvoir=avoirlesbesoins, bes=lesbesoins))
                else:
                    nosrobots.append(Map.Room.createroom(r, rom, addloot=given, req=wneeded, merchant=buyer, pasvoir=avoirlesbesoins, bes=lesbesoins))
        for s in saved:
            if showit:
            	print(f"Loading {s}...", end="\r")
            if isinstance(s, dict): #just to be safe part 2!!
                for k, v in s.items():
                    fixed = [v if isinstance(v, list) else [v]]
                    if isinstance(v, list):
                        if k in hidden:
                            nosrobots.append(Map.Room.createroom(k, *v, hide=True))
                        else:
                            nosrobots.append(Map.Room.createroom(k, *v))
                    else:
                        if k in hidden:
                            nosrobots.append(Map.Room.createroom(k, v, hide=True))
                        else:
                            nosrobots.append(Map.Room.createroom(k, v))
                    unincludeds = [r for r in roms if r != s and r != k]
                    if isinstance(v, list):
                        for t in v:
                            nosrobots.append(Map.Room.createroom(t, random.choice(unincludeds)))
                    else:
                        nosrobots.append(Map.Room.createroom(v, random.choice(unincludeds)))
        if showit:
        	print("\033[2K", "\r")
        if debug:
            print([n.name for n in nosrobots])
            print([r for r in rom])
            print([s.name for s in self.lor])
            print([saved])
        for n in nosrobots:
            n.out = tuple(dict.fromkeys(n.out))
        self.lor = nosrobots
        EventHook.onmapgenerated(m=mode, de=debug, shown=showit, exits=num)
    @classmethod
    def maprooms(cls):
        for m in cls.maps:
            print("=" * 30)
            print(m.name, "Navigation Map")
            for r in m.lor:
                print("|---", r.name, "\n|------ goes to", ",".join([o.name if isinstance(o, Map.Room) else o for o in r.out]))
    @classmethod
    def pathfinder(cls, start, end, *, show=True):
    	if start not in Map.Room.roomsnames or end not in Map.Room.roomsnames:
    		if show:
    			Error.error("Error 1: Start/End room not found!")
    		else:
    			return 1
    		return
    	for m in Map.maps:
    		ns = [n.name for n in m.lor]
    		if start in ns:
    			startmap = m
    	for m in Map.maps:
    		ns = [n.name for n in m.lor]
    		if end in ns:
    			endmap = m
    	if startmap != endmap:
    		if show:
    			Error.error("Error 2: Starting room and Ending room must be in the same map!")
    		else:
    			return 2
    		return
    	queue = [[start]]
    	visited = {start}
    	while queue:
    		path = queue.pop(0)
    		currentroom = path[-1]
    		if currentroom == end:
    			return path
    		currentroom = Map.Room.roomsnames[currentroom]
    		for neighbor in currentroom.out:
    			nname = neighbor.name if isinstance(neighbor, Map.Room) else str(neighbor)
    			if nname not in visited:
    				visited.add(nname)
    				newpath = list(path)
    				newpath.append(nname)
    				queue.append(newpath)
    	if show:
    		Error.error(f"Error 3: No paths found between {start} and {end}")
    	else:
    		return 3
    	return
    @classmethod
    def check(cls, original=None, shows=False):
    	if original is None:
    	    if not cls.maps:
    	        if shows:
    	            Error.error("Error 5: No maps detected!")
    	        return 5
    	    original = cls.maps[0].lor[0]
    	if isinstance(original, Map.Room):
    	    if not cls.maps[0].lor:
    	        if shows:
    	            Error.error(f"Error 6: No rooms detected in {cls.maps[0].name!r}")
    	        return 6
    	    orginstance = original
    	    original = original.name
    	good = 0
    	all = 0
    	results = []
    	visited = {original}
    	queue = [original]
    	while queue:
    	    current = queue.pop(0)
    	    lesortirs = Map.Room.roomsnames[current].out if isinstance(current, str) else current.out
    	    for neighbor in lesortirs:
    	        nom = neighbor.name if isinstance(neighbor, Map.Room) else neighbor
    	        if nom not in visited:
    	            visited.add(nom)
    	            queue.append(neighbor)
    	good = len(visited)
    	for m in Map.maps:
    	    if orginstance in m.lor:
    	        all = len(m.lor)
    	        break
    	else:
    	    print(f"W1: Could not find {original!r} in any map.")
    	if shows:
    		print(f"{good}/{all}")
    		print(", ".join(results))
    	else:
    		return f"{good}/{all}"
    @classmethod
    def goto(cls, where, shows=True):
    	if player.rlocation == None:
    		return
    	route = Map.pathfinder(player.rlocation.name, where, show=False)
    	if isinstance(route, list):
    		for way in route:
    			Map.Room.diffroom(into=way, show=shows)
    	else:
    		print("No route found. Error code:", route)
    @classmethod
    def gtc(cls, ma, exits, *rro, maxattempts=10000, show=False):#stands for generate til connection
        results = ["0", "1"]
        if isinstance(ma, str):
            if ma not in cls.mapsnames.keys():
                Error.error("Error 404f: Map not found")
        if maxattempts <= 0:
            Error.error("Error 22a: Invalid number for max (must be higher than 0)")
            return
        if not isinstance(ma, str) and not isinstance(ma, cls):
            Error.error("Error 22: Invalid type for argument (map)", ma)
            return
        if not isinstance(exits, int):
            Error.error("Error 22: Invalid type for argument (exits)")
            return
        if not isinstance(maxattempts, int) and not isinstance(maxattempts, float):
            Error.error("Error 22: Invalid type for argument (maxattempts)")
            return
        m = cls.mapsnames[ma] if isinstance(ma, str) else ma
        rs = rro
        attempts = 0
        best = None
        bestscore = -1
        m.generaterooms(exits, *rs)
        results = cls.check().split("/") if "/" in cls.check() else "ERROR"
        if results == "ERROR":
            print("Unknown Error 0: Something went wrong.")
            return
        if results[0] == results[1]:
            print("Fully connected map generated (1)")
            return
        ran = False
        while results[0] != results[1] and attempts < maxattempts:
            if show:
                print(attempts, f"{results[0]}/{results[1]}", end="\r")
            ran = True
            m.lor.clear()
            m.generaterooms(exits, *rs)
            results = cls.check().split("/") if "/" in cls.check() else "ERROR"
            if results == "ERROR":
                Error.error("Unknown Error 1: Something went wrong.")
            if int(results[0]) != int(results[1]):
                if int(results[0]) > bestscore:
                    bestscore = int(results[0])
                    best = deepcopy(m.lor)#just learnt that deepcopy existed :D
                m.lor.clear()
                attempts += 1
            else:
                print("Fully connected map generated.")
                return
        if ran:
            Error.error("Error 21: Fully connected map could not be generated in time. Switching map to most found connections...")
        else:
            Error.error("Unknown Error 2: Something went wrong and the script wasnt run.")
        m.lor = best
    @classmethod
    def cyclegen(cls, m, *ro):
        m = cls.mapsnames[m] if isinstance(m, str) else m if isinstance(m, cls) else None
        if m is None:
            Error.error("Error 22: Selected map must be a map or string!")
            return
        if m not in cls.maps:
            Error.error("Error 404g: Map not found")
            return
        if len(ro) < 3:
            Error.error("Error 24: At least 3 rooms are required!")
            return
        rms = [cls.Room.createroom(r) for r in ro]
        current = rms[0]
        remaining = list(range(1, len(rms)))
        while remaining:
            tn = random.choice(remaining)
            current.out = current.out + (rms[tn].name,)
            current = rms[tn]
            remaining.remove(tn)
        rms[-1].out = rms[-1].out + (rms[0].name,)
        m.lor = rms
    @classmethod
    def validate(cls, room):
        if not isinstance(room, cls.Room):
            try:
                cls.Room.roomsnames[room]
            except KeyError:
                Error.error("Error 404h: Room not found!")
                return
        nonexistent = []
        invalidconnections = []
        for o in room.out:
            try:
                if isinstance(o, Map.Room):
                    confirmed = o.name
                else:
                    confirmed = o
                test = Map.Room.roomsnames[confirmed]
            except KeyError:
                nonexistent.append(confirmed)
        if room.gridcoords != ():
            for o in room.out:
                if isinstance(o, Map.Room):
                    confirmed = o.name
                else:
                    confirmed = o
                if not isadjacent(room.gridcoords, Map.Room.roomsnames[confirmed].gridcoords):
                    invalidconnections.append(confirmed)
        if nonexistent or invalidconnections:
            valid = False
        else:
            valid = True
        return {"valid": valid, "nonexistent": nonexistent, "invalidconnections": invalidconnections}
class System:
    name = "Cutlass"
    version = "1.1.2.1"
    state = "Beta"
    @classmethod
    def credits(cls):
        print(f"================ {cls.name.upper()} ================\n")
        print("Made by airbreather5277 aka my name is a joke\n")
        print("A procedural generator game engine that creates maps with rooms connected to one another.")
        print("Tested by: None")
        print("Contributors: None")
        print("PS from dev: i am lonely :(")
        print(f"Version: {cls.version}")
        print(f"State: {cls.state}")
        vns = cls.version.split(".")
        vntvp = []
        print("=== CHANGELOG ===")
        for i, item in enumerate(vns):
            vntvp.append((item, vs[i]))
        for vn, vp in vntvp:
            print(f"{vn}: {vp}\n")
        print("=== TIPS & TRICKS ===\n")
        print("1: You can change the EventHook variables to make it so that some actions do different things!")
        print("2: You can use GTC To generate a fully connected map! That, or it will give you its best option!")
        print("3: You can use Map.pathfinder() to find a link between two maps!")
        print("4: You should never create a Room instance by itself, since it will be completely disconnected from all other rooms!")
        print("5: You can use Demo() for a terminal for some basic commands!")
    @classmethod
    def radar(cls):
        if not Map.maps or not Map.Room.rooms:
            Error.error("Error 5: No maps detected")
            return
        for r in Map.Room.rooms:
            print(r.name, end=", ") #COMPLETLY bypass the thingy of truehide and hide, and other filteration effects
        Map.Room.diffroom(default=True)
        print(player.rlocation.name)
        print(Map.check(shows=True))
        player.changemaps()
    @classmethod
    def addevent(cls, room, event, *, customs="N", mode="a"):
        if room not in Map.Room.roomsnames.keys():
            Error.error("Error 404c: Room not found")
            return
        room = Map.Room.roomsnames[room]
        if not callable(event):
            Error.error("Error 18: event must be a function (verified by callable(event))")
            return
        if mode == "a":
            room.events[event] = customs
            cdp = [c for c in customs if c.startswith("cooldown")]
            cooldown = int(cdp[0].split(": ")[1].strip()) if cdp else 0
            room.eventcds[event] = [cooldown, cooldown]
        elif mode == "r":
            room.events = {event: customs}
            cdp = [c for c in customs if c.startswith("cooldown")]
            cooldown = int(cdp[0].split(": ")[1].strip()) if cdp else 0
            room.eventcds = {event: [cooldown, cooldown]}
        else:
            Error.error("Error 17: must have \"a\" (append) or \"r\" (replace) in the mode.")
            return #uneccesary, ik. but wouldnt hurt to be safe.
        EventHook.oneventadd(event=event, customs=customs)
    @classmethod
    def kill(cls, check, name):
        if check == "m":
            if name in Map.mapsnames.keys():
                Map.mapsnames[name].active = False
                Map.maps.remove(Map.mapsnames[name])
                del Map.mapsnames[name]
                EventHook.onmapkill(mapkilled=name)
            else:
                Error.error("Error 404a: Map not found")
        elif check == "r":
            if name in Map.Room.roomsnames.keys():
                for r in Map.Room.rooms:
                    if Map.Room.roomsnames[name].name in r.out:
                        r.out = list(r.out)
                        r.out.remove(Map.Room.roomsnames[name].name)
                        r.out = tuple(r.out)
                for m in Map.maps:
                     if Map.Room.roomsnames[name] in m.lor:
                         m.lor.remove(Map.Room.roomsnames[name])
                Map.Room.roomsnames[name].active = False
                Map.Room.rooms.remove(Map.Room.roomsnames[name])
                del Map.Room.roomsnames[name]
                EventHook.onroomkill(roomkilled=name)
            else:
                Error.error("Error 404b: Room not found.")
        else:
            Error.error("Error 16: Must have \"m\" (maps) or \"r\" (rooms) in the check variable.")
    @classmethod
    def listevents(cls):
        for r in Map.Room.rooms:
            print(f"{r.name} events:")
            if r.events:
                ns = [e.__name__ for e in r.events]
                cs = [r.events[e] for e in r.events]
                re = [e for i in zip(ns, cs) for e in i]
                print(", ".join(re))
            else:
                print("No events")
    @staticmethod
    def attempt(method, *args, ofkind=None, fallback=None, **kwargs):
        try:
            if ofkind is None:
                return method(*args, **kwargs)
            else:
                return getattr(ofkind, method, EventHook.defaultfunc)(*args, **kwargs)
        except Exception as e:
            Error.error(f"Error 4: {e}", errtype="Unknown")
            if callable(fallback):
                fallback(e)
            return fallback
class ModAPI:
    def __init__(self):
        self.System = System
        self.Room = Map.Room
        self.Map = Map
        self.player = player
        self.EventHook = EventHook
    def set(self, var, val):
        setattr(self, var, val)
    def get(self, var):
        if hasattr(self, var):
            return getattr(self, var)
        else:
            Error.error("Error 404e: Variable doesnt exist.")
            return
class Mods:
    filesloaded = []
    @classmethod
    def loadmod(cls, file, debug=False):
        if not file.endswith(".cutl"):
            Error.error("Error 34: Must use .cutl files!")
        if file == sys.argv[0]:
            Error.error("Error 30: Cannot run self!")
            return
        print("By using loadmod you acknowledge that the file you have inputted will be executed as python code.")
        dimports = ["os", "subprocess", "socket", "shutil", "ctypes"]
        dfunctions = ["exec", "eval", "compile", "__import__"]
        try:
            with open(file, "r") as f:
                mod = f.read()
        except FileNotFoundError:
            Error.error("Error 404d: File not found")
            return
        try:
            modtree = ast.parse(mod)
        except Exception as e:
            print("General Error:", e)
            return
        warning = False
        for n in ast.walk(modtree):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    if (nom := alias.name.split(".")[0].strip()) in dimports:
                        print(f"Dangerous import: {nom}")
                        warning = True
            if isinstance(n, ast.ImportFrom):
                if n.module:
                    if (nom := n.module.split(".")[0].strip()) in dimports:
                        print(f"Dangerous import: {nom}")
                        warning = True
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name) and n.func.id in dfunctions:
                    print(f"Dangerous function: {n.func.id}")
                    warning = True
        if warning:
            print("Dangerous things were detected in this file. Would you like to continue?")
            answer = input("Y/N")
            if "y" in answer.lower():
                print("Execution will now be continued.")
            elif "n" in answer.lower():
                print("Execution cancelled.")
                return
        api = ModAPI()
        v = [l for l in mod.split("\n") if l.startswith("#version:")]
        fileversion = v[0].split(": ")[1].strip() if v else "IND"
        isd = [l for l in mod.split("\n") if l.startswith("#isdev:")]
        if isd:
            if isd[0].split(": ")[1].strip().lower() != "true" and isd[0].split(": ")[1].strip().lower() != "false":
                Error.error("Error 23: isdev value is invalid!")
                return
        isdev = isd[0].split(": ")[1].strip().lower() == "true" if isd else False
        if fileversion != "IND":
            if fileversion != System.version and not isdev:
                Error.error(f"Error 20: File version doesnt equal current version (file version {fileversion} needs to be {System.version})")
                return
            if isdev:
                Error.warn("W2: Isdev is active, which means this script bypasses file version checking.")
            if not isdev and fileversion == System.version:
                pass
        else:
            Error.warn("W0: File does not specify a version.")
        try:
            exec(mod, {"api": api})
        except Exception as e:
            Error.error(f"LError: {e}", errtype="Unknown")
            return
        print("Code Executed.")
        fn = os.path.basename(file)
        Mods.filesloaded.append(fn)
        print("[DEBUG] ", EventHook.onmodload)
        EventHook.onmodload(filepath=file)
class Demo:
    def __init__(self):
        self.running = True
        self.run()
    def run(self):
        while self.running:
            command = input("Type 'help' for commands: ")
            command = command.lower().strip()
            match command.split():
                case ["help"]:
                    print("=== HELP ===")
                    print("generate [mode] [options]")
                    print("raise [error]")
                    print("credits")
                    print("rooms")
                    print("maps")
                    print("destroy [m or r] [map or room]")
                    print("quit")
                case ["generate", mode, *options]:
                    testmap = Map("TestMap")
                    testmap.generaterooms(mode=f"{mode}/{'/'.join(options)}")
                    print(mode)
                case ["raise", *errors]:
                    Error.error(f"Error 0: {' '.join(errors)}", errtype="Test")
                case ["credits"]:
                    System.credits()
                case ["rooms"]:
                    for r in Map.Room.rooms:
                        print(r.name, len(r.out))
                case ["maps"]:
                    for m in Map.maps:
                        print(m.name, len(m.lor))
                case ["destroy", mor, *target]:
                    target = "".join(target)
                    System.kill(mor, target)
                case ["quit"]:
                    self.running = False
                case _:
                    Error.error("Error 32: Unknwon command for demo terminal.")
class SoL:
    @staticmethod
    def saveto(file):
        if not file.endswith(".cutl"):
            file += ".cutl"
        with open(file, "wb") as f:
            data = {"maps": Map.maps, "version": System.version, "player": player}
            pickle.dump(data, f)
    @staticmethod
    def loadfrom(file):
        if not file.endswith(".cutl"):
            Error.error("Error 34: Must use .cutl files!")
            return
        try:
            with open(file, "rb") as f:
                data = pickle.load(f)
                if data["version"] != System.version:
                    Error.error(f"Error 20: File version doesnt equal current version (file version {data['version']} needs to be {System.version})")
                Map.maps = data["maps"]
                Map.mapsnames = {m.name: m for m in Map.maps}
                Map.Room.rooms = [r for m in Map.maps for r in m.lor]
                Map.Room.roomsnames = {r.name: r for r in Map.Room.rooms}
                player = data["player"]
        except Exception as e:
            Error.error(f"Error 5: {e}", errtype="Unknown")
            return
    @staticmethod
    def info(file):
        try:
            with open(file, "rb") as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            Error.error(f"Error 6: {e}", errtype="Unknown")