# Importación de módulos necesarios
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

# Modelos creados.
 
class TemporalUser(models.Model):
    """
    Modelo para usuarios temporales.

    Este modelo se utiliza para almacenar temporalmente la información de usuarios antes de su verificación.
    """
    usernameValidator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[usernameValidator],
        error_messages={
            'unique': _("A with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True)
    password = models.BinaryField(_('password'), max_length=256)
    iv = models.BinaryField(max_length=128)

class CustomUser(AbstractUser):
    
    """
    Modelo para usuarios personalizados.

    Este modelo extiende el modelo AbstractUser proporcionado por Django y agrega un campo booleano 'verified' para verificar la cuenta.
    """
    email = models.EmailField(blank=True, unique=True)
    verified = models.BooleanField(default=False)

class Token(models.Model):
    """
    Modelo para tokens de verificación.

    Este modelo se utiliza para almacenar los tokens de verificación generados para usuarios temporales.
    """
    token = models.CharField(max_length=128, unique=True)
    tempUserId = models.IntegerField(unique=False, null=True)
    date = models.DateTimeField(null=True)

class Subject(models.Model):
    """
    Modelo para asignaturas.

    Este modelo se utiliza para almacenar las asignaturas asociadas a los usuarios.
    """
    subject = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class TestQuestionsAnswers(models.Model):
    """
    Modelo para cuestionarios y respuestas.

    Este modelo se utiliza para almacenar los cuestionarios y respuestas creados por los usuarios.
    """
    topic = models.CharField(max_length=100, null=True)
    numberQuestions = models.IntegerField(choices=[(5, '5'), (10, '10'), (20, '20')], default=5)
    adictionalInfo = models.CharField(max_length=3000, null=True)
    subject = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

class Question(models.Model):
    """
    Modelo para preguntas.

    Este modelo se utiliza para almacenar las preguntas asociadas a los cuestionarios.
    """
    statement = models.CharField(max_length=400, null=True)
    questionType = models.IntegerField(choices=[(1, 'tipo_test'), (2, 'pregunta corta')], default=1)
    questionName = models.CharField(max_length=150, null=True, default="")
    test = models.ForeignKey(TestQuestionsAnswers, on_delete=models.CASCADE)

class Answer(models.Model):
    """
    Modelo para respuestas.

    Este modelo se utiliza para almacenar las respuestas asociadas a las preguntas.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    status = models.BooleanField(default=False)