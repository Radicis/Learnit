$(document).ready(function(){
	$("#makepost").click(function(){
	  $("#right-make-post-inner").slideToggle();
	}); 
	$('#post-body').profanityFilter({
    replaceWith: ['fun', 'stuff'],
    customSwears: ['ass'],
    externalSwears: '/static/js/vendor/swearWords.json'
	});
	$('.post-body').profanityFilter({
    replaceWith: ['fun', 'stuff'],
    customSwears: ['ass'],
    externalSwears: '/static/js/vendor/swearWords.json'
});
});
