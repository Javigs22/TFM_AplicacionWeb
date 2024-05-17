function createTestButtons(questions) {
  dictQA = new Map(Object.entries(questions));
  // Seleccionar el elemento contenedor
  var container = document.getElementById("tests");
  for (key of dictQA.keys()) {
    var button = document.createElement("button");
    button.id = "test" + key;
    button.className = "buttonTest";
    var text = document.createElement("p");
    text.textContent = "Test " + key;
    button.appendChild(text);
    container.appendChild(button);
  }
}

function seeTopics(questions) {
  dictQA = new Map(Object.entries(questions));
  // Seleccionar el elemento contenedor
  var container = document.getElementById("container");
  var cont_topic = document.createElement("div");
  cont_topic.id = "topic";
  for (key of dictQA.keys()) {
    var topic = document.createElement("p");
    topic.textContent =
      "Tema del test " + key + ": " + questions[key]["topic"] + "\n";
    cont_topic.appendChild(topic);
  }
  container.appendChild(cont_topic);
}

function updateHTMLButtons() {
  //test futuro
  const buttonsTest = document.querySelectorAll(".buttonTest");
  const buttons = document.querySelectorAll(".switch-button__checkbox");
  //test actual
  const testContainer = document.querySelector(".div-test_container");
  const name = document.querySelectorAll(".question-name");

  // Marcar o desmarcar preguntas dentro de un mismo test
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var form = new FormData();
      form.append("testId", testContainer.id);
      form.append("questionId", button.id);
      console.log(form);
      var xhr = new XMLHttpRequest();
      url = "addQuestion/";
      xhr.open("POST", url, true);
      // Especificar que esperas una respuesta de tipo blob
      xhr.send(form);
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          return;
        }
      };
    });
  });

  // Cambiar de test (test1, test2, test3)
  buttonsTest.forEach(function (buttonTest) {
    buttonTest.addEventListener("click", function () {
      dictQA = new Map();

      const testContainer = document.querySelector(".div-test_container");
      const buttons_checked = document.querySelectorAll(
        ".switch-button__checkbox"
      );
      buttons_checked.forEach((node) => {
        // Acceder a la propiedad 'checked' de cada elemento
        if (node.checked == true) {
          number = node.id.split("switch-button")[1];
          dictQA.set(
            node.id,
            document.getElementById("text-field" + number).value
          );
          console.log("AAAAAA");
        }
      });

      var form = new FormData();
      if (dictQA.size != 0) {
        datosJson = JSON.stringify([...dictQA]);
        form.append("name", datosJson);
        console.log(dictQA);
      }
      console.log(testContainer);
      if (testContainer != null) {
        form.append("testIdOrigin", testContainer.id);
      }

      form.append("testIdNext", buttonTest.id);
      var xhr = new XMLHttpRequest();
      url = "updateTest/";
      xhr.open("POST", url, true);
      // Especificar que esperas una respuesta de tipo blob
      xhr.send(form);
      let test = null;
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          test = JSON.parse(xhr.responseText);
          var container = document.getElementById("container");
          var cont_topic = document.getElementById("topic");

          if (cont_topic) {
            container.removeChild(cont_topic);
          } else {
            var element = document.querySelector(".div-test_container");
            container.removeChild(element);
          }

          updateQuestions(test);
          updateStatus();
        }
      };
    });
  });
}

function saveSelection() {

  dictQA = new Map();

  const buttons_checked = document.querySelectorAll(".switch-button__checkbox");
  buttons_checked.forEach((node) => {
    // Acceder a la propiedad 'checked' de cada elemento
    if (node.checked == true) {
      number = node.id.split("switch-button")[1];
      dictQA.set(node.id, document.getElementById("text-field" + number).value);
    }
  });

  var form = new FormData();
  if (dictQA.size != 0) {
    datosJson = JSON.stringify([...dictQA]);
    form.append("name", datosJson);
    console.log(dictQA);
  }

  const test = document.querySelector(".div-test_container");
  testId = test.id
  form.append('testId', testId)
  var xhr = new XMLHttpRequest();
  url = "process_questions/";
  xhr.open("POST", url, true);
  // Especificar que esperas una respuesta de tipo blob
  xhr.responseType = "blob";
  xhr.send(form);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var blob = xhr.response;
      const enlaceDescarga = document.createElement("a");
      enlaceDescarga.href = URL.createObjectURL(blob);
      enlaceDescarga.download = "archivo_javi1.xml";
      // Hacer click en el enlace para iniciar la descarga
      enlaceDescarga.click();
      // Limpiar el objeto URL creado
      URL.revokeObjectURL(enlaceDescarga.href);
      window.location.replace("/home/")
    }
  };
}

function deleteSelections() {
  var list = document.querySelectorAll('input[name="switch-button"]');
  list.forEach((node) => {
    // Acceder a la propiedad 'checked' de cada elemento
    if (node.checked == true) {
      node.checked = false;
    }
  });
  var list2 = document.querySelectorAll(".question-name-field");
  list2.forEach((node) => {
    node.value = null;
  });

  var form = new FormData();
  test = document.querySelector(".div-test_container");

  form.append("testId", test.id);
  var xhr = new XMLHttpRequest();
  url = "deleteTest/";
  xhr.open("POST", url, true);
  xhr.send(form);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      return;
    }
  };
}

function updateQuestions(test) {
  dictQA = new Map(Object.entries(test));
  console.log(dictQA);
  // Seleccionar el elemento contenedor
  var container = document.getElementById("container");
  dictQA.forEach(function (value, key) {
    var cont_test = document.createElement("div");
    cont_test.id = "test" + key;
    cont_test.className = "div-test_container";
    var topic = document.createElement("p");
    topic.textContent = "Tema: " + value["topic"];
    cont_test.appendChild(topic);
    for (key2 in dictQA.get(key).questions) {
      //cada pregunta
      var cont_quest = document.createElement("div");
      cont_quest.className = "div-quest_container"
      var question = document.createElement("p");
      question.className = "question"
      question.textContent = value["questions"][key2]["statement"];
      cont_quest.appendChild(question);

      for (key3 in dictQA.get(key).questions[key2].answers) {
        var answer = document.createElement("p");
        answer.className = "answer";

        if (dictQA.get(key).questions[key2]["questionType"] == 1) {
          if (
            dictQA.get(key).questions[key2].answers[key3].correcto == "True"
          ) {
            answer.textContent =
              dictQA.get(key).questions[key2].answers[key3].status;
            answer.style.fontWeight = "bold";
          } else {
            answer.textContent =
              dictQA.get(key).questions[key2].answers[key3].status;
          }
        } else {
          answer.textContent =
            dictQA.get(key).questions[key2].answers[key3].status;
        }
        answer.textContent =
          dictQA.get(key).questions[key2].answers[key3].status;
        cont_quest.appendChild(answer);
      }
      var nameText = document.createElement("input");
      var nameLabel = document.createElement("label");
      nameText.type = "text";
      nameText.id = "text-field" + key2;

      nameText.name = "question-name";
      nameText.className = "question-name-field";
      nameText.value = dictQA.get(key).questions[key2].name;
      nameLabel.htmlFor = "switch-label" + key2;
      nameLabel.className = "question-input-field";
      nameLabel.textContent = "Nombre de la pregunta";
      cont_quest.appendChild(nameLabel);
      cont_quest.appendChild(nameText);

      var boton = document.createElement("input");
      boton.type = "checkbox";
      boton.checked = false;
      if (dictQA.get(key).questions[key2].activated == "True") {
        boton.checked = true;
      }

      boton.id = "switch-button" + key2;
      boton.name = "switch-button";
      boton.className = "switch-button__checkbox";
      boton.value = key2;

      cont_quest.appendChild(boton);
      cont_test.appendChild(cont_quest);
    }

    // Crear un nuevo elemento párrafo
    container.appendChild(cont_test);
  });
  const buttons = document.querySelectorAll(".botonNombre__boton");
  const testContainer = document.querySelector(".div-test_container");
  // Iterar sobre cada botón y agregar un event listener
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var number = button.id.split("botonNombre")[1];
      var name = document.getElementById("text-field" + number);
      console.log(name.value);
      var form = new FormData();
      form.append("testId", testContainer.id);
      form.append("questionId", "switch-button" + number);
      form.append("name", name.value);
      console.log(form);
      var xhr = new XMLHttpRequest();
      url = "/addNameToQuestion";
      xhr.open("POST", url, true);
      // Especificar que esperas una respuesta de tipo blob
      xhr.send(form);
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          return;
        }
      };
    });
  });
}

function updateStatus() {
  // Obtener una lista de todos los botones con la clase "miBoton"
  const buttons = document.querySelectorAll(".switch-button__checkbox");
  const testContainer = document.querySelector(".div-test_container");
  // Iterar sobre cada botón y agregar un event listener
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var form = new FormData();
      form.append("testId", testContainer.id);
      form.append("questionId", button.id);
      console.log(form);
      var xhr = new XMLHttpRequest();
      url = "addQuestion/";
      xhr.open("POST", url, true);
      // Especificar que esperas una respuesta de tipo blob
      xhr.send(form);
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          return;
        }
      };
    });
  });
}
