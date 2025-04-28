# Versão 3 para modificar led via VM

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
import json
from datetime import datetime
import pytz
import time # Necessário para o exemplo ESP32, mas NÃO usado para delay no Dash

# --- Constantes ---
IP_ADDRESS = "130.131.16.56"
PORT_STH = 8666
PORT_ORION = 1026
DASH_HOST = "0.0.0.0"
ENTITY_ID = "urn:ngsi-ld:NEXUScode:001"
FIWARE_SERVICE = 'smart'
FIWARE_SERVICEPATH = '/'
ORION_URL = f"http://{IP_ADDRESS}:{PORT_ORION}/v2/entities/{ENTITY_ID}/attrs"

# --- Limiares ---
TEMP_THRESHOLD_HIGH = 28.0
HUM_THRESHOLD_HIGH = 65.0
LUM_THRESHOLD_LOW = 150.0

# --- Variável Global para Controle de Estado (Opcional, mas recomendado) ---
# Armazena o último comando enviado para o LED ('on', 'off', ou None inicial)
last_led_command_sent = None
# -------------------------------------------------------------------------

# --- Funções de busca de dados (sem alterações significativas, apenas as melhorias anteriores) ---
def get_luminosity_data(lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/{ENTITY_ID}/attributes/luminosity?lastN={lastN}"
    headers = {'fiware-service': FIWARE_SERVICE, 'fiware-servicepath': FIWARE_SERVICEPATH}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return values
    except requests.exceptions.RequestException as e:
        print(f"Error accessing luminosity API: {e}")
        return []
    except (KeyError, IndexError, TypeError) as e: # Adicionado TypeError
        print(f"Error parsing luminosity data: {e} - Data: {data if 'data' in locals() else 'N/A'}")
        return []

def get_humidity_data(lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/{ENTITY_ID}/attributes/humidity?lastN={lastN}"
    headers = {'fiware-service': FIWARE_SERVICE, 'fiware-servicepath': FIWARE_SERVICEPATH}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return values
    except requests.exceptions.RequestException as e:
        print(f"Error accessing humidity API: {e}")
        return []
    except (KeyError, IndexError, TypeError) as e: # Adicionado TypeError
        print(f"Error parsing humidity data: {e} - Data: {data if 'data' in locals() else 'N/A'}")
        return []

def get_temperature_data(lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/{ENTITY_ID}/attributes/temperature?lastN={lastN}"
    headers = {'fiware-service': FIWARE_SERVICE, 'fiware-servicepath': FIWARE_SERVICEPATH}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return values
    except requests.exceptions.RequestException as e:
        print(f"Error accessing temperature API: {e}")
        return []
    except (KeyError, IndexError, TypeError) as e: # Adicionado TypeError
        print(f"Error parsing temperature data: {e} - Data: {data if 'data' in locals() else 'N/A'}")
        return []


# --- Função de Controle do LED MODIFICADA ---
def control_led(command):
    """
    Sends a command ('on' or 'off') to the FIWARE Orion Context Broker.
    The ESP32 is responsible for interpreting these commands.
    """
    global last_led_command_sent # Acessa a variável global para ler e escrever

    # Define o comando que *deveria* ser enviado com base na lógica atual
    target_command = command

    # Verifica se o comando desejado é diferente do último enviado
    if target_command == last_led_command_sent:
        # print(f"LED state unchanged ({target_command}). No command sent.")
        return # Sai da função se o estado não mudou

    # Se o estado mudou, procede com o envio
    if target_command not in ["on", "off"]: # Comandos válidos agora são 'on' e 'off'
        print(f"Invalid command intended: {target_command}. Must be 'on' or 'off'.")
        return

    payload = json.dumps({
        target_command: {   # Usa o nome do comando ('on' ou 'off') como chave
            "type": "command",
            "value": ""     # Valor geralmente vazio para comandos simples
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'fiware-service': FIWARE_SERVICE,
        'fiware-servicepath': FIWARE_SERVICEPATH
    }

    try:
        response = requests.request("PATCH", ORION_URL, headers=headers, data=payload, timeout=5)
        response.raise_for_status()
        print(f"Successfully sent command '{target_command}' to {ENTITY_ID}. Response: {response.status_code}")
        last_led_command_sent = target_command # ATUALIZA o último comando enviado SÓ SE foi sucesso
    except requests.exceptions.RequestException as e:
        print(f"Error sending command '{target_command}' to {ORION_URL}: {e}")
        # Não atualiza last_led_command_sent se falhar, para tentar novamente na próxima vez

# --- Função de conversão de tempo (sem alterações) ---
def convert_to_sao_paulo_time(timestamps):
    utc = pytz.utc
    sao_paulo = pytz.timezone('America/Sao_Paulo')
    converted_timestamps = []
    for timestamp_str in timestamps:
        dt_naive = None
        try:
            dt_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                dt_naive = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError as e:
                print(f"Error parsing timestamp: {timestamp_str} - {e}")
                continue
        if dt_naive:
            dt_utc = utc.localize(dt_naive)
            dt_sao_paulo = dt_utc.astimezone(sao_paulo)
            converted_timestamps.append(dt_sao_paulo)
    return converted_timestamps


# --- Configuração do App Dash e Layout (sem alterações) ---
fetch_count = 1
history_count = 20 # Aumentado um pouco para melhor visualização

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Sensor Data Viewer'),
    dcc.Graph(id='luminosity-graph'),
    dcc.Graph(id='humidity-graph'),
    dcc.Graph(id='temperature-graph'),
    dcc.Store(id='luminosity-data-store', data={'timestamps': [], 'luminosity_values': []}),
    dcc.Store(id='humidity-data-store', data={'timestamps': [], 'humidity_values': []}),
    dcc.Store(id='temperature-data-store', data={'timestamps': [], 'temperature_values': []}),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

# --- Callback de Atualização de Dados e Controle ---
@app.callback(
    Output('luminosity-data-store', 'data'),
    Output('humidity-data-store', 'data'),
    Output('temperature-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('luminosity-data-store', 'data'),
    State('humidity-data-store', 'data'),
    State('temperature-data-store', 'data')
)
def update_data_store(n, luminosity_hist, humidity_hist, temperature_hist):
    latest_temp = None
    latest_hum = None
    latest_lum = None

    # Get luminosity data
    data_luminosity = get_luminosity_data(fetch_count)
    if data_luminosity:
        try:
            latest_lum = float(data_luminosity[0]['attrValue'])
            luminosity_values = [float(entry['attrValue']) for entry in data_luminosity]
            timestamps_str = [entry['recvTime'] for entry in data_luminosity]
            timestamps = convert_to_sao_paulo_time(timestamps_str)
            luminosity_hist['timestamps'].extend(timestamps)
            luminosity_hist['luminosity_values'].extend(luminosity_values)
            luminosity_hist['timestamps'] = luminosity_hist['timestamps'][-history_count:]
            luminosity_hist['luminosity_values'] = luminosity_hist['luminosity_values'][-history_count:]
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error processing luminosity data point: {e}")


    # Get humidity data
    data_humidity = get_humidity_data(fetch_count)
    if data_humidity:
        try:
            latest_hum = float(data_humidity[0]['attrValue'])
            humidity_values = [float(entry['attrValue']) for entry in data_humidity]
            timestamps_str = [entry['recvTime'] for entry in data_humidity]
            timestamps = convert_to_sao_paulo_time(timestamps_str)
            humidity_hist['timestamps'].extend(timestamps)
            humidity_hist['humidity_values'].extend(humidity_values)
            humidity_hist['timestamps'] = humidity_hist['timestamps'][-history_count:]
            humidity_hist['humidity_values'] = humidity_hist['humidity_values'][-history_count:]
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error processing humidity data point: {e}")

    # Get temperature data
    data_temperature = get_temperature_data(fetch_count)
    if data_temperature:
        try:
            latest_temp = float(data_temperature[0]['attrValue'])
            temperature_values = [float(entry['attrValue']) for entry in data_temperature]
            timestamps_str = [entry['recvTime'] for entry in data_temperature]
            timestamps = convert_to_sao_paulo_time(timestamps_str)
            temperature_hist['timestamps'].extend(timestamps)
            temperature_hist['temperature_values'].extend(temperature_values)
            temperature_hist['timestamps'] = temperature_hist['timestamps'][-history_count:]
            temperature_hist['temperature_values'] = temperature_hist['temperature_values'][-history_count:]
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error processing temperature data point: {e}")


    # --- LÓGICA DE CONTROLE DO LED MODIFICADA ---
    if latest_temp is not None or latest_hum is not None or latest_lum is not None:
        # Condição para LIGAR o LED (lógica OR)
        should_turn_on = False
        if latest_temp is not None and latest_temp > TEMP_THRESHOLD_HIGH:
            print(f"Condition met: Temperature {latest_temp:.1f}°C > {TEMP_THRESHOLD_HIGH}°C")
            should_turn_on = True
        if latest_hum is not None and latest_hum > HUM_THRESHOLD_HIGH:
            print(f"Condition met: Humidity {latest_hum:.1f}% > {HUM_THRESHOLD_HIGH}%")
            should_turn_on = True
        if latest_lum is not None and latest_lum < LUM_THRESHOLD_LOW:
            print(f"Condition met: Luminosity {latest_lum:.1f} < {LUM_THRESHOLD_LOW}")
            should_turn_on = True

        # Determina o comando alvo ('on' ou 'off')
        target_command = "on" if should_turn_on else "off"

        # Chama a função control_led com o comando correto
        control_led(target_command)

    else:
        # Se não houver dados recentes, tentamos desligar por segurança.
        print("No recent sensor data. Attempting to send 'off' command.")
        control_led("off")
    # ---------------------------------

    return luminosity_hist, humidity_hist, temperature_hist

# --- Callback de atualização do gráfico (sem alterações) ---
@app.callback(
    Output('luminosity-graph', 'figure'),
    Output('humidity-graph', 'figure'),
    Output('temperature-graph', 'figure'),
    Input('luminosity-data-store', 'data'),
    Input('humidity-data-store', 'data'),
    Input('temperature-data-store', 'data')
)
def update_graph(luminosity_data, humidity_data, temperature_data):
    # Luminosity graph
    if luminosity_data.get('timestamps') and luminosity_data.get('luminosity_values'):
        trace_luminosity = go.Scatter(x=luminosity_data['timestamps'], y=luminosity_data['luminosity_values'], mode='lines+markers', name='Luminosity', line=dict(color='orange'))
        fig_luminosity = go.Figure(data=[trace_luminosity]).update_layout(title='Luminosity Over Time', xaxis_title='Timestamp (São Paulo Time)', yaxis_title='Luminosity', hovermode='closest')
    else:
        fig_luminosity = go.Figure().update_layout(title='Luminosity Over Time (No data)')

    # Humidity graph
    if humidity_data.get('timestamps') and humidity_data.get('humidity_values'):
        trace_humidity = go.Scatter(x=humidity_data['timestamps'], y=humidity_data['humidity_values'], mode='lines+markers', name='Humidity', line=dict(color='blue'))
        fig_humidity = go.Figure(data=[trace_humidity]).update_layout(title='Humidity Over Time', xaxis_title='Timestamp (São Paulo Time)', yaxis_title='Humidity (%)', hovermode='closest')
    else:
        fig_humidity = go.Figure().update_layout(title='Humidity Over Time (No data)')

    # Temperature graph
    if temperature_data.get('timestamps') and temperature_data.get('temperature_values'):
        trace_temperature = go.Scatter(x=temperature_data['timestamps'], y=temperature_data['temperature_values'], mode='lines+markers', name='Temperature', line=dict(color='red'))
        fig_temperature = go.Figure(data=[trace_temperature]).update_layout(title='Temperature Over Time', xaxis_title='Timestamp (São Paulo Time)', yaxis_title='Temperature (°C)', hovermode='closest')
    else:
        fig_temperature = go.Figure().update_layout(title='Temperature Over Time (No data)')

    return fig_luminosity, fig_humidity, fig_temperature

# --- Execução do App ---
if __name__ == '__main__':
    app.run(debug=True, host=DASH_HOST, port=8050)