# Importación de modulos necesarios
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, TestQuestionsAnswers, Subject

class CustomUserChangeForm(UserChangeForm):
    """
    Formulario para cambiar los detalles del usuario.

    Hereda de UserChangeForm y utiliza los mismos campos.
    """
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class RegisterForm(UserCreationForm):
    """
    Formulario para registrar un nuevo usuario.

    Hereda de UserCreationForm y agrega campos adicionales como nombre, apellido y correo electrónico.
    """
    first_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2',)

class CodeForm(forms.Form):
    """
    Formulario para ingresar el código de Google Authenticator.

    Contiene un campo para ingresar el código de 6 dígitos.
    """
    code = forms.IntegerField(max_value='999999', required=False, help_text='Introduce the 6 digits code of Google Authenticator.')

class QuestionForm(forms.ModelForm):
    """
    Formulario para crear preguntas.

    Contiene campos para el tema, el número de preguntas, información adicional, asignatura y tipo de pregunta.
    """
    adictionalInfo = forms.CharField(label='Introduce información adicional si quieres preguntas más específicas. (OPCIONAL)', required=False)
    subject = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple, required=True)
    questionType = forms.ChoiceField(choices=[(1, 'Tipo test'), (2, 'Preguntas cortas')])

    def __init__(self, userId:int, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        user = CustomUser.objects.get(id=userId)
        subjects = user.subject_set.all()
        choices = [(a.subject, a.subject) for a in subjects]
        self.fields['subject'] = forms.MultipleChoiceField(choices=choices)

    class Meta:
        model = TestQuestionsAnswers
        fields = ['topic', 'numberQuestions', 'adictionalInfo']

class SubjectForm(forms.ModelForm):
    """
    Formulario para crear una asignatura.

    Contiene un campo para ingresar el nombre de la asignatura.
    """
    subject = forms.CharField(label='Introduce el nombre de la asignatura', required=True)

    class Meta:
        model = Subject
        fields = ['subject']
