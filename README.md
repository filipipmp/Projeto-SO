# Simulador

Funcionamento baseado em operações atômicas gerenciadas com mutex:

## Thread de Encomenda
* Inicializa a encomenda
* Registra os tempos de inserção, coleta e entrega ao perceber mudança de status
* Ao final, cria um arquivo txt com as informações do rastreio

## Veículos
* Inicializa o veículo
* Enquanto houver encomendas não entregues no sistema:
  * Entra na fila do ponto de distribuição atual
  * Espera o ponto de distribuição processar todas as encomendas que serão entregues nele
  * Espera o ponto carregar as encomendas no veículo
  * Ao perceber mudança de status, o veículo parte para o próximo ponto

## Ponto de distribuição
* Inicializa o ponto de distribuição
* Enquanto houver encomendas não entregues no sistema:
  * Enquanto houver veículos na fila:
    *  Descarrega todas as encomendas com destino nesse ponto do primeiro carro
    *  Carrega o primeiro carro o máximo possível com encomendas do ponto, atualiza o status das encomendas carregadas e libera o veículo
* Ao final, expulsa todos os carros da fila do ponto e os libera
