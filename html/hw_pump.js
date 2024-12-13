function vacay_warning(pckt){
    window.alert("Vacation disable must be <= 15 and >= 0");
}

var ws
function establish_ws () {
    open_mesg_txt = '{"opcode":"refresh","value":"' + navigator.userAgent + '"}'
    ws = new WebSocket("ws://192.168.1.53:5679/")

    ws.onopen = () => ws.send(open_mesg_txt);

    ws.onmessage = function (event) {
        const cmds = JSON.parse(event.data);
        for (let c of cmds) {
            {console.log("Command: ", c)}
            switch (c.cmd_type) {
                case "function": window[c.func_id](c);
                    break;
                case "innerhtml": document.getElementById(c.id).innerHTML = c.value;
                    break;
                default: console.log("Unrecognized cmd_type: ", c.cmd_type);
            }
        }

    }

    ws.onerror = function(event) {
       console.log(event)
    }

}

window.establish_ws();

setInterval(check_ws_state, 1000);

function check_ws_state() {
    switch (ws.readyState) {
        case 0: 
            ws_status_msg = "CONNECTING ";
            break;
        case 1: 
            ws_status_msg = "OPEN ";
            break;
        case 2: 
            ws_status_msg = "CLOSING ";
            break;
        case 3: 
            ws_status_msg = "CLOSED ";
            window.establish_ws();
            break;
    }
}