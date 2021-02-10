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

        var tableau = document.querySelector('table');
        tableau.innerHTML = `
        <div id="popup">
            <p id="titre">Frais de livraison</p>
            <hr>
            <p>Commande comportant un total de produits inférieur ou égal à 5: 5.- CHF, supérieur à 5 et inférieur à 10: 10.- CHF, supérieur à 10: 15.- CHF</p>
            <p id="close">Fermer</p>
        </div> 
        `;

        // var blur = document.createElement("div");
        // blur.setAttribute("id", "blur");
        //
        // var divPop = document.createElement("div");
        // var titre = document.createElement("p");
        // titre.setAttribute('id', 'titre');
        // var textTitre = document.createTextNode("Frais de livraison");
        // titre.appendChild(textTitre);
        //
        // var barre = document.createElement("hr");
        // var para = document.createElement('p');
        // var text = document.createTextNode("Commande comportant un total de produits inférieur ou égal à 5: 5.- CHF, supérieur à 5 et inférieur à 10: 10.- CHF, supérieur à 10: 15.- CHF");
        //
        // para.appendChild(text);
        // divPop.setAttribute('id','popup');
        // divPop.appendChild(titre)
        // divPop.appendChild(barre)
        // divPop.appendChild(para);
        // blur.appendChild(divPop);
        //
        // var btnClose = document.createElement("p");
        // var textClose = document.createTextNode("Fermer");
        // btnClose.appendChild(textClose);
        // btnClose.setAttribute('id','close');
        //
        // divPop.appendChild(btnClose);
        //
        // var tableau = document.querySelector('table');
        // tableau.appendChild(divPop);

        const bttnClose = document.getElementById('close');
        bttnClose.addEventListener('click',closePopup);
    }


}

function closePopup() {
    var divPop = document.getElementById('popup');
    divPop.remove();
}


const btn = document.querySelector('strong');
btn.addEventListener('click', showPopup);




/*window.onload = clickOpen*/
