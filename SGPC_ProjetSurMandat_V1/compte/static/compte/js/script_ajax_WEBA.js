
/* fonctionnalité ajax */

/*
source:
https://developer.mozilla.org/fr/docs/Web/API/Element/insertAdjacentElement
https://openclassrooms.com/fr/courses/1567926-un-site-web-dynamique-avec-jquery/1569648-le-fonctionnement-de-ajax
*/



/*var xhr = new XMLHttpRequest();

xhr.onload = function (){
    if (xhr.status === 200) {

        var input = document.getElementById('id_UTI_EMAIL');
        input.addEventListener("click", test);
        /!*responseObject = JSON.parse(xhr.responseText);

        var newContent = '';
        for (var i = 0; i < responseObject.events.length; i++) {
            newContent += '<div class="newMail">';
            newContent += '<p id="validEmail">' + 'Adresse mail ' + responseObject.events[i].email + ' déjà prise. Veuillez en indiquer une autre' + '</p>';
            newContent += '</div>';
        }*!/

        /!*document.getElementById('contenu').innerHTML = newContent;*!/
    }
};

xhr.open('GET', 'get/ajax/validate/email', true)
xhr.send(null)

function test(){
   console.log('Oh ouuuuuuiiiiiiii');
   console.log('la suiiiiiiite');
}*/


   /*
    On focus out on input nickname,
    call AJAX get request to check if the nickName
    already exists or not.
    */

    $("#id_UTI_EMAIL").focusout(function () {
        var id_UTI_EMAIL = $(this).val();
        $.ajax({
            url: " ../checkMailValid/",
            //async: false,
            data : "id_UTI_EMAIL="+ id_UTI_EMAIL,
            success: function (response){
                console.log(response);
                console.log(response["mail"]);
                // if not valid user, alert the user
                if(!response["valid"]) {
                    var id_UTI_EMAIL = $("#id_UTI_EMAIL");
                    if (document.getElementById('popupMail') == null) {
                        var div = document.createElement('div');
                        div.setAttribute('id','popupMail');
                        var imputEmail = document.getElementById('id_UTI_EMAIL');
                        imputEmail.insertAdjacentElement("afterend", div);
                         }
                        document.getElementById('popupMail').innerHTML = `
                            <p style="color: #ea0000;">L'adresse mail '` + response["mail"] + `' est déjà utilisée, veuillez en choisir une autre</p>
                            <p style="color: #00eab3;">suggestion d'email -> ` + response["suggestion"] + `</p>
                        `;
                    id_UTI_EMAIL.focus();
                }
                else{
                    var textExist = document.getElementById('popupMail');
                    if (textExist != null){
                    textExist.remove();
                    }
                }
            },
            error: function (response) {
                console.log('la requête n\'a pas pu être envoyée');
                console.log(response);
            },
        })
    })
