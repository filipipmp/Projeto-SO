class Encomenda:
    def __init__(self):
        [self.id, self.origem, self.destino] = [None]*3
        self.tf, self.tc  = 0, 0
        self.status = 'notInit'
    
    def strEncomenda(self, r = 1):
        if   (self.status == 'notInit'):
            return 'notInit'
        elif (self.status == 'Nao coletado'):
            return(f'(id:{self.id},origem:{self.origem},t0:{int(self.t0*r)},destino:{self.destino},status:{self.status})')
        elif (self.status  == 'Coletado'):
            return(f'(id:{self.id},origem:{self.origem},t0:{int(self.t0*r)},destino:{self.destino},status:{self.status},veiculo:{self.veiculo},tc:{int(self.tc*r)})')
        elif (self.status == 'Entregue'):
            return(f'(id:{self.id},origem:{self.origem},t0:{int(self.t0*r)},destino:{self.destino},tf:{int(self.tf*r)},status:{self.status},veiculo:{self.veiculo},tc:{int(self.tc*r)})')

class Veiculo:
    def __init__(self):
        [self.id, self.ponto_atual, self.capacidade, self.carga] = [None]*4
        self.status = 'notInit'

    def strVeiculo(self):
        if (self.status == 'notInit'):
            return 'notInit'
        return f'(id:{self.id},atual:{self.ponto_atual},carga:{self.carga})'

class Ponto:
    def __init__(self):
        [self.id, self.fila] = [None]*2
        self.status = 'notInit'
    
    def strPonto(self):
        if (self.status == 'notInit'):
            return 'notInit'
        return(f'(id:{self.id},fila:{self.fila})')