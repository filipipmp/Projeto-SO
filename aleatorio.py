import random

class Aleatorio:
    def TempoViagem(self, razao_min_seg):
        return random.randint(5,10) / float(razao_min_seg)
    
    def TempoDescarregar(self, razao_min_seg):
        return random.randint(2,4) / float(razao_min_seg)