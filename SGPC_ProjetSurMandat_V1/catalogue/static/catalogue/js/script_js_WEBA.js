/*
Sources:
-https://stackoverflow.com/questions/26107125/cannot-read-property-addeventlistener-of-null
-https://www.w3schools.com/js/js_htmldom_elements.asp
-https://www.w3schools.com/js/js_htmldom_nodes.asp
-https://developer.mozilla.org/fr/docs/Web/API/ChildNode/remove
-https://developer.mozilla.org/fr/docs/Web/API/Document/getElementById
-https://developer.mozilla.org/fr/docs/Web/API/Node/appendChild
-https://developer.mozilla.org/fr/docs/Web/API/Document/querySelector
*/

function showPopup() {
    if (document.getElementById('popup')== null){
        var popup = document.createElement('div');
        popup.innerHTML = `
        <div id="popup">
            <p id="titre">Frais de livraison</p>
            <hr>
            <p>Commande comportant un total de produits inférieur ou égal à 5 articles: 5.- CHF</p>
            <p>Entre 5 et 10 articles: 10.- CHF</p>
            <p>Supérieur à 10 articles: 15.- CHF</p>
            <p id="close">Fermer</p>
        </div>`;
        const body = document.querySelector('body');
        document.getElementById('divContainer').setAttribute('id', 'blur');
        body.appendChild(popup);
        const bttnClose = document.getElementById('close');
        bttnClose.addEventListener('click',closePopup);
    }
}
function closePopup() {
    var divPop = document.getElementById('popup');
    document.getElementById('blur').setAttribute('id','divContainer');
    divPop.remove();
}
const btn = document.querySelector('strong');
btn.addEventListener('click', showPopup);