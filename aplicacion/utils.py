# Importaciones de módulos
from django.core.mail import EmailMessage
import re
from . import models
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import google.generativeai as genai

def sendEmail(email: str, subject: str, body: str, attach_file: str):
    """
    Función para enviar un correo electrónico.

    Parámetros:
        email (str): Dirección de correo electrónico del destinatario.
        subject (str): Asunto del correo electrónico.
        body (str): Cuerpo del correo electrónico.
        attach_file (str): Ruta del archivo a adjuntar al correo electrónico. 
            Si no se proporciona un archivo, debe ser una cadena vacía ('').

    Notas:
        - El correo electrónico se enviará desde la dirección 'LessonMasterTeam@gmail.com'.
        - Si se proporciona una ruta de archivo en `attach_file`, se adjuntará al correo electrónico.
        - Si `attach_file` es una cadena vacía, ningún archivo se adjuntará al correo.
        - Si falla el envío del correo electrónico, se generará una excepción.
    """
    
    # Dirección de correo electrónico del remitente
    original_email = 'LessonMasterTeam@gmail.com'
    
    # Crear un objeto EmailMessage con los parámetros proporcionados
    email = EmailMessage(
        subject,  # Asunto del correo electrónico
        body,     # Cuerpo del correo electrónico
        original_email,  # Dirección de correo electrónico del remitente
        [email],  # Lista de destinatarios (en este caso, solo uno)
    )
    
    # Adjuntar el archivo al correo electrónico si se proporciona
    if attach_file:
        email.attach_file(attach_file)
    
    # Enviar el correo electrónico
    email.send(fail_silently=False)
        
def queryIA(topic, numberQuestions, adictionalInfo, questionType):
    """
    Función para consultar a un modelo de inteligencia artificial generativa sobre la generación de preguntas para un examen.

    Parámetros:
        topic (str): El tema sobre el cual se desea generar preguntas.
        numberQuestions (int): El número de preguntas que se desea generar.
        adictionalInfo (str): Información adicional que puede ayudar a generar preguntas más específicas.
        questionType (str): El tipo de preguntas a generar. Puede ser "1" para preguntas con respuestas cortas o "2" para preguntas tipo test.

    Retorna:
        tuple: Una tupla que contiene tres listas:
            - Una lista de preguntas.
            - Una lista de respuestas (en el caso de preguntas de opción múltiple).
            - Una lista de respuestas correctas (en el caso de preguntas de opción múltiple).

    Raises:
        None

    Notas:
        - Utiliza un modelo generativo de inteligencia artificial para generar preguntas basadas en el tema proporcionado.
        - El parámetro `topic` especifica el tema sobre el cual se generarán las preguntas.
        - El parámetro `numberQuestions` indica cuántas preguntas se deben generar.
        - El parámetro `adictionalInfo` proporciona información adicional para generar preguntas más específicas.
        - El parámetro `questionType` determina el tipo de preguntas a generar. Puede ser "1" para preguntas tipo test o "2" para preguntas cortas.
        - Las preguntas generadas se devuelven como una lista.
        - Las respuestas generadas se devuelven como una lista, y las respuestas correctas se devuelven como otra lista en caso de preguntas tipo test.
    """
    # Valor de la clave de la API de Google
    GOOGLE_API_KEY = 'AIzaSyD6LpGZDxIASrvRdi4rmYJ_AHub7-jQC44'
    
    # Configurar la API generativa con la clave proporcionada
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Crear un modelo generativo
    model = genai.GenerativeModel(model_name='gemini-pro')
    
    listCAnswers = None
    
    # Generar preguntas cortas
    if questionType == "2":
        # Generación de la petición que se va a enviar a la IA
        message = f"Tengo que elaborar un examen sobre {topic}.\n\
Necesito {numberQuestions} preguntas con respuestas que contesten SOLO A LO QUE SE ESTÁ PREGUNTANDO (sin ningún tipo de información extra) y cumplan OBLIGATORIAMENTE con los siguientes requisitos:\n\
\
Requisito 1: Quiero que sean preguntas que tengan respuestas cortas con 3 o 4 palabras máximo.\n\
Requisito 2: Quiero que las preguntas se centren únicamente en contestar a lo que se pregunta. De esta forma, NO quiero información entre paréntesis ni aclaraciones después de una coma.\n\
Requisito 3: NO quiero que haya ninguna pregunta de bonus\n\
Requisito 4: El formato debe ser ESTRICTAMENTE EL SIGUIENTE:\n\
1. Aquí la pregunta\n\
Respuesta: Aquí la respuesta\n\
    " 

        # Agregar información adicional si se proporciona
        if adictionalInfo:
            message2 = f"Para que las preguntas sean más concretas, te detallo a continuación los temas dados durante la asignatura. {adictionalInfo}"          
            message = message + message2
            # Respuesta recibida introduciendo el mensaje formado por la petición básica y la información adiccional
            response = model.generate_content([message])    
            
        else:
           # Respuesta recibida introduciendo el mensaje formado por la petición básica
           response = model.generate_content([message])
        
                             
        # Patrones de expresiones regulares para extraer preguntas y respuestas del texto generado
        patternQ = r'[1-9][0-9]?\..*?(?=Respuesta:)'
        patternA = r'Respuesta: [^\n]*'
        
        # Buscar preguntas y respuestas en el texto generado
        listAnswers = re.findall(patternA, response.text)        
        listQuestions = re.findall(patternQ, response.text, re.DOTALL)
        
    else:  # Generar preguntas tipo test
        # Generación de la petición que se va a enviar a la IA
        message = f"Tengo que elaborar un examen sobre {topic}.\n\
Necesito {numberQuestions} preguntas tipo test que tengan 4 opciones y tan solo 1 opción correcta\n\
\
Requisito 1: Quiero que las preguntas sean objetivas.\n\
\
Requisito 2: NO quiero que haya ninguna pregunta de bonus\n\
\
Requisito 3: El formato debe ser ESTRICTAMENTE EL SIGUIENTE:\n\
1. Aquí la pregunta\n\
(A) Opción a\n\
(B) Opción b\n\
(C) Opción c\n\
(D) Opción d\n\
Respuesta: (B) AQUI VUELVE A ESCRIBIR ESTRICTAMENTE EL TEXTO CON LA RESPUESTA\n\
    " 

        # Agregar información adicional si se proporciona
        if adictionalInfo:
           message2 = f" Para que las preguntas sean más concretas, te detallo a continuación los temas dados durante la asignatura{adictionalInfo}"          
           message = message + message2
           # Respuesta recibida introduciendo el mensaje formado por la petición básica y la información adiccional
           response = model.generate_content([message])    
            
        else:
           # Respuesta recibida introduciendo el mensaje formado por la petición básica
           response = model.generate_content([message])
        
                 
        # Patrones de expresiones regulares para extraer preguntas y respuestas del texto generado
        patternQ = r'[1-9][0-9]?\..*?(?=\(A\))'
        patternA = r'^\([A-D]\) [^\n]*'
        patternCA = r'Respuesta: \([A-D]\) [^\n]*'
        
        # Buscar preguntas, respuestas y respuestas correctas en el texto generado
        listQuestions = re.findall(patternQ, response.text,re.DOTALL)
        listAnswers = re.findall(patternA, response.text, re.MULTILINE)
        listAnswers = splitList(listAnswers, 4)  # Dividir la lista de respuestas en sublistas de 4 elementos cada una
        listCAnswers  = re.findall(patternCA, response.text)
        
        # Procesar las respuestas correctas para obtener solo el texto de respuesta
        listCAnswersAux = []
        for CAnswers in listCAnswers:
            listCAnswersAux.append(CAnswers.split("Respuesta: ")[1])
        listCAnswers = listCAnswersAux
    # Devolver las listas de preguntas, respuestas y respuestas correctas
    return listQuestions, listAnswers, listCAnswers

def splitList(list, sublistSize):
    """
    Divide una lista en sublistas de tamaño específico.

    Parámetros:
        list (list): La lista que se va a dividir.
        sublistSize (int): El tamaño de cada sublista.

    Devuelve:
        list: Una lista de sublistas, donde cada sublista tiene un tamaño igual a `sublistSize`.
    """
    
    # Inicializa una lista para almacenar las sublistas
    sublists = []

    # Itera sobre el rango de índices de la lista original, avanzando en incrementos del tamaño de la sublista
    for i in range(0, len(list), sublistSize):
        # Agrega una sublista de la lista original, desde el índice actual hasta el índice actual más el tamaño de la sublista,
        # a la lista de sublistas
        sublists.append(list[i:i+sublistSize])

    # Retorna la lista de sublistas
    return sublists

def createXML(questionIds, names, filename):
    """
    Crea un archivo XML con preguntas para importarlo en un sistema de gestión de aprendizaje (LMS).

    Parámetros:
        questionIds (list): Una lista de identificadores de preguntas.
        names (list): Una lista de nombres de preguntas.
        filename (str): El nombre del archivo XML a crear.

    Devuelve:
        str: El contenido del archivo XML generado como una cadena de texto.
    """
    # Inicializar el contenido del archivo XML
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<quiz>\n'
    content += '\t<question type="category">\n'
    content += '\t\t<category>\n\t\t\t<text>Nombre del curso</text>\n\t\t</category>\n'
    content += '\t\t<info format="html">\n\t\t\t<text></text>\n\t\t</info>\n'
    content += '\t\t<idnumber></idnumber>\n'
    content += '\t</question>\n'
    
    # Iterar sobre cada pregunta para generar el XML
    for id, name in zip(questionIds, names):         
        content2 = createQuestionXML(id, name)  # Crear el contenido XML para cada pregunta
        content += content2 # Añadir la pregunta actual al resto del XML 
        
    # Cerrar el archivo XML
    content += '</quiz>'
    
    # Devolución del contenido
    return content
    
def createQuestionXML(id, name):
    """
    Crea un bloque de XML que representa una pregunta en formato Moodle XML.

    Parámetros:
        id: El identificador de la pregunta en la base de datos.
        name: El nombre de la pregunta.

    Devuelve:
        str: Una cadena que contiene el bloque XML de la pregunta.
    """
    
    # Verifica el tipo de pregunta en la base de datos
    if models.Question.objects.get(id=id).questionType == 1:
        # Si la pregunta es de opción múltiple
        questionAux = models.Question.objects.get(id=id)
        content2 = ''
        content2 += '\t<question type="multichoice">\n'
        content2 += f'\t\t<name>\n\t\t\t<text>{name}</text>\n\t\t</name>\n'

        # Elimina el prefijo numérico del enunciado
        question = questionAux.statement[3:]
        content2 += f'\t\t<questiontext format="html">\n\t\t\t<text><![CDATA[<p dir="ltr" style="text-align: left;">{question}<br></p>]]></text>\n\t\t</questiontext>\n'
        content2 += '\t\t<generalfeedback format="html">\n\t\t\t<text></text>\n\t\t</generalfeedback>\n'
        content2 += '\t\t<defaultgrade>1.0000000</defaultgrade>\n'
        content2 += '\t\t<penalty>0.3333333</penalty>\n'
        content2 += '\t\t<hidden>0</hidden>\n'
        content2 += '\t\t<idnumber></idnumber>\n'
        content2 += '\t\t<single>true</single>\n'
        content2 += '\t\t<shuffleanswers>true</shuffleanswers>\n'
        content2 += '\t\t<answernumbering>abc</answernumbering>\n'
        content2 += '\t\t<showstandardinstruction>1</showstandardinstruction>\n'
        content2 += '\t\t<correctfeedback format="html">\n\t\t\t<text>Respuesta correcta.</text>\n\t\t</correctfeedback>\n'
        content2 += '\t\t<incorrectfeedback format="html">\n\t\t\t<text>Respuesta incorrecta.</text>\n\t\t</incorrectfeedback>\n'

        # Agrega las opciones de respuesta
        for solution in questionAux.answer_set.all():
            option = solution.answer[4:]
            if solution.status == True:
                content2 += '\t\t<answer fraction="100.00000" format="html">\n'
                content2 += f'\t\t\t<text><![CDATA[<p dir="ltr" style="text-align: left;">{option}<br></p>]]></text>\n'
                content2 += '\t\t\t<feedback format="html">\n\t\t\t\t<text></text>\n\t\t\t</feedback>\n'
                content2 += '\t\t</answer>\n'
            else:
                content2 += '\t\t<answer fraction="-33.33333" format="html">\n'
                content2 += f'\t\t\t<text><![CDATA[<p dir="ltr" style="text-align: left;">{option}<br></p>]]></text>\n'
                content2 += '\t\t\t<feedback format="html">\n\t\t\t\t<text></text>\n\t\t\t</feedback>\n'
                content2 += '\t\t</answer>\n'
        content2 += '\t</question>\n'
        
    else:
        # Si la pregunta es de respuesta corta
        questionAux = models.Question.objects.get(id=id)
        content2 = ''
        content2 += '\t<question type="shortanswer">\n'
        content2 += f'\t\t<name>\n\t\t\t<text>{name}</text>\n\t\t</name>\n'

        # Elimina el prefijo numérico del enunciado
        question = questionAux.statement[3:]
        content2 += f'\t\t<questiontext format="html">\n\t\t\t<text><![CDATA[<p dir="ltr" style="text-align: left;">{question}<br></p>]]></text>\n\t\t</questiontext>\n'
        content2 += '\t\t<generalfeedback format="html">\n\t\t\t<text></text>\n\t\t</generalfeedback>\n'
        content2 += '\t\t<defaultgrade>1.0000000</defaultgrade>\n'
        content2 += '\t\t<penalty>0.000000</penalty>\n'
        content2 += '\t\t<hidden>0</hidden>\n'
        content2 += '\t\t<idnumber></idnumber>\n'
        
        # Obtiene la opción de respuesta correcta
        option = models.Answer.objects.get(question_id=id).answer[11:]
        
        # Agrega la opción de respuesta correcta
        content2 += '\t\t<answer fraction="100" format="html">\n'
        content2 += f'\t\t\t<text>{option}</text>\n'
        content2 += '\t\t\t<feedback format="html">\n\t\t\t\t<text>Respuesta correcta.</text>\n\t\t\t</feedback>\n'
        content2 += '\t\t\t<tolerance>100</tolerance>\n'
        content2 += '\t\t\t<tolerancetype>1</tolerancetype>\n'
        content2 += '\t\t\t<patternmatch>1</patternmatch>\n'
        content2 += '\t\t</answer>\n'
        
        # Agrega la opción de respuesta incorrecta
        content2 += '\t\t<answer fraction="0.000000" format="html">\n'
        content2 += f'\t\t\t<text>*</text>\n'
        content2 += '\t\t\t<feedback format="html">\n\t\t\t\t<text>Respuesta incorrecta.</text>\n\t\t\t</feedback>\n'
        content2 += '\t\t\t<tolerance>100</tolerance>\n'
        content2 += '\t\t\t<tolerancetype>1</tolerancetype>\n'
        content2 += '\t\t\t<patternmatch>0</patternmatch>\n'
        content2 += '\t\t</answer>\n'
        
        content2 += '\t</question>\n'
        
    return content2

def encode(key: bytes, plaintext: bytes):
    """
    Encripta un texto plano utilizando el algoritmo AES en modo CBC.

    Parámetros:
        key (bytes): La clave de encriptación, debe tener 16, 24 o 32 bytes de longitud.
        plaintext (bytes): El texto plano a encriptar.

    Devuelve:
        tuple: Una tupla que contiene el texto cifrado y el vector de inicialización (IV).
    """
    # Crea un objeto AES para encriptar en modo CBC con la clave proporcionada
    cipher = AES.new(key, AES.MODE_CBC)
    
    # Encripta el texto plano, asegurándose de que tenga un tamaño de bloque AES válido
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    
    # Obtiene el vector de inicialización (IV) utilizado durante la encriptación
    iv = cipher.iv
    
    # Retorna el texto cifrado y el vector de inicialización
    return ciphertext, iv


def decode(ciphertext: bytes, key: bytes, iv: bytes):
    """
    Desencripta un texto cifrado utilizando el algoritmo AES en modo CBC.

    Parámetros:
        ciphertext (bytes): El texto cifrado a desencriptar.
        key (bytes): La clave de desencriptación, debe ser la misma utilizada durante la encriptación.
        iv (bytes): El vector de inicialización (IV) utilizado durante la encriptación.

    Devuelve:
        bytes: El texto plano desencriptado.
    """
    # Crea un objeto AES para desencriptar en modo CBC con la clave y el IV proporcionados
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Desencripta el texto cifrado y lo desrellena para obtener el texto plano original
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    # Retorna el texto plano desencriptado
    return plaintext