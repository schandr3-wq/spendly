// main.js — students will add JavaScript here as features are built

// Size category-breakdown bars from their data-percent attribute
// (keeps templates free of inline styles).
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".cat-bar-fill[data-percent]").forEach(function (bar) {
        bar.style.width = bar.dataset.percent + "%";
    });
});
