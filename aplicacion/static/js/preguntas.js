function createQuestions(questions, answers, ids) {
  // Seleccionar el elemento contenedor
  var container = document.getElementById("container");

  var i = 0;
  for (i; i < questions.length; i++) {
    var especifico = document.createElement("div");
    especifico.id = "question" + i;

    // Crear un nuevo elemento párrafo
    var q = document.createElement("p");
    q.className = "question"
    // Agregar texto al párrafo
    q.textContent = questions[i];
    especifico.appendChild(q);

    var a = document.createElement("p");
    a.className = "answer"
    a.textContent = answers[i];
    especifico.appendChild(a);

    var b = document.createElement("input");
    var c = document.createElement("label");
    b.type = "text";
    b.id = "text-field" + i;

    b.name = "question-name";
    b.className = "question-name-field";
    c.textContent = "Nombre de la pregunta";
    c.setAttribute("for", "switch-label" + i);
    c.className = "question-input-field";
    especifico.appendChild(c);
    especifico.appendChild(b);
    
    var boton = document.createElement("input");
    boton.type = "checkbox";
    boton.id = "switch-button" + i;
    boton.value = ids[i];
    boton.name = "switch-button";
    boton.className = "switch-button__checkbox";

    especifico.appendChild(boton);
    container.appendChild(especifico);
  }
}

function createQuestionsTest(questions, answers, canswers, ids) {
  // Seleccionar el elemento contenedor
  var container = document.getElementById("container");

  var i = 0;
  for (i; i < questions.length; i++) {

    //crear un contenedor
    var especifico = document.createElement("div");
    especifico.id = "question" + i;
    // Crear un nuevo elemento párrafo
    var q = document.createElement("p");
    q.className = "question"
    // Agregar texto al párrafo
    q.textContent = questions[i];
    // Insertar el nuevo párrafo dentro del contenedor
    especifico.appendChild(q);
    
    for(j = 0; j < answers[i].length; j++){
      var a = document.createElement("p");
      a.className = "answer"
      
      a.textContent = String.fromCharCode(8195) + answers[i][j];
  
      if (answers[i][j] == canswers[i]){
        a.style.fontWeight = "bold";
      }

      especifico.appendChild(a);
      
    }
    var b = document.createElement("input");
    var c = document.createElement("label");
    b.type = "text";
    b.id = "text-field" + i;
    
    b.name = "question-name";
    b.className = "question-name-field";
    c.textContent = "Nombre de la pregunta";
    c.setAttribute("for", "switch-label" + i);
    c.className = "question-input-field";
    especifico.appendChild(c);
    especifico.appendChild(b);
    
    var boton = document.createElement("input");
    boton.type = "checkbox";
    boton.id = "switch-button" + i;
    boton.value = ids[i];
    boton.name = "switch-button";
    boton.className = "switch-button__checkbox";
   
    especifico.appendChild(boton);
    container.appendChild(especifico);
  }
}

function saveSelection(test_id) {
  
  var list = document.querySelectorAll('input[name="switch-button"]');
  console.log("LISTAAAAAAA")
  console.log(list)
  question = new Array();
  names = new Array();
  list.forEach((node) => {
    // Acceder a la propiedad 'checked' de cada elemento
    if (node.checked == true) {
      
      question.push(node.value); 
      i = node.id;
      a = i.split("switch-button")[1];
      var inputText = document.getElementById("text-field" + a);
      names.push(inputText.value);
    }  
  });
  console.log(question)
  console.log(names)
  var form = new FormData();
  form.append("questions", question);
  form.append("names", names);

  var xhr = new XMLHttpRequest();
  url = "process_questions/";
  xhr.open("POST", url, true);
  // Especificar que esperas una respuesta de tipo blob
  xhr.responseType = "blob";
  console.log(form)
  xhr.send(form);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var blob = xhr.response;
      const enlaceDescarga = document.createElement("a");
      enlaceDescarga.href = URL.createObjectURL(blob);
      console.log(enlaceDescarga)
      enlaceDescarga.download = "archivo_javi1_" + test_id + ".xml";;

      // Hacer click en el enlace para iniciar la descarga
      enlaceDescarga.click();

      // Limpiar el objeto URL creado
      URL.revokeObjectURL(enlaceDescarga.href);
      window.location.replace("/home/")
    }
  };
}
