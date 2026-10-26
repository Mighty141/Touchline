document.addEventListener("DOMContentLoaded", function () {
  // Club crests: if the provider's crest URL is empty, stale, or blocked,
  // retry football-data.org's crest CDN using the team's official API ID.
  document.querySelectorAll("img.crest-image").forEach(img => {
    img.addEventListener("error", function () {
      const apiId = img.dataset.apiId;
      if (apiId && img.dataset.crestFallback !== "1") {
        img.dataset.crestFallback = "1";
        img.src = `https://crests.football-data.org/${encodeURIComponent(apiId)}.png`;
        return;
      }
      // Avoid a broken-image icon if neither provider URL works.
      img.style.display = "none";
      img.setAttribute("aria-hidden", "true");
    }, { once: false });
  });
  // JavaScript DOM/events: filter fixtures without reloading the page.
  const buttons = document.querySelectorAll(".btn-filter");
  const cards = document.querySelectorAll(".match-filter-card");
  buttons.forEach(button => button.addEventListener("click", function () {
    buttons.forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    cards.forEach(card => card.classList.toggle("d-none", button.dataset.status !== "ALL" && card.dataset.status !== button.dataset.status));
  }));

  // Small drafting coordinate readout. It does not capture or store cursor data.
  const coordinateReadout = document.getElementById("coordinateReadout");
  if (coordinateReadout && window.matchMedia("(pointer: fine)").matches) {
    document.addEventListener("mousemove", event => {
      coordinateReadout.textContent = `X: ${String(event.clientX).padStart(4, "0")} / Y: ${String(event.clientY).padStart(4, "0")}`;
    }, { passive: true });
  } else if (coordinateReadout) {
    coordinateReadout.textContent = "GRID: 20 PX / MOBILE";
  }

  // jQuery AJAX + JSON: request match data from Django.
  if (window.jQuery) {
    $("#refreshMatches").on("click", function () {
      const btn = $(this); btn.prop("disabled", true).text("Loading match data…");
      $.ajax({url:"/api/matches/", method:"GET", dataType:"json"})
        .done(data => $("#ajaxMessage").text("API RESPONSE: received " + data.matches.length + " matches as JSON. Source: " + data.source + "."))
        .fail(() => $("#ajaxMessage").text("REQUEST FAILED: could not load match data. Check the Django server."))
        .always(() => btn.prop("disabled", false).text("↻ Refresh match data with AJAX"));
    });
  }
});
