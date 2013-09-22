$(function(){
    $("[name=type]").on("change", function myfunction(elem) {
        var value = $("input[name=type]:checked").val();
        $('.textinput').prop('disabled', value === 'dhcp');
    });
});
