document.querySelector("#oib").addEventListener("keydown", function (event) {
    if (event.keyCode == 13) {
        search();
    }
});


document.querySelector("#zvajz-button").addEventListener("click", () => {
    search();
});


function parser(status, output, id) { //Status can be ok, red, green
    let node = document.createElement("LI");
    if (status === 'ok') {
        node.className = "list-group-item list-group-item-secondary mx-3";
        if (id != null) {
            node.id = String(id);
        }
    } else if (status === 'red') {
        node.className = "list-group-item list-group-item-danger mx-3";
        if (id != null) {
            node.id = String(id);
        }
    } else if (status === 'green') {
        node.className = "list-group-item list-group-item-success mx-3";
        if (id != null) {
            node.id = String(id);
        }
    }

    let textnode = document.createTextNode(output);
    node.appendChild(textnode);
    document.getElementById("results").appendChild(node);
}

function hrefParser(output) {
    let node = document.createElement("LI");
    node.className = "list-group-item list-group-item-secondary mx-3";
    let a = document.createElement("A");
    a.setAttribute("href", "https://" + String(output));
    a.setAttribute("target", "_blank");
    let textnode = document.createTextNode(output);
    node.appendChild(a);
    a.appendChild(textnode);
    document.getElementById("results").appendChild(node);
}




async function hackom(contact) {
    try {
        document.getElementById('0' + String(contact)).remove()
    } catch (err) {}

    let requestOptions = {
        method: 'GET',
    };

    const response = await fetch('/operator/' + String(contact), requestOptions)
        .then(response => response.json())
        .catch(error => console.error)

    response = response[0]

    if (response.Operator !== "ISKON") {
        parser('green', '0' + String(contact) + ' ' + response.Operator, contact);
    } else {
        parser('red', '0' + String(contact) + ' ' + response.Operator, contact);
    }
}


async function search() {
    document.querySelector("#results-box").style.display = 'none'
    if (document.querySelector("#oib").value.length < 8) return;
    document.querySelector("title").innerText = 'Smash'
    document.getElementById("results-box").innerHTML = '';
    document.getElementById("results-box").innerHTML = '<ul id="results" class="list-group"></ul><div id="contacts" class="row d-flex align-items-start m-2"></div>';
    document.getElementById("search-svg").style.display = "none";
    document.getElementById("spinner").style.display = "block";

    var urlencoded = new URLSearchParams();

    var requestOptions = {
        method: 'POST',
        body: urlencoded,
    };

    let response = await fetch('/oib/' + document.getElementById('oib').value, requestOptions)
        .then(response => response.json())
        .catch(error => console.error)

    console.log(response)
    document.querySelector("#results-box").style.display = 'block'
    if (response._id === null) {
        parser('red', "Subjekt obrisan!");
        document.getElementById("spinner").style.display = "none";
        document.getElementById("search-svg").style.display = "block";
    } else {
        parser('ok', response.skraceno_ime_tvrtke);
        document.querySelector("title").innerText = response.skraceno_ime_tvrtke

        //Company Tax number
        parser('ok', 'OIB: ' + response._id)

        //Company status
        if (response.pravni_postupak !== "Bez postupka") {
            parser('red', response.pravni_postupak);
        } else {
            parser('green', response.pravni_postupak);
        }

        //Capital investment
        if (response.temeljni_kapital_tvrtke > 5000000) {
            parser('red', 'Kapital: ' + response.temeljni_kapital_tvrtke.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + ' KN');
        } else if (response.temeljni_kapital_tvrtke === null) {
            parser('red', 'Kapital nije pronađen!')
        } else {
            parser('green', 'Kapital: ' + response.temeljni_kapital_tvrtke.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + ' KN')
        }

        //Services
        if (response.nkd != null) parser('ok', response.nkd);


        //Website
        if (response.web != null) hrefParser(response.web);

        //Address    
        parser('ok', String(response.naselje) + ' , ' + String(response.ulica));

        //Contacts
        if (response.kontakti.length !== 0) {
            var kontakti = ""
            response.kontakti.forEach(
                (kontakt) => {
                    kontakti = kontakti + `${0 + kontakt} `
                }
            )
            parser('ok', `Kontakti: ${kontakti}`);
        }


        document.getElementById("spinner").style.display = "none";
        document.getElementById("search-svg").style.display = "block";
    }
}