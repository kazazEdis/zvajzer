function callApi(oib_mbs) {
    var myHeaders = new Headers();
    myHeaders.append("Access-Control-Allow-Origin", "127.0.0.1:8000");
    
    var requestOptions = {
      method: 'POST',
      headers: myHeaders,
      redirect: 'follow'
    };
    
    fetch("http://127.0.0.1:5000/" + oib_mbs, requestOptions)
      .then(response => response.text())
      .then(result => console.log(result))
      .catch(error => console.log('error', error));
}

