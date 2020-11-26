document.querySelector("#oib").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      search();
    }
  });

document.querySelector("#zvajz-button").addEventListener("click", function(event) {
    search();
});

function parser(status,output) { //Status can be ok, red, green
    let node = document.createElement("LI");
    if (status === 'ok'){
        node.className = "list-group-item list-group-item-secondary";
    } else if (status === 'red') {
        node.className = "list-group-item list-group-item-danger";
    } else if (status === 'green') {
        node.className = "list-group-item list-group-item-success";
    }
    
    let textnode = document.createTextNode(output);         
    node.appendChild(textnode);
    document.getElementById("results").appendChild(node);
}



function contactsParser(contact) {
    let box = document.createElement("DIV")
    box.style = "margin-top: 1%;margin-bottom: 1px;"
    box.id = '0' + String(contact);
    box.className = "col"      
    let button = document.createElement("BUTTON");
    button.innerHTML = '0' + String(contact);
    button.type = "button";
    button.id = "hackom-button";
    button.className = "col btn btn-danger";
    button.setAttribute('onclick', 'hackom(' + String(contact) + ')');
    box.appendChild(button)
    document.getElementById("contacts").appendChild(box);
    
}

function addSpinner(elemId) {
    let node = document.createElement("DIV");
    node.id = "spinner"
    node.className = "spinner-border text-light";
    node.style = "margin-left: 7%;margin-bottom: 2%;"
    node.role = "status"
    let span = document.createElement('span')
    span.class = "sr-only"
    node.appendChild(span)
    document.getElementById(elemId).appendChild(node);
}

async function hackom(contact) {
    let requestOptions = {
    method: 'GET',
    };

    const response = await fetch('/operator/' + String(contact), requestOptions)
    .then(response => response.json())
    .catch(error => console.error)

    if (response['0' + String(contact)] !== "ISKON") {
        parser('green','0' + String(contact) + ' ' + response['0' + String(contact)]);
    } else {
        parser('red','0' + String(contact) + ' ' + response['0' + String(contact)]);
    }

    document.getElementById('0' + String(contact)).remove()

    }


async function search() {
    document.getElementById("results-box").innerHTML = '';
    document.getElementById("results-box").innerHTML = '<ul id="results" class="list-group col"></ul><div id="contacts" class="col"></div>';
    document.getElementById("search-svg").style.display = "none";
    addSpinner('zvajz-button');
    var urlencoded = new URLSearchParams();

    var requestOptions = {
    method: 'POST',
    body: urlencoded,
    };

    const response = await fetch('/' + document.getElementById('oib').value, requestOptions)
    .then(response => response.json())
    .catch(error => console.error)
    console.log(response)

    if (response.sudski === null) {
        parser('red',"Subjekt obrisan!");
        document.getElementById("spinner").remove();
        document.getElementById("search-svg").style.display = "block";
    } else {
        parser('ok', response.sudski.skraceno_ime_tvrtke);

        //Company status check
        if (response.sudski.pravni_postupak !== "Bez postupka") {
            parser('red',response.sudski.pravni_postupak);
        } else {
            parser('green',response.sudski.pravni_postupak);
        }
    
    
        //Company capital check
        parser('ok', 'OIB: ' + response.sudski.oib_tvrtke)
    
        if (response.sudski.temeljni_kapital_tvrtke > 5000000) {
            parser('red','Kapital: ' + response.sudski.temeljni_kapital_tvrtke + ' KN');
        } else {
            parser('green','Kapital: ' + response.sudski.temeljni_kapital_tvrtke + ' KN')
        }
    
    
        parser('ok', response.nkd);

        if (response.web != null) {parser('ok', response.web);}
        
            
        parser('ok', response.sudski.adresa_sjedista_tvrtke)
        for (let i of response.osobe) {
            parser('ok', i)
        }
        for (let i of response.contacts) {
            contactsParser(i)
        }
        document.getElementById("spinner").remove()
        document.getElementById("search-svg").style.display = "block";
        }
    }