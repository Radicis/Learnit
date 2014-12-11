
	/* ----  AXAJ call to get randomuser.me JSON object */
$.ajax({
	 //Request 5 results
	  url: 'http://api.randomuser.me/?results=7',
	  dataType: 'json',	 
	  success: function(data){			
		//Iterate through the JSON objects contained in the array data.results
		for(var i=0;i<data.results.length;i++){
			//Target the i+n nthchild and put in img src
			$(".posts li:nth-child(" + (i+1) + ") img").attr("src",data.results[i].user.picture.thumbnail);			
		}
	  }
});

$(document).ready(function(){
	
	$("#makepost").click(function(){
	  $("#right-make-post-inner").slideToggle();
	}); 
	$(".logo").click(function(){
	  $("#main-nav").slideToggle();
	}); 
	
	$('.posts-container').profanityFilter({
    replaceWith: ['fun', 'stuff'],
    customSwears: ['ass'],
    externalSwears: '/static/js/vendor/swearWords.json'
	});
	
	$('.side-content').profanityFilter({
    replaceWith: ['fun', 'stuff'],
    customSwears: ['ass'],
    externalSwears: '/static/js/vendor/swearWords.json'
	});

});
