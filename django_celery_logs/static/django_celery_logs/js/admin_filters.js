document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.createElement("button");
    const filterDiv = document.getElementById("changelist-filter");

    if (!filterDiv) return;

    const i18n = window.adminFiltersI18n || {
        showFilters: "Show Filters",
        hideFilters: "Hide Filters"
    };

    toggleBtn.className = "historylink";
    toggleBtn.textContent = i18n.showFilters;
    toggleBtn.type = "button";

    filterDiv.classList.add("hidden");
    document.body.classList.add("hidden-filters");
    filterDiv.parentNode.insertBefore(toggleBtn, filterDiv);

    toggleBtn.addEventListener("click", function () {
        const currentlyHidden = filterDiv.classList.contains("hidden");

        if (currentlyHidden) {
            filterDiv.classList.remove("hidden");
            document.body.classList.remove("hidden-filters");
            toggleBtn.textContent = i18n.hideFilters;
            localStorage.setItem("admin-filters-hidden", "false");
        } else {
            filterDiv.classList.add("hidden");
            document.body.classList.add("hidden-filters");
            toggleBtn.textContent = i18n.showFilters;
            localStorage.setItem("admin-filters-hidden", "true");
        }
    });
});
