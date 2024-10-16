from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Función para realizar el análisis léxico
def analisis_lexico(expression):
    tokens_expr = [
        (r'\d+(\.\d+)?', 'NUMBER'),
        (r'[+\-*/]', 'OPERATOR'),
        (r'[()]', 'PARENTHESIS')
    ]
    
    tokens = []
    pos = 0
    while pos < len(expression):
        match = None
        for token_expr in tokens_expr:
            pattern, token_type = token_expr
            regex = re.compile(pattern)
            match = regex.match(expression, pos)
            if match:
                token_value = match.group(0)
                tokens.append({"token": token_value, "type": token_type})
                pos = match.end(0)
                break
        if not match:
            pos += 1  # Ignoramos caracteres no válidos

    return tokens

# Función para evaluar la expresión (con manejo de errores)
def evaluar_expresion(expression):
    try:
        resultado = eval(expression)
        return {"status": "success", "resultado": resultado}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Estructura de árbol de nodos
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Función para construir el árbol de operaciones
def construir_arbol(tokens):
    def parse_expression(index):
        node_stack = []
        op_stack = []

        while index < len(tokens):
            token = tokens[index]['token']
            tipo = tokens[index]['type']

            if tipo == 'NUMBER':
                node_stack.append(Node(token))

            elif token == '(':
                subtree, index = parse_expression(index + 1)
                node_stack.append(subtree)

            elif token == ')':
                break

            elif tipo == 'OPERATOR':
                while op_stack and op_stack[-1] in ['*', '/']:
                    operator = op_stack.pop()
                    right = node_stack.pop()
                    left = node_stack.pop()
                    node_stack.append(Node(operator, left, right))
                op_stack.append(token)

            index += 1

        while op_stack:
            operator = op_stack.pop()
            right = node_stack.pop()
            left = node_stack.pop()
            node_stack.append(Node(operator, left, right))

        return node_stack[0], index

    tree, _ = parse_expression(0)
    return tree

# Función para recorrer el árbol de forma recursiva
def recorrer_arbol(node):
    if node is None:
        return None

    return {
        'value': str(node.value),
        'left': recorrer_arbol(node.left),
        'right': recorrer_arbol(node.right)
    }

@app.route('/')
def index():
    return render_template('calculadora.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.get_json()
    expression = data.get('expression', '')
    
    tokens = analisis_lexico(expression)
    resultado = evaluar_expresion(expression)
    
    return jsonify({
        "resultado": resultado.get("resultado", None),
        "tokens": tokens,
        "status": resultado.get("status"),
        "message": resultado.get("message", "")
    })

@app.route('/tree', methods=['POST'])
def generar_arbol():
    data = request.get_json()
    expression = data.get('expression', '')

    tokens = analisis_lexico(expression)
    tree = construir_arbol(tokens)

    arbol_representation = recorrer_arbol(tree)
    
    return jsonify({
        "arbol": arbol_representation
    })

if __name__ == '__main__':
    app.run(debug=True)