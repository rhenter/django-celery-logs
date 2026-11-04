document.addEventListener("DOMContentLoaded", function () {
    const filterDiv = document.getElementById("changelist-filter");
    const slot = document.getElementById("filters-toggle-slot");

    if (!filterDiv || !slot) return;

    const storageKey = "admin-filters-hidden";
    const i18n = window.adminFiltersI18n || {
        showFilters: "Show Filters",
        hideFilters: "Hide Filters"
    };

    const toggleBtn = document.createElement("button");
    toggleBtn.className = "celery-logs-toggle-filters";
    toggleBtn.type = "button";
    slot.appendChild(toggleBtn);

    function setHidden(hidden, persist) {
        filterDiv.classList.toggle("hidden", hidden);
        document.body.classList.toggle("hidden-filters", hidden);
        toggleBtn.textContent = hidden ? i18n.showFilters : i18n.hideFilters;
        if (persist) localStorage.setItem(storageKey, hidden ? "true" : "false");
    }

    // Filters stay in the default Django sidebar (visible); the button only toggles them.
    setHidden(localStorage.getItem(storageKey) === "true", false);

    toggleBtn.addEventListener("click", function () {
        setHidden(!filterDiv.classList.contains("hidden"), true);
    });
});
