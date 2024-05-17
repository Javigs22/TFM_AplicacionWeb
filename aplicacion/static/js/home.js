function validateSelection() {
    // Verificar si alguna funcionalidad está marcada
    var functionalities = document.getElementsByClassName('funcionalidad');
    var marcada = false;
    for (var i = 0; i < functionalities.length; i++) {
        if (functionalities[i].checked) {
            marcada = true;
            break;
        }
    }
    // Si alguna funcionalidad está marcada, avanzar a la página correspondiente
    if (marcada) {
        for (var i = 0; i < functionalities.length; i++) {
            if (functionalities[i].checked) {
                window.location.href = functionalities[i].value;
                break;
            }
        }
    } else {
        alert("Debes marcar una funcionalidad antes de continuar.");
    }
}