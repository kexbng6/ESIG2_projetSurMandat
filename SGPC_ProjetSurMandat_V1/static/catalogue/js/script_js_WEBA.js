/*
https://stackoverflow.com/questions/45215699/django-javascript-hidden-div-dynamically-updated
https://stackoverflow.com/questions/33473154/toggle-element-by-numerical-value-of-data-attribute-in-django-template
https://stackoverflow.com/questions/26107125/cannot-read-property-addeventlistener-of-null
https://www.w3schools.com/js/js_htmldom_elements.asp
https://www.w3schools.com/js/js_htmldom_nodes.asp
https://developer.mozilla.org/fr/docs/Web/API/GlobalEventHandlers/onload
https://developer.mozilla.org/fr/docs/Web/API/Element/classList
https://developer.mozilla.org/en-US/docs/Web/API/HTMLDetailsElement/toggle_event
*/

/*
const hover = function (){
        const buttons = document.querySelectorAll('span');
        buttons.forEach((btn) => {
        btn.addEventListener('mouseover', showPopup);
    })
*/


function showPopup() {
    if (document.getElementById('popup')== null){

        var sub = document.createElement('div');

        sub.innerHTML = `
        <div id="popup">
            <p id="titre">Frais de livraison</p>
            <hr>
            <p>Commande comportant un total de produits inférieur ou égal à 5: 5.- CHF</p>
            <p>supérieur à 5 et inférieur à 10: 10.- CHF</p>
            <p>supérieur à 10: 15.- CHF</p>
            <p id="close">Fermer</p>
        </div>`;

        var body = document.querySelector('body');

        var divContainer = document.getElementById('divContainer');
        divContainer.setAttribute('id', 'blur');

        body.appendChild(sub)

        const bttnClose = document.getElementById('close');
        bttnClose.addEventListener('click',closePopup);
    }


}

function closePopup() {
    var divPop = document.getElementById('popup');

    var divContient = document.getElementById('blur');
    divContient.setAttribute('id','divContainer');

    divPop.remove();
}


const btn = document.querySelector('strong');
btn.addEventListener('click', showPopup);




/*window.onload = clickOpen*/
