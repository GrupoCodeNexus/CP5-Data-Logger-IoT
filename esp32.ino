// Autor: Fábio Henrique Cabrini 
// Resumo: Esse programa possibilita ligar e desligar o LED onboard, além de mandar o status para o Broker MQTT,
// permitindo ao Helix saber se o LED está ligado ou desligado.
 
// Revisões:
// Rev1: 26-08-2023 Código portado para o ESP32 e para realizar a leitura de luminosidade e publicar o valor em um tópico apropriado do broker.
// Autor Rev1: Lucas Demetrius Augusto
// Rev2: 28-08-2023 Ajustes para o funcionamento no FIWARE Descomplicado.
// Autor Rev2: Fábio Henrique Cabrini
// Rev3: 1-11-2023 Refinamento do código e ajustes para o funcionamento no FIWARE Descomplicado.
// Autor Rev3: Fábio Henrique Cabrini
// Alteração: 05-03-2025 Alterações de entidades e de IP para conectar a uma máquina virtual privada.
// Autor alteração: Kayque Carvalho
 
#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"
 
// Configurações - variáveis editáveis
const char* default_SSID = "RAFAELA-2.4G";        // Nome da rede Wi-Fi
const char* default_PASSWORD = "carvalho63";               // Senha da rede Wi-Fi
const char* default_BROKER_MQTT = "130.131.16.56"; // IP da máquina virtual Broker MQTT
const int default_BROKER_PORT = 1883;             // Porta do Broker MQTT
const char* default_TOPICO_SUBSCRIBE = "/TEF/NEXUScode/cmd"; // Tópico MQTT de escuta
const char* default_TOPICO_PUBLISH_1 = "/TEF/NEXUScode/attrs"; // Tópico MQTT de envio de informações para Broker
const char* default_TOPICO_PUBLISH_2 = "/TEF/NEXUScode/attrs/l"; // Tópico MQTT de envio de luminosidade

const char* default_TOPICO_PUBLISH_3 = "/TEF/NEXUScode/attrs/h"; // MQTT de envio de humidade
const char* default_TOPICO_PUBLISH_4 = "/TEF/NEXUScode/attrs/t";  // MQTT de envio de temperatura

const char* default_ID_MQTT = "fiware_code";    // ID MQTT
const int default_D4 = 2;                        // Pino do LED onboard
 
// Declaração da variável para o prefixo do tópico
const char* topicPrefix = "NEXUScode";
const int DHT_PIN = 15;                           // Pino do DHT
 
// Variáveis para configurações editáveis
const char* SSID = default_SSID;
const char* PASSWORD = default_PASSWORD;
const char* BROKER_MQTT = default_BROKER_MQTT;
int BROKER_PORT = default_BROKER_PORT;
const char* TOPICO_SUBSCRIBE = default_TOPICO_SUBSCRIBE;
const char* TOPICO_PUBLISH_1 = default_TOPICO_PUBLISH_1;
const char* TOPICO_PUBLISH_2 = default_TOPICO_PUBLISH_2;
const char* TOPICO_PUBLISH_3 = default_TOPICO_PUBLISH_3;    // Para humidade
const char* TOPICO_PUBLISH_4 = default_TOPICO_PUBLISH_4;    // Para a temperatura


const char* ID_MQTT = default_ID_MQTT;
int D4 = default_D4;
 
WiFiClient espClient;
PubSubClient MQTT(espClient);
char EstadoSaida = '0';
DHTesp dhtSensor;
 
// Função para inicializar a serial
void initSerial() {
    Serial.begin(115200);
    dhtSensor.setup(DHT_PIN, DHTesp::DHT11);
}
 
// Função para inicializar a conexão Wi-Fi
void initWiFi() {
    delay(10);
    Serial.println("------ Conexao WI-FI ------");
    Serial.print("Conectando-se na rede: ");
    Serial.println(SSID);
    Serial.println("Aguarde");
    reconectWiFi();
}
 
// Função para inicializar o MQTT
void initMQTT() {
    MQTT.setServer(BROKER_MQTT, BROKER_PORT);
    MQTT.setCallback(mqtt_callback);
}
 
// Função de setup
void setup() {
    InitOutput();
    initSerial();
    initWiFi();
    initMQTT();
    delay(5000);
    MQTT.publish(TOPICO_PUBLISH_1, "s|on"); // Envia status inicial
}
 
// Função loop
void loop() {
    VerificaConexoesWiFIEMQTT();
    EnviaEstadoOutputMQTT();
    handleLuminosity();
    handleHumidity();
    handleTemperature();
    MQTT.loop();
    
    Serial.println("---");
    
    delay(2000); // Espera para a próxima leitura
}
 
// Função de reconexão Wi-Fi
void reconectWiFi() {
    if (WiFi.status() == WL_CONNECTED) return;
    
    WiFi.begin(SSID, PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(100);
        Serial.print(".");
    }
    
    Serial.println();
    Serial.println("Conectado com sucesso na rede ");
    Serial.print(SSID);
    Serial.println("IP obtido: ");
    Serial.println(WiFi.localIP());
    
    // Garantir que o LED inicie desligado
    digitalWrite(D4, LOW);
}
 
// Função callback do MQTT
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (int i = 0; i < length; i++) {
        char c = (char)payload[i];
        msg += c;
    }
    Serial.print("- Mensagem recebida: ");
    Serial.println(msg);
    
    // Forma o padrão de tópico para comparação
    String onTopic = String(topicPrefix) + "@on|";
    String offTopic = String(topicPrefix) + "@off|";
    
    // Compara com o tópico recebido
    if (msg.equals(onTopic)) {
        digitalWrite(D4, HIGH);
        EstadoSaida = '1';
    }
    
    if (msg.equals(offTopic)) {
        digitalWrite(D4, LOW);
        EstadoSaida = '0';
    }
}
 
// Função para verificar conexões Wi-Fi e MQTT
void VerificaConexoesWiFIEMQTT() {
    if (!MQTT.connected()) reconnectMQTT();
    reconectWiFi();
}
 
// Função para enviar o estado do LED para o Broker
void EnviaEstadoOutputMQTT() {
    if (EstadoSaida == '1') {
        MQTT.publish(TOPICO_PUBLISH_1, "s|on");
        Serial.println("- Led Ligado");
    }
    if (EstadoSaida == '0') {
        MQTT.publish(TOPICO_PUBLISH_1, "s|off");
        Serial.println("- Led Desligado");
    }
    
    Serial.println("- Estado do LED onboard enviado ao broker!");
    delay(1000);
}
 
// Função para inicializar o pino do LED
void InitOutput() {
    pinMode(D4, OUTPUT);
    digitalWrite(D4, HIGH); // Inicializa o LED desligado
    
    boolean toggle = false;
    for (int i = 0; i <= 10; i++) {
        toggle = !toggle;
        digitalWrite(D4, toggle);
        delay(200);
    }
}
 
// Função de reconexão MQTT
void reconnectMQTT() {
    while (!MQTT.connected()) {
        Serial.print("* Tentando se conectar ao Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        
        if (MQTT.connect(ID_MQTT)) {
            Serial.println("Conectado com sucesso ao broker MQTT!");
            MQTT.subscribe(TOPICO_SUBSCRIBE);
        } else {
            Serial.println("Falha ao reconectar no broker.");
            Serial.println("Haverá nova tentativa de conexão em 2s");
            delay(2000);
        }
    }
}
 
// Função para ler e publicar a luminosidade
void handleLuminosity() {
    const int potPin = 34;
    int sensorValue = analogRead(potPin);
    int luminosity = map(sensorValue, 0, 4095, 0, 100);
    String mensagem = String(luminosity);
    
    Serial.print("Valor da luminosidade: ");
    Serial.println(mensagem.c_str());
    MQTT.publish(TOPICO_PUBLISH_2, mensagem.c_str());

    // Verifica se a luminosidade é menor que 1000
    if (luminosity < 40) {
        verificarCondicoes();
    }
}

// Função para ler e publicar a humidade
void handleHumidity() {
    TempAndHumidity data = dhtSensor.getTempAndHumidity();
    String mensagem = String(data.humidity);        // Cria string de umidade

    Serial.print("Valor da umidade: ");
    Serial.print(mensagem.c_str()); 
    Serial.println("%");
    MQTT.publish(TOPICO_PUBLISH_3, mensagem.c_str());

    // Verifica se a umidade é maior que 30
    if (data.humidity > 70) {
        verificarCondicoes();
    }
}

// Função para ler e publicar a temperatura
void handleTemperature() {
    TempAndHumidity data = dhtSensor.getTempAndHumidity();
    String mensagem = String(data.temperature);

    Serial.print("Valor da temperatura: ");
    Serial.print(mensagem.c_str());
    Serial.println("°C");
    MQTT.publish(TOPICO_PUBLISH_4, mensagem.c_str());

    // Verifica se a temperatura é maior que 30
    if (data.temperature > 30) {
        verificarCondicoes();
    }
}

// Função para verificar as condições e controlar o LED
void verificarCondicoes() {
    TempAndHumidity data = dhtSensor.getTempAndHumidity();
    const int potPin = 34;
    int sensorValue = analogRead(potPin);
    int luminosity = map(sensorValue, 0, 4095, 0, 100);

    // Verifica se as condições para ligar o LED são atendidas
    if (data.temperature > 32 or data.humidity > 88 or luminosity < 25) {
        // Faz o LED piscar
        for (int i = 0; i < 10; i++) {
            digitalWrite(D4, HIGH);  // Liga o LED
            delay(500);               // Espera meio segundo
            digitalWrite(D4, LOW);   // Desliga o LED
            delay(500);               // Espera meio segundo
        }
        EstadoSaida = '1';   // Define o estado do LED
    } else {
        digitalWrite(D4, LOW); // Desliga o LED
        EstadoSaida = '0';
        Serial.println("- LED desligado. Condições não atendidas.");
    }
}
