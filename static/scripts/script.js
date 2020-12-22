document.querySelector("#oib").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      search();
    }
  });


document.querySelector("#zvajz-button").addEventListener("click", ()=> {
    search();
});

document.querySelector("#operator").addEventListener("click", ()=> {
    let inp = document.getElementById('operator-box').value
    while(inp.charAt(0) === '0') { inp = inp.substring(1); }
    hackom(inp)
    document.getElementById('operator-box').value = ''
});

document.querySelector("#operator-box").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      let inp = document.getElementById('operator-box').value
    while(inp.charAt(0) === '0') { inp = inp.substring(1); }
    hackom(inp)
    document.getElementById('operator-box').value = ''
    }
  });


function parser(status,output, id) { //Status can be ok, red, green
    let node = document.createElement("LI");
    if (status === 'ok'){
        node.className = "list-group-item list-group-item-secondary mx-3";
        if (id != null) { node.id = String(id); }
    } else if (status === 'red') {
        node.className = "list-group-item list-group-item-danger mx-3";
        if (id != null) { node.id = String(id); }
    } else if (status === 'green') {
        node.className = "list-group-item list-group-item-success mx-3";
        if (id != null) { node.id = String(id); }
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

function contactsParser(contact) {
    let box = document.createElement("DIV")
    box.id = '0' + String(contact);
    box.className = "col mt-1";    
    let button = document.createElement("BUTTON");
    button.innerHTML = '0' + String(contact);
    button.type = "button";
    button.id = "hackom-button";
    button.className = "col btn btn-danger";
    button.setAttribute('onclick', 'hackom(' + String(contact) + ')');
    box.appendChild(button);
    document.getElementById("contacts").appendChild(box);    
}



async function hackom(contact) {
    try {
        document.getElementById('0' + String(contact)).remove()
      }
      catch(err) {}

    let requestOptions = {
    method: 'GET',
    };

    const response = await fetch('/operator/' + String(contact), requestOptions)
    .then(response => response.json())
    .catch(error => console.error)
    

    if (response.operator !== "ISKON") {
        parser('green','0' + String(contact) + ' ' + response.operator, contact);
    } else {
        parser('red','0' + String(contact) + ' ' + response.operator, contact);
    }

    if (response['operator_history'].length > 1) {
        let table = document.createElement("TABLE");
        table.className = "table table-striped table-dark";
        let thead = document.createElement("THEAD");
        thead.innerHTML = '<tr><th scope="col">Operator</th><th scope="col">Datum provjere</th></tr>'
        let tbody = document.createElement("TBODY");
        
        
        for (let item of response['operator_history']) {
            operator = item.operator
            timestamp = item.timestamp

            let tr = document.createElement("TR");
            tr.className = "table-striped";
            let a = document.createElement("TD");
            a.innerText = operator
            let b = document.createElement("TD");
            b.innerText = timestamp
        
            tr.appendChild(a);
            tr.appendChild(b);
            tbody.appendChild(tr);
        }
        
        table.appendChild(thead);
        table.appendChild(tbody);
        document.getElementById(String(contact)).appendChild(table);
    }
}


async function search() {
    document.querySelector("title").innerText = 'Žvajzer'
    document.getElementById("results-box").innerHTML = '';
    document.getElementById("results-box").innerHTML = '<ul id="results" class="list-group"></ul><div id="contacts" class="row d-flex align-items-start m-2"></div>';
    document.getElementById("search-svg").style.display = "none";
    document.getElementById("spinner").style.display = "block";

    var urlencoded = new URLSearchParams();

    var requestOptions = {
    method: 'POST',
    body: urlencoded,
    };

    let response = await fetch('/' + document.getElementById('oib').value, requestOptions)
    .then(response => response.json())
    .catch(error => console.error)
    response = response[String(document.querySelector("#oib").value)]

    if (response.sudski === null) {
        parser('red',"Subjekt obrisan!");
        document.getElementById("spinner").style.display = "none";
        document.getElementById("search-svg").style.display = "block";
    } else {
        parser('ok', response.sudski.skraceno_ime_tvrtke);
        document.querySelector("title").innerText = "Ž: " + response.sudski.skraceno_ime_tvrtke

        //Company Tax number
        parser('ok', 'OIB: ' + response.sudski.oib_tvrtke)

        //Company status
        if (response.sudski.pravni_postupak !== "Bez postupka") {
            parser('red',response.sudski.pravni_postupak);
        } else {
            parser('green',response.sudski.pravni_postupak);
        }

        //Capital investment
        if (response.sudski.temeljni_kapital_tvrtke > 5000000) {
            parser('red','Kapital: ' + response.sudski.temeljni_kapital_tvrtke.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + ' KN');
        } else if (response.sudski.temeljni_kapital_tvrtke === null) {
            parser('red', 'Kapital nije pronađen!')
        } else {
            parser('green','Kapital: ' + response.sudski.temeljni_kapital_tvrtke.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + ' KN')
        }

        //Company size
        if (response.velicina != "Veliki") {
            parser('ok', 'Veličina: ' + response.velicina);
        } else {
            parser('red', 'Veličina: ' + response.velicina);
        }

        //Services
        if (response.nkd != null) {parser('ok', response.nkd);}
        

        //Website
        if (response.web != null) {hrefParser(response.web);}

        //Address    
        parser('ok', String(response.sudski.naselje) + ' , ' + String(response.sudski.ulica));

        //Personality
        for (let i of response.osobe) {
            parser('ok', i)
        }

        //Contacts
        for (let i of response.contacts) {
            contactsParser(i)
        }

        document.getElementById("spinner").style.display = "none";
        document.getElementById("search-svg").style.display = "block";
    }
}
