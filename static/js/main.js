$(document).ready(function(){
	$("#makepost").click(function(){
	  $("#right-make-post-inner").slideToggle();
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
