$(document).ready(function () {
    // $("div#reg").removeClass("registra");
    document.getElementById("showReg").onclick = function () {
        document.getElementById("log").style.display = "none";
        document.getElementById("reg").style.display = "block";
    }
    document.getElementById("showLog").onclick = function () {
        document.getElementById("reg").style.display = "none";
        document.getElementById("log").style.display = "block";
    }
});