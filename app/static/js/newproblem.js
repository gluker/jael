var qCounter = 1;
$(function(){
   var requirementBlock = ""+
        "<div class='requirementblock row' id='requirement%id%'>"+
            "<div class='col-xs-4'>"+
                "<input placeholder='Condition%id%' class='form-control' type='text' name='condition%id%'>"+
            "</div>"+
            "<div class='col-xs-4'>"+
                "<input placeholder='Comment for %id%'  class='form-control' type='text' name='comment%id%'>"+
            "</div>"+
        "</div>";
    $("#addRequirementBtn").on('click',function(){
        var newRequirement = requirementBlock;
        $("#counter").val(qCounter);
        newRequirement = newRequirement.replace(/%id%/g,qCounter++);
        $("#requirements").append(newRequirement);
    });
});

