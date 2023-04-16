
class RunningBotSingle:

    __instance = None

    @staticmethod
    def get_instance():
        if RunningBotSingle.__instance is None:
            RunningBotSingle()
        return RunningBotSingle.__instance

    def __init__(self):
        if RunningBotSingle.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            RunningBotSingle.__instance = self
        self.current_bot = None
        self.bot = None

    def set_current_game_bot(self, bot):
        self.current_bot = bot

    def get_current_game_bot(self):
        return self.current_bot

    def get_current_bot(self):
        return self.bot

    def set_current_bot(self, bot):
        self.bot = bot