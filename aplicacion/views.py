# Importaciones de módulos y definiciones de formularios
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from aplicacion.forms import RegisterForm, CodeForm, QuestionForm, SubjectForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import models, utils
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# Importaciones de bibliotecas adicionales
import qrcode  # Para generar códigos QR
import hashlib  # Para funciones hash criptográficas
import os  # Para operaciones relacionadas con el sistema de archivos
import base64  # Para codificación y decodificación base64
import pyotp  # Para generación y validación de códigos OTP (One-Time Password)
import secrets  # Para generación de números aleatorios criptográficamente seguros
import re  # Para manipulación de expresiones regulares
import json  # Para manipulación de datos JSON
import datetime  # Para manipulación de fechas y horas
import TFM.settings  # El archivo de configuración de Django para el proyecto

# Constantes y variables globales
MAX_ATTEMPTS = 3  # Número máximo de intentos permitidos
tempUser_ID = 1  # ID temporal de usuario, posiblemente utilizado para algún propósito específico


# Vistas creadas.
def initial_menu(request):
    """
    Vista que maneja la página inicial del sitio web.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el usuario no es anónimo y está verificado, redirige a la página de inicio ("/home").
    - Si el usuario es anónimo o no está verificado, renderiza la plantilla 'initial_menu.html'.
    """
    if not request.user.is_anonymous:
        if request.user.verified:
            # Redirige al usuario verificado a la página de inicio de la app.
            return redirect('/home')
    
    # Renderiza la plantilla 'initial_menu.html' para usuarios anónimos o no verificados.
    return render(request, 'initial_menu.html')

def register(request):
    """
    Vista para el registro de usuarios.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el método de solicitud es POST y el formulario es válido:
        - Se procesa y guarda la información del usuario en una instancia temporal.
        - Se genera un código de seguridad único para la verificación del correo electrónico.
        - Se envía un correo electrónico de verificación al usuario.
        - Se guarda un token de verificación en la base de datos.
        - Se renderiza la plantilla 'registration/verification.html'.
    - Si el método de solicitud no es POST o el formulario no es válido:
        - Se renderiza la plantilla 'registration/register.html' con el formulario de registro.

    """
    if request.method == 'POST':
        # Si la solicitud es de tipo POST, procesar el formulario de registro
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Si el formulario es válido, extraer los datos del formulario
            username = form.cleaned_data.get('username')
            password:str = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            # Codificar la contraseña y generar un vector de inicialización (IV)
            password, iv = utils.encode(TFM.settings.Key, bytes(password, 'utf-8'))

            # Crear una instancia temporal de usuario y guardarla en la base de datos
            user = models.TemporalUser(username=username, password=password, email=email, iv=iv)
            user.save()
            
            # Obtener el puerto del servidor
            port = request.META['SERVER_PORT']
            
            # Generar un código de seguridad único para la verificación del correo electrónico
            secCode = secrets.token_hex(16)  # Genera un token hexadecimal de 16 bytes (32 caracteres)
            hashSecCode = hashlib.sha256(bytes(secCode, 'utf-8'))  # Hash del código de seguridad

            # Construir el enlace de verificación de correo electrónico
            link = f'http://localhost:{port}/verificar-correo?token={secCode}&userId={user.id}'

            # Enviar un correo electrónico de verificación al usuario con el enlace
            utils.sendEmail(email, 'Verification account', f'Follow the next link to verify the mail\n Link: {link}', None)

            # Obtener la fecha y hora actual y agregar un margen de tiempo de 2 minutos
            date = datetime.datetime.now()
            margen = datetime.timedelta(minutes=2)

            # Crear un token de verificación y guardarlo en la base de datos con una validez de 2 minutos
            token = models.Token(token=hashSecCode.hexdigest(), tempUserId=user.id, date=date+margen)
            token.save()

            # Renderizar la plantilla de verificación de registro
            return render(request, 'registration/verification.html')
    else:
        # Si la solicitud no es de tipo POST, mostrar el formulario de registro vacío
        form = RegisterForm()

    # Renderizar la plantilla de registro con el formulario correspondiente
    return render(request, 'registration/register.html', {'form': form})
    
@login_required
def postlogin(request):
    """
    Vista para el segundo proceso de inicio de sesión del usuario. Consiste en la introducción de una secuencia de 6 dígitos

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el método de solicitud es GET:
        - Se genera un código QR único para la autenticación de dos factores (2FA).
        - Se envía un correo electrónico al usuario con el código QR adjunto.
        - Se renderiza la plantilla 'registration/postlogin.html' con el formulario para ingresar el código.
    - Si el método de solicitud es POST:
        - Se verifica el código ingresado por el usuario.
        - Si el código es válido, se marca al usuario como verificado y se redirige a la página de inicio.
        - Si el código es incorrecto, se cuenta el número de intentos fallidos.
        - Si se supera el número máximo de intentos, se redirige al usuario a la página de inicio de sesión.
        - Si no se supera el número máximo de intentos, se vuelve a renderizar la página de inicio de sesión con un mensaje de error.
    """
    baseKey = f'{request.user.username}'.encode()
    key = hashlib.sha256(baseKey).hexdigest().encode()

    if request.method == 'GET':
        # Si la solicitud es GET, generar código QR y enviar correo electrónico
        if 'login_attempts' in request.session:
            del request.session['login_attempts']
        userAux = request.user
        email = userAux.email
        
        # Generación del URI para el código QR
        uri = pyotp.totp.TOTP(base64.b32encode(key)).provisioning_uri(name=request.user.username, issuer_name='LessonMaster')     
        qrcode.make(uri).save(f'aplicacion/static/qrcode/qr_{userAux.username}.png')

        # Envío del correo electrónico con el código QR adjunto
        utils.sendEmail(email, 'No-replay', 'Hello', f'aplicacion/static/qrcode/qr_{userAux.username}.png')

        # Renderizado de la plantilla para ingresar el código
        return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})
    else:
        # Si la solicitud es POST, verificar el código ingresado por el usuario
        form = CodeForm(request.POST)
        if form.is_valid():
            # Si el formulario es válido, obtener el código
            code = form.data.get('fcode')
            totp = pyotp.TOTP(base64.b32encode(key))
            
            if totp.verify(code):
                # Si el código es válido, marcar al usuario como verificado y redirigir a la página de inicio de la app
                if 'login_attempts' in request.session:
                    # Si hay intentos fallidos, los elimino
                    del request.session['login_attempts']
                # Seleccionar el usuario que coincida con el nombre de usuario
                userAux = models.CustomUser.objects.get(username=request.user.username)
                # Modificar el campo verificado a verdadero, guardar el campo y redirigir a la página de inicio la app
                userAux.verified = True
                userAux.save()
                error = "El proceso de inicio de sesión se ha completado correctamente. En unos segundos será redirigido a la página principal del programa."
                return render(request, 'redirect_program.html', {'error': error})
            
            else:
                # Si el código es incorrecto, contar los intentos fallidos
                if 'login_attempts' in request.session:
                    request.session['login_attempts'] += 1
                else:
                    request.session['login_attempts'] = 1
                
                # Si se supera el número máximo de intentos, redirigir al usuario al menú inicial de inicio
                if request.session['login_attempts'] >= MAX_ATTEMPTS:
                    del request.session['login_attempts']
                    error = "El proceso de inicio de sesión no se ha completado correctamente porque se ha alcanzado el número máximo de intentos. En unos segundos será redirigido al menú inicial del programa. Si quiere usar la aplicación deberá repetir el proceso."
                    return render(request, 'registration/redirect_attempts.html', {'error': error})
                
                else:
                    # Si no se supera el número máximo de intentos, volver a renderizar la página de inicio con un mensaje de error
                    return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})

        return render(request, 'registration/postlogin.html', {'form': CodeForm(request.POST)})

@require_http_methods(["GET", "POST"])         
def verification(request):
    """
    Vista para comprobar el token de verificación del correo electrónico.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el método de solicitud es GET:
        - Se verifica la presencia y validez del token y el ID de usuario en la URL.
        - Se realiza la validación del token y se realiza el proceso de registro si es correcto.
    - Si el método de solicitud es POST:
        - Se realiza la misma verificación y proceso de registro que en el método GET.
    """
    userId = request.GET.get('userId')
    token = request.GET.get("token")

    if not token:
        # Si no se encuentra el token en la URL, se muestra un mensaje de error
        error = "El proceso de verificación ha fallado porque el token no ha sido encontrado. Si desea registrarse en la aplicación deberá repetir el proceso."
        return render(request, 'registration/redirect_registration.html', {'error': error})
    if not userId:
        # Si no se encuentra el ID de usuario en la URL, se muestra un mensaje de error
        error = "El proceso de verificación ha fallado porque el usuario no ha sido encontrado. Si desea registrarse en la aplicación deberá repetir el proceso."
        return render(request, 'registration/redirect_registration.html', {'error': error})
        
    match = re.match(r'^[A-Za-z0-9]{32}$', token)
    if not match:
        # Si el formato del token es incorrecto, se muestra un mensaje de error
        error = "El proceso de verificación ha fallado porque el token es incorrecto. Si desea registrarse en la aplicación deberá repetir el proceso."
        return render(request, 'registration/redirect_registration.html', {'error': error})
    
    match = re.match(r'^[0-9]*$', str(userId))
    if not match:
        # Si el formato del ID de usuario es incorrecto, se muestra un mensaje de error
        error = 'El proceso de verificación ha fallado porque el usuario es incorrecto. Si desea registrarse en la aplicación deberá repetir el proceso.'
        return render(request, 'registration/redirect_registration.html', {'error': error})
    try:
        # Se intenta obtener el objeto token de la base de datos
        tokenObject = models.Token.objects.get(tempUserId=userId)
    except models.Token.DoesNotExist:
        # Si no se encuentra el token en la base de datos, se muestra un mensaje de error
        
        error = "El proceso de verificación ha fallado porque el token del usuario no ha sido encontrado. Si desea registrarse en la aplicación deberá repetir el proceso."
        return render(request, 'registration/redirect_registration.html', {'error': error})
    
    if hashlib.sha256(bytes(token,'utf-8')).hexdigest() == tokenObject.token:        
        # Si el token es correcto, se verifica si ha caducado
        if datetime.datetime.now() > tokenObject.date:
            # Si ha caducado, se muestra un mensaje de error y se eliminan los datos temporales
            tempUser.delete()
            error = "El proceso de verificación ha fallado porque el token es correcto pero ha caducado. Si desea registrarse en la aplicación deberá repetir el proceso."
            return render(request, 'registration/redirect_registration.html', {'error': error})
        else:
            # Si el token es válido, se coge el usuario temporal, se decodifica la contraseña y 
            # se guarda al usuario en la base de datos definitiva
            tempUser = models.TemporalUser.objects.get(id=userId)
            password = utils.decode(tempUser.password, TFM.settings.Key, tempUser.iv)
            user = models.CustomUser(username=tempUser.username, email=tempUser.email)
            user.set_password(password)
            user.save()
            
            # Se eliminan el token y los datos temporales de la base de datos
            models.Token.objects.get(tempUserId=userId).delete()
            tempUser.delete()
            
            error = 'El proceso de verificación ha sido realizado de manera satisfactoria. En unos segundos será redirigido al menú inicial para realizar el proceso de inicio de sesión.'
            return render(request, 'redirect_program.html', {'error': error})
    
    else:
        # Si el token es incorrecto, se muestra un mensaje de error y se eliminan los datos temporales
        error = 'El proceso de verificación ha fallado porque el token es incorrecto. Si desea registrarse en la aplicación deberá repetir el proceso.'
        tempUser.delete()
        return render(request, 'registration/redirect_registration.html', {'error': error})

def home(request: object):
    """
    Vista para la página de inicio.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el usuario es anónimo o no está verificado:
        - Redirige al usuario a la página de inicio de sesión.
    - Si el usuario está autenticado y verificado:
        - Si existe un diccionario de preguntas en la sesión, se elimina.
        - Renderiza la plantilla 'home.html'.
    """
    if not request.user.is_anonymous:        
        if request.user.verified:
            if request.session.get('questionDict'):
                del request.session['questionDict']
            return render(request, 'home.html')
        else:
            return redirect('/accounts/login/?next=/postlogin')
    else:
        return redirect('/accounts/login/?next=/postlogin')
                     
def createTest(request):
    """
    Vista para la funcionalidad 1.
    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el método de solicitud es POST:
        - Si el formulario es válido, se obtienen el tema y el número de preguntas y se renderiza la plantilla 'questions.html'.
    - Si el método de solicitud no es POST:
        - Se renderiza la plantilla 'createTest.html' con el formulario correspondiente.
    """
    if request.method == 'POST':
        # Si la solicitud es POST, procesar el formulario de preguntas 
        form = QuestionForm(data=request.POST, userId=request.user.pk)
        if form.is_valid():
            # Si el formulario es válido obtener el tema y el número de preguntas y renderizar a 'questions.html'
            topic = form.cleaned_data['topic']
            numberQuestions = form.cleaned_data['numberQuestions']
            return render(request, 'questions.html', {'topic': topic, 'numberQuestions': numberQuestions})
    else:
        # Si la solicitud no es POST, mostrar el formulario de preguntas vacío
        form = QuestionForm(userId=request.user.pk)
    return render(request, 'createTest.html', {'form': form})


def questions(request):
    """
    Vista para procesar el formulario de preguntas y mostrar las preguntas generadas y sus respuestas.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el formulario es válido
        - Obtener los datos del formulario
        - Consultar el generador de preguntas para obtener las preguntas y respuestas
        - Crear un nuevo test de preguntas y respuestas en la base de datos
        - Procesar las preguntas y respuestas obtenidas del generador
        - Renderiza la plantilla 'testQuestions.html' o 'shortQuestions.html' con las preguntas generadas y sus respuestas, dependiendo del tipo de pregunta
    """
    form = QuestionForm(data=request.POST, userId=request.user.pk)
    print(form)
    if form.is_valid():
           
        # Si el formulario es válido, obtener los datos del formulario
        topic = form.data.get('topic')
        numberQuestions = form.data.get('numberQuestions')
        subject = form.data.get('subject')
        adictionalInfo = form.data.get('adictionalInfo', '')
        questionType = form.data.get('questionType')
        # Consultar el generador de preguntas para obtener las preguntas y respuestas
        lQuestions, lAnswers, lCAnswers = utils.queryIA(topic, numberQuestions, adictionalInfo, questionType)
        
        # Crear un nuevo test de preguntas y respuestas en la base de datos
        userAux = models.CustomUser.objects.get(username=request.user.username)
        test = models.TestQuestionsAnswers(topic=topic, numberQuestions=numberQuestions, adictionalInfo=adictionalInfo, user=userAux, subject=subject)
        test.save()
        
        lID = []  # Lista para almacenar los IDs de las preguntas creadas
        
        # Procesar las preguntas y respuestas obtenidas del generador
        if questionType == "1":  # Tipo test
            for question, answers, canswer in zip(lQuestions, lAnswers, lCAnswers):
                # Crear una nueva pregunta en la base de datos
                questionModel = models.Question(statement=question, questionType=questionType, test=test)
                questionModel.save()
                lID.append(questionModel.id)
                # Crear las respuestas asociadas a la pregunta
                for answer in answers:
                    flag = False
                    if answer == canswer:
                        flag = True
                    answerModel = models.Answer(answer=answer, status=flag, question=questionModel)
                    answerModel.save()
            return render(request, 'testQuestions.html', {'questions': lQuestions, 'answers': lAnswers, 'canswers': lCAnswers, 'ids': lID, 'test': test.id})
        else:  # Tipo pregunta corta
            for question, answer in zip(lQuestions, lAnswers):
                # Crear una nueva pregunta en la base de datos
                questionModel = models.Question(statement=question, questionType=questionType, test=test)
                questionModel.save()
                lID.append(questionModel.id)
                # Crear la respuesta asociada a la pregunta
                answerModel = models.Answer(answer=answer, question=questionModel)
                answerModel.save()
            return render(request, 'shortQuestions.html', {'questions': lQuestions, 'answers': lAnswers, 'ids': lID, 'test': test.id})

def chooseSubject(request): 
    """
    Vista para mostrar el formulario de selección de asignatura.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Inicialización de un formulario QuestionForm con el ID de usuario actualmente autenticado 
    - Renderiza la plantilla 'chooseSubject.html'
    """
    form = QuestionForm(userId=request.user.pk)
    return render(request, 'chooseSubject.html', {'form': form})

    
def createSubject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid(): 
            asignatura = form.cleaned_data['subject']
            
            userAux = models.CustomUser.objects.get(username = request.user.username)
            list_subjects = userAux.subject_set.all()
            
            if(list_subjects):
                for subject in list_subjects:
                    if(subject.subject == asignatura):
                        form.add_error(field='subject',error = "El usuario ya tiene esa asignatura. Introduzca otro nombre o presione el botón de volver atrás para regresar al menu de funcionalidades")
                        return render(request, 'createSubject.html', {'form': form})                
                    
                               
            subjectModel = models.Subject(subject = asignatura, user = userAux)
            subjectModel.save()
            error = "La asignatura se ha creado correctamente. En unos segundos será redirigido al menú de funcionalidades."
            return render(request, 'redirect_program.html', {'error': error})
        else:
            form = SubjectForm()
            return render(request, 'createSubject.html', {'form': form})            
    else:
        form = SubjectForm()
        return render(request, 'createSubject.html', {'form': form})
    
@login_required
def showTests(request):
    """
    Vista para mostrar las preguntas de un usuario para una asignatura determinada.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Filtrar los test que pertenecen al usuario y a la asignatura que corresponde
    - Inicializar un diccionario para almacenar las preguntas y el tema correspondiente.
    - Renderiza la plantilla 'viewTests.html' con un diccionario de preguntas y temas asociados, filtradas por el usuario y la asignatura proporcionados en la solicitud POST.
    """
    # Q permite crear objetos de consulta combinados con operadores lógicos (& representa un AND) que permiten comprobar el usuario y el tema, mostrando las preguntas de un usuario para una asignatura determinada.
    listQA = models.TestQuestionsAnswers.objects.filter(Q(subject=request.POST.get('subject')) & Q(user_id=request.user.pk))
    
    # Inicializar un diccionario para almacenar la información de las preguntas y temas
    dictQA = {}     
    for b in listQA:
        dictQA[b.id] = {}
        dictQA[b.id]['topic'] = b.topic
    
    # Renderizar la plantilla 'viewTests.html' con el diccionario de preguntas y temas asociados
    return render(request, 'viewTests.html', {'questions':dictQA})



def logout_extension(request):
    """
    Vista para cerrar sesión de un usuario y desactivar la verificación.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Selecciona el usuario que corresponde con el nombre de usuario de la request.
    - Modifica el campo verified a falso y guarda el cambio
    - Redirige al usuario a la página de cierre de sesión de Django.
    """
    user = models.CustomUser.objects.get(username=request.user.username)
    user.verified = False
    user.save()
    error = "La aplicación se ha cerrado de forma correcta. Para volver a utilizarla deberá volver a iniciar sesión."
    return render(request, 'redirect_logout.html', {'error': error})
    

@require_http_methods(['POST'])
@csrf_exempt
def processSelectedQuestion(request):
    """
    Vista para procesar preguntas seleccionadas por el usuario y crear un archivo XML con la información de las preguntas.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si no existe un diccionario de preguntas en la sesión, retorno con estado 200 (OK)
    - Si se proporciona nombres en la solicitud POST, se genera un diccionario con estos nombres.
    - Si se proporciona un identificador de test, se asigna a la variable testId
    - Se obtienen los identificadores de preguntas así como el nombre asociado a cada pregunta
    - Se ordenan los identificadores de preguntas y los nombres de cada pregunta
    - Un archivo XML con la información de las preguntas seleccionadas.
    - Preparar la respuesta HTTP con el archivo XML para ser descargado por el usuario
    """
    questionDict: dict = None 
    name: dict = None
    if request.session.get('questionDict') is None:
        # Si no existe un diccionario de preguntas en la sesión, se retorna una respuesta HTTP 200
        return HttpResponse("200")
    if request.POST.get('name') is not None:
        # Si se proporciona un 'name' en la solicitud POST, se convierte a un diccionario
        name = dict(json.loads(request.POST.get('name')))
    
    testId: str = None 
    if request.POST.get('testId') is not None:
        # Si se proporciona un 'testId' en la solicitud POST, se asigna a la variable 'testId'
        testId = request.POST.get('testId')

    questionDict = request.session['questionDict']
    names = []
    questionIds = []
    for key, value in name.items():
        # Se obtienen los IDs de las preguntas seleccionadas y sus nombres
        questionIds.append(key.split("switch-button")[1])
        names.append(value)
        
    for key, _ in questionDict.items():
        if testId == key:
            continue
        
        for key2, value in questionDict[key].items():
            questionIds.append(key2.split("switch-button")[1])
            names.append(value)
    
    # Ordenar los IDs de las preguntas
    questionIds = [int(x) for x in questionIds]
    for i in range(len(questionIds)):
        for j in range(i + 1, len(questionIds)):
            if questionIds[i] > questionIds[j]:
                questionIds[i], questionIds[j] = questionIds[j], questionIds[i]
                names[i], names[j] = names[j], names[i]
          
    # Crear un archivo XML con la información de las preguntas seleccionadas
    filename = "archivo_" + request.user.username + "_.xml"
    content = utils.createXML(questionIds, names, filename)

    # Preparar la respuesta HTTP con el archivo XML para ser descargado por el usuario
    response = HttpResponse(content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(f"aplicacion/downloads/{filename}")}"'
        
    return response

@require_http_methods(['POST'])
@csrf_exempt
def addQuestion(request):
    """
    Vista para añadir o eliminar una pregunta seleccionada por el usuario a un diccionario de preguntas en la sesión.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si se proporciona un 'testId' en la solicitud POST:
        - Se asigna el ID del test a la variable 'testId'.
    - Si se proporciona un 'questionId' en la solicitud POST:
        - Se asigna el ID de la pregunta a la variable 'questionId'.
        - Si no existe un diccionario de preguntas en la sesión, se crea uno vacío.
        - Se obtiene el diccionario de preguntas de la sesión.
        - Si el test aún no tiene un diccionario de preguntas asociado, se crea uno vacío para ese test.
        - Si la pregunta ya está en el diccionario de preguntas del test, se elimina.
        - Si el diccionario de preguntas del test queda vacío después de eliminar la pregunta, se elimina el diccionario de preguntas del test.
        - Si la pregunta no está en el diccionario de preguntas del test, se añade al diccionario de preguntas del test.
        - Se actualiza el diccionario de preguntas en la sesión.
        - Se retorna una respuesta HTTP con estado 200 (OK).
    """
    if request.POST.get('testId') is not None:
        # Si se proporciona un 'testId' en la solicitud POST, se asigna a la variable 'testId'
        testId: str = request.POST['testId']
    if request.POST.get('questionId') is not None:
        # Si se proporciona un 'questionId' en la solicitud POST, se asigna a la variable 'questionId'
        questionId: str = request.POST['questionId']
        
        if request.session.get('questionDict') is None:
            # Si no existe un diccionario de preguntas en la sesión, se crea uno vacío
            request.session['questionDict'] = {}
        questionDict: dict = request.session['questionDict']
        print("antes")
        print(questionDict)
            
        if questionDict.get(testId) is None:
            # Si el test aún no tiene un diccionario de preguntas asociado, se crea uno vacío para ese test
            questionDict[testId] = {}

        if questionId in questionDict[testId].keys():
            # Si la pregunta ya está en el diccionario de preguntas del test, se elimina
            del questionDict[testId][questionId]
            if len(questionDict[testId].keys()) == 0:
                # Si el diccionario de preguntas del test queda vacío después de eliminar la pregunta, se elimina el diccionario de preguntas del test
                del questionDict[testId]
        else:
            # Si la pregunta no está en el diccionario de preguntas del test, se añade al diccionario de preguntas del test
            questionDict[testId][questionId] = ""
        request.session['questionDict'] = questionDict
        print("despues")
        print(questionDict)
        return HttpResponse("200")

@require_http_methods(['POST'])
@csrf_exempt
def updateTest(request):
    """
    Vista para actualizar un test en la sesión del usuario.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si se proporciona un 'name' en la solicitud POST:
        - Se obtienen los nombres de las preguntas del test desde el navegador web y se almacenan en un diccionario.
    - Si se proporciona un 'testIdOrigin' en la solicitud POST:
        - Se obtiene el ID del test original que se está modificando.
    - Si existe un diccionario de preguntas en la sesión del usuario:
        - Se actualiza el diccionario de preguntas con los nombres de las preguntas del test modificado, si están disponibles.
        - Se actualiza la sesión con el diccionario de preguntas modificado.
    - Se obtiene el ID del test siguiente desde la solicitud POST y se procesa para obtener el test correspondiente de la base de datos.
    - Se construye un diccionario con la información del test obtenido de la base de datos, incluyendo el tema, las preguntas y las respuestas.
    - Se retorna una respuesta JSON con la información del test actualizada.
    """
    names: dict = None
    if request.POST.get('name') is not None:
        # Si se proporciona un 'name' en la solicitud POST, se obtienen los nombres de las preguntas del test y 
        # se almacenan en un diccionario
        names = dict(json.loads(request.POST.get('name')))
        print(names)
    
    questionDict: dict = None
    testIdOrigin = None
    if request.POST.get('testIdOrigin'):
        # Si se proporciona un 'testIdOrigin' en la solicitud POST, se obtiene el ID del test original que se está modificando
        testIdOrigin = request.POST['testIdOrigin']
        print(testIdOrigin)
    
    if request.session.get('questionDict'):
        # Si existe un diccionario de preguntas en la sesión del usuario, se obtiene y se actualiza
        questionDict: dict = request.session['questionDict']
        print(questionDict)
        if names:
            # Si se obtuvieron nombres de preguntas, se actualizan en el diccionario de preguntas
            for key, value in names.items():
                questionDict[testIdOrigin][key] = value
        # Se actualiza el diccionario de la sesión
        request.session['questionDict'] = questionDict
        print(questionDict)
    
    # Se obtiene el ID del test siguiente desde la solicitud POST
    test_id = request.POST['testIdNext']
    print(test_id)
    testId = int(test_id.split("test")[1])
    # Se obtiene el test que corresponde al identificador obtenido
    test = models.TestQuestionsAnswers.objects.get(id=testId)
    
    # Se construye un diccionario con la información del test obtenido de la base de datos
    dictQA = {}
    dictQA[test.id] = {}
    dictQA[test.id]['topic'] = test.topic
    dictQA[test.id]['questions'] = {}
    
    # Se recorren las preguntas del test y se construye el diccionario de preguntas y respuestas
    for question in test.question_set.all():
        dictQA[test.id]['questions'][question.id] = {}
        dictQA[test.id]['questions'][question.id]['statement'] = question.statement
        dictQA[test.id]['questions'][question.id]['questionType'] = question.questionType
        dictQA[test.id]['questions'][question.id]['activated'] = "False"
        dictQA[test.id]['questions'][question.id]['name'] = ""
        
        # Si existe un diccionario de preguntas en la sesión y la pregunta está activada, se actualiza el estado y el nombre de la pregunta
        if questionDict:
            if questionDict.get(test_id):
                if f'switch-button{question.id}' in questionDict[test_id]:
                    dictQA[test.id]['questions'][question.id]['activated'] = "True"
                    if questionDict[test_id].get('switch-button' + str(question.id)):
                        dictQA[test.id]['questions'][question.id]['name'] = questionDict[test_id]['switch-button' + str(question.id)]
        
        dictQA[test.id]['questions'][question.id]['answers'] = {}
        
        # Se recorren las respuestas de cada pregunta y se agregan al diccionario
        for answer in question.answer_set.all():
            dictQA[test.id]['questions'][question.id]['answers'][answer.id] = {}
            dictQA[test.id]['questions'][question.id]['answers'][answer.id]['status'] = answer.answer
            dictQA[test.id]['questions'][question.id]['answers'][answer.id]['correcto'] = str(answer.status)
    
    # Se retorna una respuesta JSON con la información del test actualizada
    return JsonResponse(dictQA, safe=True)


@require_http_methods(['POST'])
@csrf_exempt
def deleteTest(request):
    """
    Vista para eliminar un test de la sesión del usuario.

    Parámetros:
    - request: El objeto HttpRequest que representa la solicitud del cliente.

    Proceso:
    - Si el método de solicitud es POST 
        - Se coge el testId de la solicitud POST
    - Si no hay diccionario en la sesión.
        - Se retorna con estado 200 (OK).
    - Si el diccionario contiene el identificador del test 
        - Se elimina el test del diccionario.
        - Se almacena el diccionario en la sessión
    - Se retorna con estado 200 (OK).
    """
    
    # Se almacena el identificador de test que hay en la solicitud POST
    testId: str = request.POST['testId']
    if request.session.get('questionDict') is None:
        # Si no hay un diccionario de preguntas en la sesión, se retorna 
        return HttpResponse("200")
    questionDict: dict = request.session['questionDict']
           
    if questionDict.get(testId):
        # Si el 'testId' existe en el diccionario de preguntas, se elimina y se actualiza la sesión
        del questionDict[testId]
        request.session['questionDict'] = questionDict
        print(request.session['questionDict'])  # Imprimir el diccionario de preguntas actualizado (para depuración)
    # Este o no el test se vuelve con estado 200 tras eliminarlo del diccionario
    return HttpResponse("200")
        