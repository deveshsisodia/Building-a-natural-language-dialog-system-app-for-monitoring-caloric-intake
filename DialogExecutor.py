from DialogManager import DialogManager


class MainInterface:
    def __init__(self):
        print("****************************************")
        print("*******Speech Based Dialog System*******")
        print("****************************************\n")
        self._initialize_dialog_manager()
        self.user_name = 'Steven'
        self.food_items_tokens = ''
        self.final_usda_food_items = ''

    def _initialize_dialog_manager(self):
        self.dialog_manager_obj = DialogManager(complete_db_overhaul=False)

    def execute_dialog(self):
        self.user_name = self.dialog_manager_obj.get_user_name_from_user()
        print('Final user_name: {0}'.format(self.user_name))
        self.food_items_tokens = self.dialog_manager_obj.get_food_items_tokens_from_user(self.user_name)
        self.final_usda_food_items = self.dialog_manager_obj.get_all_usda_food_items_from_user(self.food_items_tokens)

if __name__ == '__main__':
    interface_obj = MainInterface()
    interface_obj.execute_dialog()