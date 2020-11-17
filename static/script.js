
function parser(output) {
    let node = document.createElement("LI");
    let textnode = document.createTextNode(output);         
    node.appendChild(textnode);
    document.getElementById("results").appendChild(node);
}

async function search() {
    var urlencoded = new URLSearchParams();

    var requestOptions = {
    method: 'POST',
    body: urlencoded,
    };

    const response = await fetch('/' + document.getElementById(oib.id).value, requestOptions)
    .then(response => response.json())
    .catch(error => console.log('error', error))
    console.log(response.sudski)

    parser(response.sudski.skraceno_ime_tvrtke)
    parser(response.sudski.pravni_postupak)
    parser('OIB: ' + response.sudski.oib_tvrtke)
    parser('Kapital: ' + response.sudski.temeljni_kapital_tvrtke + ' KN')
    parser(response.sudski.adresa_sjedista_tvrtke)
    for (let i of response.osobe) {
        parser(i)
    }
    for (let i of response.operators) {
        parser(i)
    }
    }
