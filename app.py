from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    # Leer el archivo Excel
    df = pd.read_excel(file)

    # Crear el polígono con Shapely
    polygon = Polygon(zip(df['X'], df['Y']))

    # Acomodar rectángulos
    rects = acomodar_rectangulos_juntos(polygon)

    # Crear y guardar el gráfico
    fig, ax = plt.subplots()
    x, y = polygon.exterior.xy
    ax.fill(x, y, alpha=0.5, fc='b', label='Polígono')

    for idx, rect in enumerate(rects):
        x, y = rect.exterior.xy
        ax.plot(x, y, label=f'Rectángulo {idx+1}')
    
    ax.legend()
    plt.savefig('output.png')
    return "<img src='output.png'/>"

def acomodar_rectangulos_juntos(polygon):
    # Implementación simplificada para acomodar rectángulos dentro de un polígono
    rects = [box(1, 1, 3, 3), box(1, 4, 3, 6), box(4, 1, 6, 3), box(4, 4, 6, 6)]
    return rects

@app.route('/design_with_api', methods=['POST'])
def design_with_api():
    api_key = "LA_API_KEY_DEBERIA_DE_ESTAR_AQUI_PERO_SE_NOS_ACABARON_LOS_CREDITOS"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    prompt = """
    1. Cargar el Archivo Excel: Utilicé pandas para cargar el archivo Excel proporcionado, y leí los datos de las coordenadas de la figura poligonal desde la hoja especificada.
    2. Crear un Objeto Polígono con Shapely: Basado en las coordenadas X e Y proporcionadas, creé un objeto polígono utilizando la librería Shapely para representar la figura poligonal.
    3. Definir la Función para Acomodar Rectángulos: Implementé una función, acomodar_rectangulos_juntos, que intenta colocar 4 rectángulos (4 de largo x 3 de ancho) dentro del polígono. La función itera a través de posiciones, comenzando en el vértice inferior izquierdo del polígono, avanzando en incrementos definidos por las dimensiones del rectángulo. Etiqueta el primero como: Habitación, el segundo como: Baño, el tercero como: Sala, el cuarto como: Cocina.
    4. Graficar la Figura Poligonal y los Rectángulos Acomodados: Usé Matplotlib para crear una visualización de la figura poligonal y los rectángulos acomodados, rellenando la figura poligonal con un color para diferenciarla y delineando cada rectángulo con un color distinto.
    """
    data = {
        'model': 'gpt-4',
        'prompt': prompt,
        'max_tokens': 500
    }

    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    if response.status_code == 200:
        return jsonify(response.json()['choices'][0]['text'])
    else:
        return jsonify({'error': 'No se pudo obtener respuesta de la API de OpenAI'}), 500

if __name__ == '__main__':
    app.run(debug=True)
