function updateRidingWindow(id) {
    idNumeric = id.substring(id.indexOf("_") + 1);
    riding = ridings[idNumeric]
    $("#riding-name").text(riding["name"]);
    for (key in riding["projected"]) {
        selector = "#riding-result-" + key.toLowerCase();
        $(selector).text(Math.round(riding["projected"][key]) + "%");
    }
    for (key in riding["swings"]) {
        selector = "#riding-swing-" + key.toLowerCase();
        $(selector).text(Math.round(riding["swings"][key]) + "%");
    }
}

$().ready(function () {
    svgNode = $("#riding-map")[0];
    //init svg-pan-zoom
    svgNode.addEventListener("load", function () {
        svgPanZoom("#riding-map", { maxZoom: 20 })
        //get the root svg node
        svgRoot = svgNode.contentDocument.documentElement;
        $("polygon", svgRoot).click(function (evt) {
            updateRidingWindow(evt.target.id);
        });
    });
})