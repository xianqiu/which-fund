

class FundModel:
    
    def __init__(self, budget:int, num:int):
        self.budget = budget
        self.num = num
        self.result = None

    def process(self):
        pass


class SimpleFundModel(FundModel):
    
    def __init__(self, budget:int, num:int):
        super().__init__(budget, num)

    def process(self):
        pass


