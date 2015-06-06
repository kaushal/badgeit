$(function(){
  var canvas = new fabric.Canvas('c1');
  var active = null;
  var symbolCount = 0;
  var defaults = {
  	fill: 'rgba(255,255,255,0.0)',
	top: canvas.getHeight() / 2,
	left: canvas.getWidth() / 2,
	stroke: '#fff',
	borderColor: 'rgba(255,255,255,0.75)',
	cornerColor: 'rgba(255,255,255,0.75)',
	cornerSize: 12,
	transparentCorners: true
  };

  $(document).keyup(function(e)
  {
  	var del = (e.keyCode == 46 || e.keyCode == 8);
  	if (active && del) {
      active.remove();
  	  active = null;
  	  canvas.discardActiveObject();
  	  symbolCount--;
  	}
  });

  canvas.on('object:selected', function(e) {active = e.target;});

  $('.circle').click(function(e) {
  	var shapeDefaults = $.extend({}, defaults);
    var circle = new fabric.Circle($.extend(shapeDefaults, {
    	radius: $(this).data('drawRadius'),
    	strokeWidth: $(this).data('drawRadius') * 0.2,
    	top: defaults.top - $(this).data('drawRadius'),
    	left: defaults.left - $(this).data('drawRadius')
    }));
    canvas.add(circle);
    canvas.setActiveObject(circle);
    active = circle;
    symbolCount++;
  });

  $('.square').click(function(e) {
    var shapeDefaults = $.extend({}, defaults);
    var square = new fabric.Rect($.extend(shapeDefaults, {
    	width: $(this).data('drawWidth'),
    	height: $(this).data('drawHeight'),
    	strokeWidth: $(this).data('drawWidth') * 0.1,
    	top: defaults.top - $(this).data('drawHeight') / 2,
    	left: defaults.left - $(this).data('drawWidth') / 2
    }));
    canvas.add(square);
    canvas.setActiveObject(square);
    active = square;
    symbolCount++;
  });

  $('.triangle').click(function(e) {
    var shapeDefaults = $.extend({}, defaults);
    var triangle = new fabric.Triangle($.extend(shapeDefaults, {
    	width: $(this).data('drawWidth'),
    	height: $(this).data('drawHeight'),
    	strokeWidth: $(this).data('drawWidth') * 0.1,
    	top: defaults.top - $(this).data('drawHeight') / 2,
    	left: defaults.left - $(this).data('drawWidth') / 2
    }));
    canvas.add(triangle);
    canvas.setActiveObject(triangle);
    active = triangle;
    symbolCount++;
  });

  $('.line').click(function(e) {
  	var shapeDefaults = $.extend({}, defaults);
    var line = new fabric.Line($.extend(shapeDefaults, {
    	angle: 30,
    	width: $(this).data('drawWidth'),
    	strokeWidth: $(this).data('drawWidth') * 0.1,
    	top: defaults.top - $(this).data('drawHeight') / 2,
    	left: defaults.left - $(this).data('drawWidth') / 2
    }));
    canvas.add(line);
    canvas.setActiveObject(line);
    active = line;
    symbolCount++;
  });

  $('#challenge-create').submit(function(e)
  {
  	var data = {
	  badgeImage: canvas.toDataURL(),
	  badgeText: $(this).find(':input[name="badge-text"]').val()
	};

  	if (symbolCount > 0 && data.badgeText.trim().length > 0) {
		$.ajax({
		  type: "POST",
  		  url: $(this).attr('action'),
		  data: data,
  		  success: function(msg) {

        	//TODO: Not sure what to do on success.

  		  },
  		  error: function(XMLHttpRequest, textStatus, errorThrown) {
     		alert("Whoops!! Something when wrong when we tried to create your badge.");
  		  }
  		});
	} else {
		alert("You need an image and challenge for your badge!!");
	}
  	e.preventDefault();
  });
});
