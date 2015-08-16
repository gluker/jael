removeRequirement = function(but){
    $(but).parent().parent().remove();
}
$(function(){
   qCounter = +$("#counter").val()+1;
   var requirementBlock = ""+
        "<div class='requirementblock row' id='requirement%id%'>"+
            "<div class='col-xs-4'>"+
                "<input placeholder='Condition%id%' class='form-control' type='text' name='requirements-%id%-condition'>"+
            "</div>"+
            "<div class='col-xs-4'>"+
                "<input placeholder='Comment for %id%'  class='form-control' type='text' name='requirements-%id%-comment'>"+
            "</div>"+
            "<div class='col-xs-1'>"+
                "<button type='button' onclick='removeRequirement(this);'class='btn btn-danger'>X</button>"+
            "</div>"+
        "</div>";
    $("#addRequirementBtn").on('click',function(){
        var newRequirement = requirementBlock;
        $("#counter").val(qCounter);
        newRequirement = newRequirement.replace(/%id%/g,qCounter++);
        $("#requirements").append(newRequirement);
    });
});

