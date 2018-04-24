function updateRidingWindow(id) {
    idNumeric = id.substring(id.indexOf("_") + 1);
    $.get("api/get_riding_data/" + idNumeric, function (data) {
        $("#riding-name").text(data["name"]);
        for (key in data["percents"]) {
            selector = "#riding-result-" + key.toLowerCase();
            $(selector).text(Math.round(data["percents"][key]) + "%");
        }
        for (key in data["swings"]) {
            selector = "#riding-swing-" + key.toLowerCase();
            $(selector).text(Math.round(data["swings"][key]) + "%");
        }
    });
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