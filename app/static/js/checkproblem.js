$("form").on("submit", function(event){
    event.preventDefault();
    var data_to_send = $(this).serialize(); 
    console.log(data_to_send);
    $.ajax({
        data : data_to_send,
        url: $("form").attr("action"),
        type: "POST",
        success: function(result){
            if(result['rate'] !== "undefined"){
                if (result['rate'] == "100"){
                    $("#panel").attr("class","panel panel-success");
                } else{
                    $("#panel").attr("class","panel panel-default");
                }
                $("#rate").text(result['rate']);
            };
            $("#messages").empty();
            msgs = result['messages']
            errs = result['errors']
            for (var index in msgs){
                $("#messages").append("<div class='alert alert-warning'>"+msgs[index]+"</div>");
            };
            for (var index in errs){
                $("#messages").append("<div class='alert alert-danger'>"+errs[index]+"</div>");
            };
            console.log(result);
        }
    });
});
