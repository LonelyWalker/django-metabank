$(function(){
  var slot_template = _.template($("#slot-template").html(), null, {variable:'slot'});

  function render_slot(slot){
    var new_slot = slot_template(slot);
    var old_slot = $("#slot-"+slot.id);
    if (old_slot[0]){
      old_slot.replaceWith(new_slot);
    } else {
      $("#slots").append(new_slot);
    }
  };

  var lock=false;
  function update(){
    if (lock)
      return;
    lock=true;
    $.ajax({
      url:'/status/chip-info/data/',
      dataType: 'json',
      success: function (data) {
        lock=false;
        if (data)
          _.each(data.slots, render_slot);
      }
    });
  };
  update();
  setInterval(update, 3000);
});
