from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Diccionario de palabras reservadas y sus tipos
keywords = {
    'int': 'Palabra reservada',
    'for': 'Palabra reservada',
    'if': 'Palabra reservada',
    'else': 'Palabra reservada',
    'while': 'Palabra reservada',
    'return': 'Palabra reservada',
    'public': 'Palabra reservada',
    'class': 'Palabra reservada',
    'static': 'Palabra reservada',
    'void': 'Palabra reservada',
    'System.out.println': 'Palabra reservada'
}

# Análisis Léxico
def lexical_analysis(code):
    result = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        index = 0
        while index < len(line):
            token_detected = False
            for keyword in keywords:
                if line[index:].startswith(keyword) and (index + len(keyword) == len(line) or not line[index + len(keyword)].isalnum()):
                    result.append((line_number, index, keywords[keyword], keyword))
                    index += len(keyword)
                    token_detected = True
                    break
            if token_detected:
                continue

            char = line[index]
            if char in [';', '{', '}', '(', ')', '[', ']']:
                tipo = 'Punto y coma' if char == ';' else 'Llave' if char in ['{', '}'] else 'Paréntesis' if char in ['(', ')'] else 'Corchete'
                result.append((line_number, index, tipo, char))
                index += 1
            elif char.isdigit():
                start = index
                while index < len(line) and line[index].isdigit():
                    index += 1
                result.append((line_number, start, 'Número', line[start:index]))
            elif char.isalpha() or char == '_':
                start = index
                while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                    index += 1
                result.append((line_number, start, 'Identificador', line[start:index]))
            else:
                index += 1
    return result

def syntactic_analysis(code):
    result = []
    lines = code.split('\n')
    open_braces = 0  # Contador para llaves abiertas
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if '{' in stripped_line:
            open_braces += stripped_line.count('{')
        if '}' in stripped_line:
            open_braces -= stripped_line.count('}')
            
        if stripped_line.startswith('public'):
            if ('class' in stripped_line or 'void' in stripped_line) and '{' in stripped_line:
                result.append((line_number, stripped_line, True))
            else:
                result.append((line_number, stripped_line, False))
        elif stripped_line.startswith('System.out.println'):
            if '(' in stripped_line and ')' in stripped_line and stripped_line.endswith(';'):
                result.append((line_number, stripped_line, True))
            else:
                result.append((line_number, stripped_line, False))
        elif stripped_line == '}':
            result.append((line_number, '}', True))  # Verificar contexto si es necesario

    # Verificar si faltan llaves al finalizar el análisis
    if open_braces != 0:
        result.append(('Final', 'Desequilibrio de llaves', False))

    return result

def semantic_analysis(code):
    result = []
    lines = code.split('\n')
    for line_number, line in enumerate(lines, start=1):
        if 'public' in line:
            if 'class' in line or 'void' in line:
                result.append((line_number, line.strip(), True))
            else:
                result.append((line_number, line.strip(), False))
        elif 'System.out.println' in line:
            if '(' in line and ')' in line and ';' in line:
                result.append((line_number, line.strip(), True))
            else:
                result.append((line_number, line.strip(), False))
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    code = ""
    lexical_result = []
    syntactic_result = []
    semantic_result = []
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                code = f.read()
        elif 'code' in request.form and request.form['code'].strip() != '':
            code = request.form['code']
        else:
            return "No file selected or code provided"
        
        lexical_result = lexical_analysis(code)
        syntactic_result = syntactic_analysis(code)
        semantic_result = semantic_analysis(code)
        
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @keyframes neon {
                0%, 100% {
                    text-shadow: 
                        0 0 5px #39ff14,
                        0 0 10px #39ff14,
                        0 0 20px #39ff14,
                        0 0 40px #fffd00,
                        0 0 80px #fffd00,
                        0 0 90px #fffd00,
                        0 0 100px #fffd00,
                        0 0 150px #fffd00;
                }
                50% {
                    text-shadow: 
                        0 0 5px #fffd00,
                        0 0 10px #fffd00,
                        0 0 20px #fffd00,
                        0 0 40px #39ff14,
                        0 0 80px #39ff14,
                        0 0 90px #39ff14,
                        0 0 100px #39ff14,
                        0 0 150px #39ff14;
                }
            }

            body {
                font-family: 'Courier New', Courier, monospace;
                background-color: #0e0b16;
                color: #fffd00;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #39ff14;
                animation: neon 1.5s infinite;
            }
            form {
                margin-bottom: 20px;
                width: 80%;
                max-width: 800px;
                text-align: center;
                background-color: #1f1a38;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 20px #39ff14;
            }
            table {
                width: 80%;
                max-width: 800px;
                border-collapse: collapse;
                margin-bottom: 20px;
                text-align: left;
            }
            table, th, td {
                border: 1px solid #39ff14;
            }
            th, td {
                padding: 10px;
            }
            th {
                background-color: #3d2c8d;
                color: #39ff14;
            }
            td {
                background-color: #2e1a47;
            }
            label, input, textarea {
                display: block;
                margin: 10px auto;
                width: 90%;
                max-width: 400px;
                color: #ffd00;
            }
            input[type="submit"] {
                background-color: #39ff14;
                color: #141414;
                border: none;
                padding: 10px;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #fffd00;
            }
        </style>
        <title>Analizador Léxico, Sintáctico y Semántico</title>
    </head>
    <body>
        <h1>Analizador Léxico, Sintáctico y Semántico</h1>
        <form method="POST" enctype="multipart/form-data">
            <label for="file">Subir Archivo:</label>
            <input type="file" name="file"><br><br>
            <label for="code">O ingresa el código aquí:</label><br>
            <textarea name="code" rows="10" cols="50">{{ code }}</textarea><br><br>
            <input type="submit" value="Ejecutar">
        </form>

        {% if lexical_result %}
        <h2>Análisis Léxico</h2>
        <table>
            <tr>
                <th>Linea</th>
                <th>Posición</th>
                <th>Tipo de Caracter</th>
                <th>Caracter</th>
                <th>Palabra Reservada</th>
            </tr>
            {% for line in lexical_result %}
            <tr>
                <td>{{ line[0] }}</td>
                <td>{{ line[1] }}</td>
                <td>{{ line[2] }}</td>
                <td>{% if line[2] != 'Palabra reservada' %}{{ line[3] }}{% endif %}</td>
                <td>{% if line[2] == 'Palabra reservada' %}{{ line[3] }}{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}

        {% if syntactic_result %}
        <h2>Análisis Sintáctico</h2>
        <table>
            <tr>
                <th>Linea</th>
                <th>Tipo de Estructura</th>
                <th>Estructura Correcta</th>
                <th>Estructura Incorrecta</th>
            </tr>
            {% for line in syntactic_result %}
            <tr>
                <td>{{ line[0] }}</td>
                <td>{{ line[1] }}</td>
                <td>{% if line[2] %}X{% endif %}</td>
                <td>{% if not line[2] %}X{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}

        {% if semantic_result %}
        <h2>Análisis Semántico</h2>
        <table>
            <tr>
                <th>Linea</th>
                <th>Tipo de Estructura</th>
                <th>Estructura Correcta</th>
                <th>Estructura Incorrecta</th>
            </tr>
            {% for line in semantic_result %}
            <tr>
                <td>{{ line[0] }}</td>
                <td>{{ line[1] }}</td>
                <td>{% if line[2] %}X{% endif %}</td>
                <td>{% if not line[2] %}X{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </body>
    </html>
    """, code=code, lexical_result=lexical_result, syntactic_result=syntactic_result, semantic_result=semantic_result)

if __name__ == '__main__':
    app.run(debug=True)
