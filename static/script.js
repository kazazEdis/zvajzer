
function parser(output) {
    let node = document.createElement("LI");
    node.className = "list-group-item list-group-item-secondary";
    let textnode = document.createTextNode(output);         
    node.appendChild(textnode);
    document.getElementById("results").appendChild(node);
}

function addSpinner(elemId) {
    let node = document.createElement("DIV");
    node.id = "spinner"
    node.className = "spinner-border text-light";
    node.style = "margin-left: 7.5%;margin-bottom: 2%;"
    node.role = "status"
    let span = document.createElement('span')
    span.class = "sr-only"
    node.appendChild(span)
    document.getElementById(elemId).appendChild(node);
}

async function search() {
    addSpinner("results-box")
    var urlencoded = new URLSearchParams();

    var requestOptions = {
    method: 'POST',
    body: urlencoded,
    };

    const response = await fetch('/' + document.getElementById(oib.id).value, requestOptions)
    .then(response => response.json())
    .catch(error => console.log('error', error))

    parser(response.sudski.skraceno_ime_tvrtke)
    parser(response.sudski.pravni_postupak)
    parser('OIB: ' + response.sudski.oib_tvrtke)
    parser('Kapital: ' + response.sudski.temeljni_kapital_tvrtke + ' KN')
    parser(response.nkd)
    parser(response.sudski.adresa_sjedista_tvrtke)
    for (let i of response.osobe) {
        parser(i)
    }
    for (let i of response.operators) {
        parser(i)
    }
    document.getElementById("spinner").remove()
    }
