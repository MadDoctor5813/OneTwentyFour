function updateRidingWindow(id) {
    var idNumeric = id.substring(id.indexOf("_") + 1);
    var riding = ridings[idNumeric]
    $("#riding-name").text(riding["name"]);
    for (var key in riding["projected"]) {
        var selector = "#riding-result-" + key.toLowerCase();
        $(selector).text(riding["projected"][key].toFixed(2) + "%");
    }
    for (var key in riding["swings"]) {
        var selector = "#riding-swing-" + key.toLowerCase();
        $(selector).text(riding["swings"][key].toFixed(2) + "%");
    }
}

//yes, it's already in the CSS but I have no idea how to sync those up
colors = {
    'PC': "#2c338e",
    'LIB': "#ed1b36",
    'NDP': "#f48120",
    'OTH': "#98999b"
}

function colorRiding(idx) {
    var idNumeric = this.id.substring(this.id.indexOf("_") + 1);
    var winner = "";
    var resultMax = 0;
    var ridingData = ridings[idNumeric];
    for (var key in ridingData['projected']) {
        if (ridingData['projected'][key] > resultMax) {
            resultMax = ridingData['projected'][key];
            winner = key;
        }
    }
    $(this).css({ 'fill': colors[winner] });
    console.log(this.resultMax);
}

$().ready(function () {
    svgNode = $("#riding-map")[0];
    //init svg-pan-zoom
    svgNode.addEventListener("load", function () {
        svgPanZoom("#riding-map", { maxZoom: 20 })
        //get the root svg node
        svgRoot = svgNode.contentDocument.documentElement;
        ridingShapes = $("polygon", svgRoot);
        ridingShapes.click(function (evt) {
            updateRidingWindow(evt.target.id);
        });
        ridingShapes.each(colorRiding);
    });
})
