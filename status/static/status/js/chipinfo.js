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

  var statusIcons = {
    W: 'icon-warning-sign',
    I: 'icon-info-sign',
    S: 'icon-ok-sign',
    E: 'icon-exclamation-sign',
    F: 'icon-exclamation-sign'
  };

  function notify(response){
    var $notifs = $('.page-header .navbar-inner .notifications');
    if (!$notifs.length) {
      $notifs = $('<div class="notifications pull-right"></div>').appendTo($('.page-header .navbar-inner'));
    }
    var alert = $('<div class="alert"></div>')
      .append('<a href="#" class="close" data-dismiss="alert">&times;</a>')
      .append('<i class="'+statusIcons[response.STATUS]+'" />')
      .append(' ' + response.Msg);
    $notifs.append(alert);
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

  $(document).on('click', '.chip-info a.set-bits', function(e){
    var url = $(this).attr('href');
    $.ajax(url, {
      type: 'POST',
      success: notify,
      error: function(jqXHR, textStatus, errorThrown){
        notify({STATUS: 'E',
                Msg: errorThrown});
      }
    });
    return false;
  });
});
