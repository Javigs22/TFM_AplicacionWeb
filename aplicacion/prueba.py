import re

contenido = ''
try:
    # Abre el archivo en modo lectura
    with open('prueba.txt', 'r', encoding='UTF-8') as archivo:
        # Realiza operaciones en el archivo, por ejemplo, leer su contenido
        contenido = archivo.read()
except FileNotFoundError:
    print("El archivo no se encontró.")

# Expresión regular en Python
expresion_regular = r"[1-9][0-9]?\..*?(?=Respuesta:)"

# Buscar coincidencias
listQuestions = re.findall(expresion_regular, contenido, re.DOTALL)
print(listQuestions)
for question in listQuestions:
    print(question)
    
    
    
    
expresion_regular_antigua = r'[1-9][0-9]{0,1}. \¿[^?]*\?'