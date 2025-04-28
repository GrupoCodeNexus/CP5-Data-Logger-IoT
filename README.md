# CP5 - Data Logger/IoT

Este projeto consiste no desenvolvimento de uma solução de monitoramento para vinherias utilizando Internet das Coisas (IoT). O sistema coleta dados de sensores de luminosidade, umidade e temperatura em tempo real, envia esses dados para a plataforma FIWARE e os disponibiliza para análise através de um dashboard web dinâmico. O objetivo é permitir o acompanhamento das condições ambientais da vinheria de forma remota e histórica.

## Desafio proposto

- **Integração de Hardware:** Adicionar o sensor de temperatura e umidade DHT11 ao ESP32, que já possuía o sensor de luminosidade LDR.
- **Desenvolvimento do Dashboard:** Criar um painel web dinâmico em Python para exibir dados históricos (luminosidade, temperatura, umidade) obtidos da API do FIWARE (STH-Comet, porta 8666).
- **Serviço de Dashboard:** Publicar o dashboard como um serviço web (API em Python na porta 5000) hospedado em um ambiente Linux.
- **Simulação:** Demonstrar o funcionamento completo da solução (sensores enviando dados ao FIWARE) usando o simulador Wokwi.
- **Alerta Visual Remoto:** Fazer o LED azul do ESP32 piscar remotamente quando os valores dos sensores saírem dos limites aceitáveis, até que voltem ao normal.
- **Evidência em Vídeo:** Produzir um vídeo de 3 minutos (time-lapse) mostrando a simulação no Wokwi, o envio de dados para o FIWARE e a visualização no dashboard.
- **Demonstração Prática:** Apresentar a solução funcionando com o hardware físico (ESP32, LDR, DHT11) conectado ao FIWARE e exibindo dados no dashboard.

## Tecnologias utilizadas

**Hardware:**
1. Microcontrolador: **ESP32**
2. Sensores: **DHT11** (temperatura e umidade), **LDR** (luminosidade)
3. Atuador: LED Azul (integrado ao ESP32)

**Máquina Virtual (VM):**
1. Provedor: **Microsoft Azure**
2. Sistema Operacional: **Linux (Ubuntu)**
3. Configuração: **Standard B1s (1 vCPU, 1 GiB de memória)**

**Software/Plataformas:**
1. **FIWARE** (Orion Context Broker, STH-Comet)
2. **Wokwi** (Simulador)
3. **Python** (Para o Dashboard e API)
4. **Arduino IDE** (Para programação do ESP32)
5. **Postman** (Para testes de API)

## Links úteis
Link do wokiwi com a simulação: [clique aqui](https://wokwi.com/projects/429334626804446209) 

Link do vídeo no youtube: [clique aqui](https://youtu.be/MrBl9a0KkMQ)

## Integrantes da equipe:

- [Francisco Vargas](https://github.com/Franciscov25)
- [Kayque Carvalho](https://github.com/Kay-Carv)
- [Matheus Eiki](https://github.com/Matheus-Eiki)
- [Marcelo Affonso](https://github.com/tenebres-cpu)
