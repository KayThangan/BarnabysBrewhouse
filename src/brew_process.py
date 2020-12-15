"""
This module is a program that simulates brew process for a given gyle
number, beer and quantity.
"""
import time
from threading import Lock
from transitions import Machine
from brew_process_dict import allocate_tank, release_tank, \
    tank_status, update_beer_stock, beer_stock_status
from brew_logger import errorLogger, eventLogger

lock = Lock()
beers_producer_queue = []

errorLogger = errorLogger()
eventLogger = eventLogger()

# InventoryManagement
def start_process_for_beers():
    """
    This method starts the beer process.
    """
    with lock:
        for beer_obj in beers_producer_queue:
            if beer_obj.state == "start":
                beer_obj.hot_brew_process()
            elif beer_obj.state == "hot_brew":
                beer_obj.fermentation_process()
            elif beer_obj.state == "fermentation":
                beer_obj.conditioning_and_carbonation_process()
            elif beer_obj.state == "conditioning":
                beer_obj.bottling_and_labelling_process()
            elif beer_obj.state == "bottling":
                beer_obj.finish_process()

def create_process_for_beer(gyle_no: int, beer_name: str,
                            quantity: int):
    """
    This create brew process for a beer.
    :param gyle_no: an integer showing the batch number.
    :param beer_name: a string representing the name of the beer.
    :param quantity: an integer of the beer quantity.
    """
    errorLogger.info("Creating a brewing process for a given batch of "
                     "beer.")
    if not find_process_for_beer(gyle_no, beer_name, quantity):
        with lock:
            beers_producer_queue.append(BrewingProcess(gyle_no,
                                                       beer_name,
                                                       quantity,
                                                       {},
                                                       False,
                                                       "start",
                                                       "start"))
            eventLogger.critical("@state : @%s",
                                 store_beer_process_data())
    else:
        errorLogger.warning("Beer process already exists")

def find_process_for_beer(gyle_no: int, beer_name: str, quantity: int):
    """
    This method finds the beer which is taking part in a process.
    :param gyle_no: an integer of the batch number.
    :param beer_name: a string containing the name of the beer.
    :param quantity: an integer representing the quantity of the beer.
    """
    errorLogger.info("Finding a given beer from the brewing process.")
    for beer_obj in beers_producer_queue:
        if beer_obj.gyle_no == gyle_no and \
                beer_obj.bear_name == beer_name and \
                beer_obj.quantity == quantity:
            return beer_obj
    return None

def move_process_to_next_state(gyle_no: int, beer_name: str,
                               quantity: int):
    """
    This function allow the process to move the process to the next
     state.
    :param gyle_no: an integer of the batch number.
    :param beer_name: a string containing the name of the beer.
    :param quantity: an integer representing the quantity of the beer.
    """
    errorLogger.info("Moving a given beer in the brewing process to "
                     "the next stage.")
    beer_obj = find_process_for_beer(gyle_no, beer_name, quantity)
    if beer_obj:
        beer_obj.set_move_next()
        time.sleep(0.2)
        eventLogger.critical("@state : @%s", store_beer_process_data())


def remove_process_for_beer(gyle_no: int, beer_name: str,
                            quantity: int):
    """
    This function allow the process to remove the process to the next
     state.
    :param gyle_no: an integer of the batch number.
    :param beer_name: a string containing the name of the beer.
    :param quantity: an integer representing the quantity of the beer.
    """
    errorLogger.info("Removing a given beer in the brewing process.")
    beer_obj = find_process_for_beer(gyle_no, beer_name, quantity)
    if beer_obj:
        beers_producer_queue.remove(beer_obj)
        eventLogger.critical("@state : @%s", store_beer_process_data())


def status_process_for_beer() -> dict:
    """
    This gets the status of the current beers in process.
    """
    errorLogger.info("Retrieving the status of a given beer in the "
                     "brewing process.")
    with lock:
        beer_queue = {}
        for beer_obj in beers_producer_queue:
            key = beer_obj.bear_name + ":" + str(beer_obj.gyle_no) + \
                  ":" + str(beer_obj.quantity)
            tmp = {key: {
                "gyle_no": beer_obj.gyle_no,
                "beer_name": beer_obj.bear_name,
                "quantity": beer_obj.quantity,
                "process_tank": beer_obj.process_tanks,
                "is_allocate": beer_obj.is_allocate
            }}
            beer_queue.update(tmp)
        return beer_queue

def status_process_for_tank() -> dict:
    """
    This gets the status of the current tanks in process.
    :return:
    """
    errorLogger.info("Retrieving the status of the tanks.")
    return tank_status()

def status_process_for_beer_stock() -> dict:
    """
    This gets the status of the current beer stock in process.
    :return:
    """
    errorLogger.info("Retrieving the status of the current beers in "
                     "stock.")
    return beer_stock_status()

def store_beer_process_data() -> list:
    """
    Storing beer process data
    :return:
    """
    process = []
    for beer_obj in beers_producer_queue:
        process.append({"name": beer_obj.bear_name,
                        "qty": beer_obj.quantity,
                        "gyle": beer_obj.gyle_no,
                        "state": beer_obj.cur_state,
                        "is_allocate": beer_obj.is_allocate,
                        "p_tank": beer_obj.process_tanks})
    return process

def restore_beer_process(gyle_no, beer_name, qty, p_state, is_allocate,
                         p_tank):
    """
    This function restores the beer process.
    :param gyle_no: an integer of the batch number.
    :param beer_name: a string containing the name of the beer.
    :param qty: an integer representing the quantity of the beer.
    :param p_state: a string of the state.
    :param is_allocate: a boolean of the process being allocated.
    :param p_tank: a dictionary of the process tank.
    :return:
    """
    state = p_state
    for p in p_tank:
        state = p
    beers_producer_queue.append(BrewingProcess(gyle_no, beer_name, qty,
                                               p_tank, is_allocate,
                                               p_state, state))

class BrewingProcess(object):
    """
    This class contain a state machine for the brew processes.
    """
    states = ["start", "hot_brew", "fermentation", "conditioning",
              "bottling", "finish", "incomplete"]

    # Initialize the state machine
    def __init__(self, gyle_no, beer_name, quantity, process_tanks,
                 is_allocate, p_state, c_state):
        super(BrewingProcess)

        self.gyle_no = gyle_no
        self.bear_name = beer_name
        self.quantity = quantity
        self.process_tanks = process_tanks
        self.can_move_next = False
        self.lock = Lock()
        self.prev_state = p_state
        self.cur_state = c_state
        self.is_allocate = is_allocate

        self.machine = Machine(
            model=self,
            states=BrewingProcess.states,
            initial=self.prev_state,
            ignore_invalid_triggers=True,
            auto_transitions=True,
            # ordered_transitions=True
        )

        # Hot Brew
        self.machine.add_transition(
            trigger="hot_brew_process",
            source="start",
            dest="hot_brew",

            # we check only enter 'hot_brew' state if the
            # 'has_cooks_ingredients_complete' is competed

            # otherwise we go to 'incomplete', as you can see in the
            # next transition
            conditions=['has_cooks_ingredients_complete'],
            after="cooks_ingredients_process_complete",
        )

        self.machine.add_transition(
            trigger='hot_brew_process',
            source='start',
            dest='incomplete',
        )

        # Fermentation
        self.machine.add_transition(
            trigger="fermentation_process",
            source="hot_brew",
            dest="fermentation",

            # we check only enter 'fermentation' state if the
            # 'has_fermentation_complete' is competed

            # otherwise we go to 'incomplete', as you can see in the
            # next transition
            conditions=['has_fermentation_complete'],
            after="fermentation_process_complete",
        )

        self.machine.add_transition(
            trigger='fermentation_process',
            source='hot_brew',
            dest='incomplete',
        )

        # Conditioning
        self.machine.add_transition(
            trigger="conditioning_and_carbonation_process",
            source="fermentation",
            dest="conditioning",

            # we check only enter 'conditioning' state if the
            # 'has_conditioning_and_carbonation_complete' is completed

            # otherwise we go to 'incomplete', as you can see in the
            # next transition
            conditions=['has_conditioning_and_carbonation_complete'],
            after="conditioning_and_carbonation_process_complete"
        )

        self.machine.add_transition(
            trigger='conditioning_and_carbonation_process',
            source='fermentation',
            dest='incomplete',
        )

        # Bottling
        self.machine.add_transition(
            trigger="bottling_and_labelling_process",
            source="conditioning",
            dest="bottling",

            # we check only enter 'bottling' state if the
            # 'has_bottling_and_labelling_complete' is completed

            # otherwise we go to 'incomplete', as you can see in the
            # next transition
            conditions=['has_bottling_and_labelling_complete'],
            after="bottling_and_labelling_process_complete"
        )

        self.machine.add_transition(
            trigger='bottling_and_labelling_process',
            source='conditioning',
            dest='incomplete',
        )

        self.machine.add_transition(
            trigger='finish_process',
            source='bottling',
            dest='finish',
            after="finish_process_complete"
        )

        # we notify the states whenever we enter/exit each state,

        # callbacks declared on the 'destination' state on
        # 'add_transition'
        self.machine.on_enter_start('do_on_enter')
        self.machine.on_enter_hot_brew('do_on_enter')
        self.machine.on_enter_fermentation('do_on_enter')
        self.machine.on_enter_conditioning('do_on_enter')
        self.machine.on_enter_bottling('do_on_enter')
        self.machine.on_enter_incomplete('do_on_enter')

        # callbacks declared on the 'source ' state on 'add_transition'
        self.machine.on_exit_start('do_on_exit')
        self.machine.on_exit_hot_brew('do_on_exit')
        self.machine.on_exit_fermentation('do_on_exit')
        self.machine.on_exit_conditioning('do_on_exit')
        self.machine.on_exit_bottling('do_on_exit')
        self.machine.on_exit_incomplete('do_on_exit')

    def set_move_next(self):
        """
        This method initialise move next.
        """
        with self.lock:
            self.can_move_next = True

    def do_on_exit(self):
        """
        This does on exit.
        """
        self.prev_state = self.state
        self.cur_state = self.state

    def do_on_enter(self):
        """
        This does on enter.
        """
        if self.state == "incomplete":
            self.machine.set_state(self.prev_state)
        else:
            self.cur_state = self.state

    def check_state(self):
        """
        This checks the state of the beer.
        """
        with self.lock:
            if self.can_move_next:
                self.can_move_next = False
                return True

    def has_cooks_ingredients_complete(self):
        """
        This checks if the cook ingredient has completed.
        """
        try:
            if not self.is_allocate:
                tank_name = allocate_tank("hot_brew", self.quantity)
                if tank_name:
                    self.is_allocate = True
                    self.process_tanks.update(
                        {"hot_brew": {"tank_name": tank_name}})
            return self.is_allocate and self.check_state()
        except:
            return False

    def cooks_ingredients_process_complete(self):
        """
        This completes the cook ingredient process.
        """
        self.is_allocate = False

    def has_fermentation_complete(self):
        """
        This checks if the fermentation process has completed.
        """
        try:
            if not self.is_allocate:
                tank_name = allocate_tank("fermentation",
                                          self.quantity)
                if tank_name:
                    self.is_allocate = True
                    self.process_tanks.update(
                        {"fermentation": {"tank_name": tank_name}})
            return self.is_allocate and self.check_state()
        except:
            return False

    def fermentation_process_complete(self):
        """
        This completes the fermentation process.
        """
        self.is_allocate = False
        release_tank(self.process_tanks["fermentation"]["tank_name"])

    def has_conditioning_and_carbonation_complete(self):
        """
        This checks if the conditioning and carbonation process has
         completed.
        """
        try:
            if not self.is_allocate:
                tank_name = allocate_tank("conditioning",
                                          self.quantity)
                if tank_name:
                    self.is_allocate = True
                    self.process_tanks.update(
                        {"conditioning": {"tank_name": tank_name}})
            return self.is_allocate and self.check_state()
        except:
            return False

    def conditioning_and_carbonation_process_complete(self):
        """
        This completes the conditioning and carbonation process.
        """
        self.is_allocate = False
        release_tank(self.process_tanks["conditioning"]["tank_name"])

    def has_bottling_and_labelling_complete(self):
        """
        This checks if the bottling and labelling process has
         completed.
        """
        try:
            if not self.is_allocate:
                tank_name = allocate_tank("bottling", self.quantity)
                if tank_name:
                    self.is_allocate = True
                    self.process_tanks.update(
                        {"bottling": {"tank_name": tank_name}})
            return self.is_allocate and self.check_state()
        except:
            return False

    def bottling_and_labelling_process_complete(self):
        """
        This completes the bottling and labelling process.
        """
        self.is_allocate = False

    def finish_process_complete(self):
        """
        This completes the finish process.
        :return:
        """
        self.process_tanks.update({"finish": {"tank_name": 'Empty'}})
        update_beer_stock(self.bear_name, self.quantity)
