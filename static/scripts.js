$(document).ready(function() {
    // Animation du bouton de vote
    $('.btn-primary').hover(function() {
        $(this).animate({opacity: 0.8}, 200);
    }, function() {
        $(this).animate({opacity: 1}, 200);
    });

    // Animation sur les titres
    $('h1, h3').hide().fadeIn(2000);

    // Confirmation pour la soumission du vote
    $('form').on('submit', function() {
        return confirm("Êtes-vous sûr de vouloir soumettre votre vote ?");
    });
});
