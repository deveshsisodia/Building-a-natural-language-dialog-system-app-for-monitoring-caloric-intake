from DialogManager import DialogManager
from DialogTracer import DialogTracer


class MainInterface:
    def __init__(self):
        self.dialog_tracer_obj = DialogTracer(True)
        print("\n****************************************")
        print("*******Speech Based Dialog System*******")
        print("****************************************\n")
        self._initialize_dialog_manager()
        self.user_name = ''
        self.food_items_tokens = ''
        self.final_usda_food_items = ''

    # Loading Data Base
    def _initialize_dialog_manager(self):
        self.dialog_manager_obj = DialogManager(complete_db_overhaul=False)

    # Evaluating Calorific Intake of user based on food items eaten by him
    def execute_dialog(self):
        self.user_name = self.dialog_manager_obj.get_user_name_from_user()
        self.food_items_tokens = self.dialog_manager_obj.get_food_items_tokens_from_user(self.user_name)
        # self.food_items_tokens = ['chicken','burger']
        self.final_usda_food_items = self.dialog_manager_obj.get_all_usda_food_items_from_user(self.food_items_tokens)
        self.dialog_manager_obj.show_food_items_with_calories(self.final_usda_food_items)

if __name__ == '__main__':
    interface_obj = MainInterface()
    interface_obj.execute_dialog()
