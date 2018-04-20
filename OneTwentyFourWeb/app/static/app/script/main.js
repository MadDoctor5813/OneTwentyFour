$().ready(function () {
   //init svg-pan-zoom
    $("#riding-map")[0].addEventListener("load", function () {
        svgPanZoom("#riding-map", { maxZoom: 20 })
    });
})