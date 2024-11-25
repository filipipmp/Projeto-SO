import threading
import random
import time

from aleatorio import Aleatorio
from estruturas import Ponto, Veiculo, Encomenda

# TODO: lembrar de gerar os arquivos de rastreio depois de finalizar a simulação

# ================================================= VARIAVEIS GLOBAIS =================================================
mutex = threading.Lock()

def dormir(t = 1e-6):
    time.sleep(t)

rand = Aleatorio()  # Gera tempos aleatórios para as situações descritas (em minutos reais)
S, C, P, A = None, None, None, None
Pontos, Veiculos, Encomendas = None, None, None  # Arrays globais com as informações de cada entidade
t0 = None
min_em_seg_simul = None # Usado para converter minutos reais para segundos de simulação
# =========================================== FUNÇÕES PARA CONSULTA INTERNA ===========================================
def todas_encomendas_entregues():
    global Encomendas
    for encomenda in Encomendas:
        if (encomenda.status != 'Entregue'):
            return False
    return True

def id_carga_a_coletar(id_veiculo, id_ponto):
    global Veiculos
    for id_encomenda in Veiculos[id_veiculo].carga:
        if (Encomendas[id_encomenda].destino == id_ponto):
            return id_encomenda
    return -1

def id_encomenda_a_carregar(id_ponto):
    global Encomendas
    for encomenda in Encomendas:
        if (encomenda.origem == id_ponto and encomenda.status == 'Nao coletado'):
            return encomenda.id
    return -1
# ================================================= FUNÇÕES DE THREAD =================================================
def Ponto_thread(id):
    global Pontos, Veiculos, Encomendas, t0, min_em_seg_simul

    # Inicializa o Ponto respectivo no array global
    mutex.acquire()
    Pontos[id].id = id
    Pontos[id].fila = []
    Pontos[id].status = 'Init'
    mutex.release()
    dormir()
    mutex.acquire()
    # Loop principal (enquando houver encomendas ainda não entregues)
    while (not todas_encomendas_entregues()):
        # Enquanto houver carros na fila, atende
        while (len(Pontos[id].fila)):
            # Primeiro coleta todas as entregas do primeiro da fila com destino nesse posto
            id_encomenda = id_carga_a_coletar(Pontos[id].fila[0], id)
            while(id_encomenda != -1):
                time.sleep(rand.TempoDescarregar(min_em_seg_simul))
                Veiculos[Pontos[id].fila[0]].carga.remove(id_encomenda)
                Encomendas[id_encomenda].status = 'Entregue'
                mutex.release()
                dormir()
                mutex.acquire()
                id_encomenda = id_carga_a_coletar(Pontos[id].fila[0], id)
            
            # Depois, carrega encomendas no primeiro veículo da fila (se tiver espaço)
            id_encomenda = id_encomenda_a_carregar(id)
            while(id_encomenda != -1 and len(Veiculos[Pontos[id].fila[0]].carga) < A):
                Veiculos[Pontos[id].fila[0]].carga.append(id_encomenda)
                Encomendas[id_encomenda].veiculo = Pontos[id].fila[0]
                Encomendas[id_encomenda].status = 'Coletado'
                mutex.release()
                dormir()
                mutex.acquire()
                id_encomenda = id_encomenda_a_carregar(id)
            Veiculos[Pontos[id].fila[0]].status = 'Disponivel'
            Pontos[id].fila.pop(0)
            mutex.release()
            dormir()
            mutex.acquire()
        mutex.release()
        dormir()
        mutex.acquire()
    for id_v in Pontos[id].fila:
        Veiculos[id_v].status = 'Disponivel'
    mutex.release()

def Veiculo_thread(id, origem):
    global Pontos, Veiculos, Encomendas, t0, min_em_seg_simul, A

    # Inicializa o Veículo respectivo no array global
    mutex.acquire()
    Veiculos[id].id     = id
    Veiculos[id].ponto_atual = origem
    Veiculos[id].capacidade = A
    Veiculos[id].carga = []
    Veiculos[id].status = 'Disponivel'
    mutex.release()
    dormir()
    mutex.acquire()
    # Loop principal (break quando não houver encomendas a entregar)
    while (not todas_encomendas_entregues()):
        # Espera para entrar na fila do posto atual
        Pontos[Veiculos[id].ponto_atual].fila.append(id)
        Veiculos[id].status = 'Em espera'
        mutex.release()
        dormir()
        mutex.acquire()
        # Espera até ser atendido
        while (Veiculos[id].status != 'Disponivel'):
            mutex.release()
            dormir()
            mutex.acquire()

        # Viaja para o próximo ponto
        mutex.release()
        time.sleep(rand.TempoViagem(min_em_seg_simul))
        mutex.acquire()
        Veiculos[id].ponto_atual = (Veiculos[id].ponto_atual + 1)%S
    mutex.release()

def Encomenda_thread(id, info):
    global Pontos, Veiculos, Encomendas, t0, min_em_seg_simul, P

    mutex.acquire()
    Encomendas[id].id = id
    Encomendas[id].origem  = info[0]
    Encomendas[id].destino = info[1]
    Encomendas[id].t0 = time.time()-t0
    Encomendas[id].status  = 'Nao coletado'
    mutex.release()
    dormir()
    mutex.acquire()
    while (True):
        # Quando coletado, calcula o tempo da coleta
        if (Encomendas[id].status != 'Nao coletado'):
            Encomendas[id].tc = time.time() - t0
            break
        mutex.release()
        dormir()
        mutex.acquire()
    mutex.release()
    dormir()
    mutex.acquire()
    # Espera até ser entregue
    while (True):
        # Quando entregue, calcula o tempo da entrega
        if (Encomendas[id].status != 'Coletado'):
            Encomendas[id].tf = time.time() - t0
            break
        mutex.release()
        dormir()
        mutex.acquire()
    file = open(f'Rastreios/Rastreio_Encomenda-{id}', 'w')
    file.write(Encomendas[id].strEncomenda())
    file.close()
    mutex.release()

# ===================================================== SIMULAÇÃO =====================================================
def simulacao(l_S=3, l_C=2, l_P=8, l_A=3, l_min_em_seg_simul = 1, print_a_cada  = 1):
    global S, C, P, A, min_em_seg_simul
    S, C, P, A, min_em_seg_simul = l_S, l_C, l_P, l_A, l_min_em_seg_simul

    # Testa condições dasimulação
    if not (S > 1 and C > 0 and P > A and A > C):
        print('Parâmetros SCPA não suportados')
        return

    global Pontos, Veiculos, Encomendas, t0
    Pontos     = [Ponto()     for i in range(0, S)]
    Veiculos   = [Veiculo()   for i in range(0, C)]
    Encomendas = [Encomenda() for i in range(0, P)]

    # Inicialização das threads
    threads_Pontos     = [threading.Thread(target=Ponto_thread,     args=(i,)) for i in range(0, S)]
    threads_Veiculos   = [threading.Thread(target=Veiculo_thread,   args=(i, random.randint(0, S-1))) for i in range(0, C)]
    threads_Encomendas = [threading.Thread(target=Encomenda_thread, args=(i, random.sample([i for i in range(0, S)], 2))) for i in range(0, P)]
    t0 = time.time()

    # Execução das threads
    for thread in threads_Pontos + threads_Veiculos + threads_Encomendas:
        thread.start()

    # Loop para tela de monitoramento
    while(not todas_encomendas_entregues()):
        print_simulacao()
        #print_active_threads(threads_Pontos, threads_Veiculos, threads_Encomendas)
        time.sleep(print_a_cada)
    
    # Join das threads
    for thread in threads_Encomendas + threads_Veiculos + threads_Pontos:
        thread.join()

    # Print final
    print('\n\nSIMULACAO CONCLUIDA\n')
    print_simulacao()

def print_simulacao():
    mutex.acquire()
    global Pontos, Veiculos, Encomendas, t0, min_em_seg_simul
    print(f'\nTEMPO ATUAL: {int((time.time()-t0)*min_em_seg_simul)} min')
    print('  PONTOS:')
    for ponto in Pontos:
        print('    ' + ponto.strPonto())
    print('  VEÍCULOS:')
    for veiculo in Veiculos:
        print('    ' + veiculo.strVeiculo())
    print('  ENCOMENDAS:')
    for encomenda in Encomendas:
        print('    ' + encomenda.strEncomenda(min_em_seg_simul))
    mutex.release()

def print_active_threads(P,V,E):
    print(f'  THREADS ATIVAS')
    for i in range(0, len(P)):
        if (P[i].is_alive()):
            print(f'    Ponto-{i}')
    for i in range(0,len(V)):
        if (P[i].is_alive()):
            print(f'    Veiculo-{i}') 
    for i in range(0,len(E)):
        if (E[i].is_alive()):
            print(f'    Encomenda-{i}')     

if __name__=='__main__':
    simulacao()