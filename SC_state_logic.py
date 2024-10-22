from SC_utils import *

class State:
    states = {1: 'start',
              2: 'chooseObject',
              3: 'takeNearPrice',
              4: 'takeFarPrice',
              5: 'takeHighPrice',
              6: 'throwToBasket',
              7: 'goToBase'}
    currentState = 1
    def __init__(self):
        self.currentState = 1
    def on_enter(self):
        ...
    def on_exit(self):
        ...
    def update(self):
        # Вызывается каждую итерацию цикла обработки состояния
        ...
    def update_logic_to_other(self): # ->State
        # Проверяет условия перехода на другие состояния и переходит по необходимоси
        ...
    def update_logic_to_myself(self)->bool:
        # Проверяет глобальные условия и возвращает True, если на это состояние сейчас нужно перейти
        ...
        
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
                
        
