document.addEventListener("DOMContentLoaded", function () {
    const filterDiv = document.getElementById("changelist-filter");
    const slot = document.getElementById("filters-toggle-slot");

    if (!filterDiv || !slot) return;

    const bar = slot.closest(".auto-refresh-controls");
    const i18n = window.adminFiltersI18n || {
        showFilters: "Show Filters",
        hideFilters: "Hide Filters"
    };

    const toggleBtn = document.createElement("button");
    toggleBtn.className = "celery-logs-toggle-filters";
    toggleBtn.type = "button";
    toggleBtn.textContent = i18n.showFilters;
    slot.appendChild(toggleBtn);

    // Render filters below the gray bar instead of the right-hand sidebar.
    filterDiv.classList.add("celery-logs-filters", "hidden");
    bar.parentNode.insertBefore(filterDiv, bar.nextSibling);
    document.body.classList.add("hidden-filters");

    function setHidden(hidden) {
        filterDiv.classList.toggle("hidden", hidden);
        document.body.classList.toggle("hidden-filters", hidden);
        toggleBtn.textContent = hidden ? i18n.showFilters : i18n.hideFilters;
        localStorage.setItem("admin-filters-hidden", hidden ? "true" : "false");
    }

    toggleBtn.addEventListener("click", function () {
        setHidden(!filterDiv.classList.contains("hidden"));
    });
});
