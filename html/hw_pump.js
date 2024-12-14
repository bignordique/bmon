function vacay_warning(pckt){
    window.alert("Vacation disable must be <= 15 and >= 0");
}

var wss
function establish_wss () {
    open_mesg_txt = '{"opcode":"refresh","value":"' + navigator.userAgent + '"}'
    wss = new WebSocket("wss://hw.bignordique.com:5679/")

    wss.onopen = () => wss.send(open_mesg_txt);

    wss.onmessage = function (event) {
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

    wss.onerror = function(event) {
       console.log(event)
    }

}

window.establish_wss();

setInterval(check_wss_state, 1000);

function check_pump_state() {
    <script src="https://hw.bignordique.com/cgi-bin/gen_pump_status.py"></script> 
}
