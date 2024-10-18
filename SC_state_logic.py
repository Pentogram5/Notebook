from SC_utils import *

class State:
    # states = {1: 'start',
    #           2: 'chooseObject',
    #           3: 'takePL',
    #           4: 'takePL_far',
    #           5: 'takePH',
    #           6: 'THROW_TO_BASKET',
    #           7: 'goToBase'}
    NONE = -1
    START = 0
    CHOOSE_OBJECT = 1
    TAKE_PL_CLOSE = 2
    TAKE_PL_FAR = 3
    TAKE_PH = 4
    THROW_TO_BASKET = 5
    GOTOBASE = 6
    DEACTIVATE = 7


    currentState = 1
    def __init__(self):
        self.currentState = 1
        self.id = State.NONE
    def on_enter(self):
        ...
    def on_exit(self):
        ...
    def update(self):
        # Вызывается каждую итерацию цикла обработки состояния
        ...
    def update_logic_to_other(self): # ->str[State]
        # Проверяет условия перехода на другие состояния и переходит по необходимоси
        ...
    def update_logic_to_myself(self)->bool:
        # Проверяет глобальные условия и возвращает True, если на это состояние сейчас нужно перейти
        ...

class Start(State):
    def update_logic_to_other(self):
        return State.START

def the_first_time_choose():
    #Функция проверки впервые выбираем объект
    ...
class ChooseObject(State):
    
    def update_logic_to_other(self):
        if nothing_remain_check():
            return State.GOTOBASE
        elif the_first_time_choose():
            return State.TAKE_PL_CLOSE
        elif not(the_first_time_choose()):
            ...#оценка стоимости остаточных призов
            return get_remain_valuable_object_state()
        else:
            return State.CHOOSE_OBJECT
def nothing_remain_check():
    # Функция проверки того, что ни одного объекта не осталось на поле
    ...

class TakePH(State):
    def update_logic_to_other(self):
        if robot_is_holding():
            return State.THROW_TO_BASKET
        else: 
            return State.TAKE_PH

class TakePL_close(State):
    #
    def update_logic_to_other(self):
        if robot_is_holding():
            return State.THROW_TO_BASKET
        if enemy_is_catching_PL() and not robot_is_holding():
            return State.TAKE_PH
        # if in_state_choose():
        #     if robot_can_catch():
        #         if triger_enemy_take_PL():
        #             return State.TAKE_PH
        #         else:
        #             return State.TAKE_PL

def enemy_is_catching_PL():
    #Функция проверки идет ли соперник за ближайшем объектом
    ...
def robot_is_holding():
    #Проверка взял ли наш робот что-то
    ...
class TakePL_far(State):
    def update_logic_to_other(self):
        if robot_is_holding():
            return State.THROW_TO_BASKET
        if enemy_is_catching_PL() and not robot_is_holding():
            return State.TAKE_PH

class ThrowToBasket(State):    
    def update_logic_to_other(self):
        if not robot_is_holding():
            return State.CHOOSE_OBJECT    

def robot_on_the_base():
    #Находится ли робот на базе?
    ...
class GoToBase(State):
    def update_logic_to_other(self):
        if robot_on_the_base():
            return State.DEACTIVATE

class StateUpdater:
    def __init__(self, states, start_state_index=0):
        self.states = states
        self.start_state = states[start_state_index]
        # self.end_state
        self.current_state = self.start_state
    def update(self):
        # Не даёт гарантии однозначности результата. Однозначность результата определяется самой логикой
        for state in self.states:
            go_to_this_state = state.update_logic_to_myself()
            if go_to_this_state:
                self.current_state = state
        new_state = self.current_state.update_logic_to_other()
        if new_state is not None:
            self.current_state = new_state
        
        self.current_state.update()
    

def main():
    tr = ThreadRate(30)
    states = ...
    
    state_updater = StateUpdater(states, start_state_index=0)
    while True:
        state_updater.update()
        tr.sleep()
    
if __name__=='__main__':
    main()
                
        
