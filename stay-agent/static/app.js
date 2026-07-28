// TripVerse Stay Agent JavaScript Implementation
document.addEventListener("DOMContentLoaded", () => {
    // API base URL
    const API_BASE = "";

    // App state
    let currentStay = null;
    let activeHotel = null;
    let selectedHotelsForCompare = [];
    let map = null;
    let mapMarkers = [];
    let activeTravelStyle = "Adventure";
    let activeAccommodation = "Hotel";
    let allStaysHistory = [];

    // Currency Mappings
    const EXCHANGE_RATES = {
        USD: 1.0,
        INR: 85.0,
        EUR: 0.92,
        JPY: 155.0,
        THB: 36.2,
        GBP: 0.78
    };
    
    const CURRENCY_SYMBOLS = {
        USD: "$",
        INR: "₹",
        EUR: "€",
        JPY: "¥",
        THB: "฿",
        GBP: "£"
    };

    // DOM Elements
    const sidebar = document.getElementById("sidebar");
    const openSidebarBtn = document.getElementById("openSidebar");
    const closeSidebarBtn = document.getElementById("closeSidebar");
    const historyList = document.getElementById("historyList");
    const historySearch = document.getElementById("historySearch");
    const filterBookmarked = document.getElementById("filterBookmarked");
    const showStatsBtn = document.getElementById("showStatsBtn");
    
    const stayForm = document.getElementById("stayForm");
    const guestMinus = document.getElementById("guestMinus");
    const guestPlus = document.getElementById("guestPlus");
    const guestsInput = document.getElementById("guests");
    const travelStyleSelector = document.getElementById("travelStyleSelector");
    
    const loadingPanel = document.getElementById("loadingPanel");
    const errorPanel = document.getElementById("errorPanel");
    const errorMessage = document.getElementById("errorMessage");
    
    const resultsPanel = document.getElementById("resultsPanel");
    const resDestination = document.getElementById("resDestination");
    const resDates = document.getElementById("resDates");
    const resArea = document.getElementById("resArea");
    const resAreaReason = document.getElementById("resAreaReason");
    const resTotalCost = document.getElementById("resTotalCost");
    
    const hotelsContainer = document.getElementById("hotelsContainer");
    const tipsContainer = document.getElementById("tipsContainer");
    
    const sliderDining = document.getElementById("sliderDining");
    const sliderTransit = document.getElementById("sliderTransit");
    const sliderActivities = document.getElementById("sliderActivities");
    const valDining = document.getElementById("valDining");
    const valTransit = document.getElementById("valTransit");
    const valActivities = document.getElementById("valActivities");
    
    const exportBtn = document.getElementById("exportBtn");
    const bookmarkBtn = document.getElementById("bookmarkBtn");
    const notesToggleBtn = document.getElementById("notesToggleBtn");
    const notesPanel = document.getElementById("notesPanel");
    const personalNotesInput = document.getElementById("personalNotesInput");
    const saveNotesBtn = document.getElementById("saveNotesBtn");
    const starRatingInput = document.getElementById("starRatingInput");
    const deletePlanBtn = document.getElementById("deletePlanBtn");
    
    const comparisonSection = document.getElementById("comparisonSection");
    const comparisonTable = document.getElementById("comparisonTable");
    
    const statsModal = document.getElementById("statsModal");
    const closeStatsBtn = document.getElementById("closeStatsBtn");
    const statTotalPlanned = document.getElementById("statTotalPlanned");
    const statBookmarked = document.getElementById("statBookmarked");
    const statAvgRating = document.getElementById("statAvgRating");
    const popularDestinationsList = document.getElementById("popularDestinationsList");

    const preferredCurrencySelect = document.getElementById("currency");

    /* ==========================================================================
       Sidebar Controls & Responsiveness
       ========================================================================== */
    openSidebarBtn.addEventListener("click", () => {
        sidebar.classList.remove("collapsed");
    });

    closeSidebarBtn.addEventListener("click", () => {
        sidebar.classList.add("collapsed");
    });

    const handleResize = () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove("collapsed");
        } else {
            sidebar.classList.add("collapsed");
        }
    };
    window.addEventListener("resize", handleResize);
    handleResize(); // Initial call

    /* ==========================================================================
       Form Input Event Listeners
       ========================================================================== */
    // Date minimums (prevent check-out before check-in)
    const todayStr = new Date().toISOString().split("T")[0];
    document.getElementById("checkin").min = todayStr;
    document.getElementById("checkout").min = todayStr;

    document.getElementById("checkin").addEventListener("change", (e) => {
        document.getElementById("checkout").min = e.target.value;
    });

    // Guest counter
    guestMinus.addEventListener("click", () => {
        let val = parseInt(guestsInput.value);
        if (val > 1) {
            guestsInput.value = val - 1;
            updateTicketVisuals();
        }
    });

    guestPlus.addEventListener("click", () => {
        let val = parseInt(guestsInput.value);
        if (val < 10) {
            guestsInput.value = val + 1;
            updateTicketVisuals();
        }
    });

    // Travel Style selectors
    travelStyleSelector.addEventListener("click", (e) => {
        if (e.target.classList.contains("badge-btn")) {
            travelStyleSelector.querySelectorAll(".badge-btn").forEach(btn => btn.classList.remove("active"));
            e.target.classList.add("active");
            activeTravelStyle = e.target.getAttribute("data-value");
            updateTicketVisuals();
        }
    });

    // Destination and budget listeners
    document.getElementById("destination").addEventListener("input", updateTicketVisuals);
    document.getElementById("budget").addEventListener("change", updateTicketVisuals);
    preferredCurrencySelect.addEventListener("change", () => {
        updateTicketVisuals();
        updateDisplayedPrices();
    });

    /* ==========================================================================
       Database & History Fetchers
       ========================================================================== */
    async function loadHistory() {
        try {
            const searchQuery = historySearch.value.trim();
            const favoritesOnly = filterBookmarked.checked;
            
            let url = `${API_BASE}/stays?`;
            if (searchQuery) url += `search=${encodeURIComponent(searchQuery)}&`;
            if (favoritesOnly) url += `bookmarked=true&`;

            const res = await fetch(url);
            if (!res.ok) throw new Error("Could not fetch stays history.");
            
            allStaysHistory = await res.json();
            renderHistoryList(allStaysHistory);
        } catch (err) {
            console.error(err);
            historyList.innerHTML = `<div class="loading-history text-danger"><i class="fa-solid fa-circle-exclamation"></i> Error loading history</div>`;
        }
    }

    function renderHistoryList(items) {
        if (items.length === 0) {
            historyList.innerHTML = `<div class="loading-history">No stays found</div>`;
            return;
        }

        historyList.innerHTML = "";
        items.forEach(item => {
            const dateStr = `${item.checkin} to ${item.checkout}`;
            const ratingStars = Array(5).fill(0).map((_, i) => 
                `<i class="${i < item.rating ? 'fa-solid' : 'fa-regular'} fa-star"></i>`
            ).join("");

            const div = document.createElement("div");
            div.className = `history-item ${currentStay && currentStay.id === item.id ? 'active' : ''}`;
            div.innerHTML = `
                <div class="history-item-header">
                    <div class="history-dest">${escapeHtml(item.destination)}</div>
                    ${item.is_bookmarked ? '<span class="history-bookmark-badge"><i class="fa-solid fa-bookmark"></i></span>' : ''}
                </div>
                <div class="history-meta">
                    <span>${dateStr}</span>
                    <div class="history-stars">${ratingStars}</div>
                </div>
            `;
            
            div.addEventListener("click", () => {
                document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
                div.classList.add("active");
                displayStay(item);
                
                if (window.innerWidth <= 768) {
                    sidebar.classList.add("collapsed");
                }
            });
            
            historyList.appendChild(div);
        });
    }

    // Live search and bookmark filter
    historySearch.addEventListener("input", debounce(loadHistory, 300));
    filterBookmarked.addEventListener("change", loadHistory);

    /* ==========================================================================
       AI Generation & Planning Loader
       ========================================================================== */
    stayForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const destination = document.getElementById("destination").value.trim();
        const checkin = document.getElementById("checkin").value;
        const checkout = document.getElementById("checkout").value;
        const guests = parseInt(guestsInput.value);
        const budget = document.getElementById("budget").value;
        const requirements = document.getElementById("requirements").value.trim();

        resultsPanel.classList.add("hidden");
        errorPanel.classList.add("hidden");
        loadingPanel.classList.remove("hidden");
        comparisonSection.classList.add("hidden");
        selectedHotelsForCompare = [];
        
        loadingPanel.scrollIntoView({ behavior: "smooth" });

        try {
            const response = await fetch(`${API_BASE}/stay`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    destination,
                    checkin,
                    checkout,
                    guests,
                    budget,
                    travel_style: activeTravelStyle,
                    accommodation: activeAccommodation,
                    requirements
                })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || "Failed to generate stay plan.");
            }

            const data = await response.json();
            
            // Reload sidebar history and load this new stay
            await loadHistory();
            displayStay(data);
        } catch (err) {
            console.error(err);
            errorMessage.textContent = err.message;
            errorPanel.classList.remove("hidden");
        } finally {
            loadingPanel.classList.add("hidden");
        }
    });

    /* ==========================================================================
       Stay Presentation Rendering
       ========================================================================== */
    function displayStay(stay) {
        currentStay = stay;
        
        // Ensure active class on sidebar item
        document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
        // Render results
        resDestination.textContent = stay.destination;
        
        const dateOptions = { month: 'short', day: 'numeric', year: 'numeric' };
        const d1 = new Date(stay.checkin);
        const d2 = new Date(stay.checkout);
        const dateRangeStr = `${d1.toLocaleDateString('en-US', dateOptions)} - ${d2.toLocaleDateString('en-US', dateOptions)} (${stay.guests} guests)`;
        resDates.textContent = dateRangeStr;
        
        resArea.textContent = stay.recommended_area || "Center";
        resAreaReason.textContent = stay.area_reason || "";
        
        // Reset and populate personal notes
        personalNotesInput.value = stay.notes || "";
        renderStarRating(stay.rating || 0);
        notesPanel.classList.add("hidden");
        notesToggleBtn.classList.remove("active");
        
        // Setup bookmark button state
        updateBookmarkIcon(stay.is_bookmarked);

        // Render climate forecast
        renderWeatherDetails(stay.destination, stay.checkin);
        
        // Render packing checklist based on Travel Style
        renderPackingChecklist(stay.travel_style || activeTravelStyle);

        // Initialize active hotel for calculator
        activeHotel = stay.hotels && stay.hotels.length > 0 ? stay.hotels[0] : null;

        // Populate Slider baseline values (handling ranges)
        let costStr = stay.estimated_total_cost || "600";
        let parts = costStr.split("-");
        let firstPart = parts[0].replace(/[^0-9]/g, "");
        let baseCost = parseInt(firstPart) || 600;
        currentStay.baseline_cost = baseCost; // Attach dynamically for sliders
        resetCostCalculator();

        // Hotels Grid Population
        hotelsContainer.innerHTML = "";
        const hotels = stay.hotels || [];
        
        hotels.forEach((hotel, idx) => {
            const reviewsHtml = (hotel.reviews || []).map(r => `
                <div class="review-item">
                    <div class="review-header">
                        <span class="review-author"><i class="fa-regular fa-user"></i> ${escapeHtml(r.author || "Guest")}</span>
                        <span class="review-rating">
                            ${Array(Math.max(1, Math.min(5, Math.round(parseFloat(r.rating || 5))))).fill(0).map(() => '<i class="fa-solid fa-star"></i>').join("")}
                        </span>
                    </div>
                    <div class="review-comment">"${escapeHtml(r.comment)}"</div>
                </div>
            `).join("");

            const bookingSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(hotel.name + " " + stay.destination + " Booking")}`;
            const usdPrice = parseInt(hotel.price_per_night.replace(/[^0-9]/g, "")) || 100;
            const selCurrency = preferredCurrencySelect.value;
            const currencyRate = EXCHANGE_RATES[selCurrency] || 1.0;
            const currencySymbol = CURRENCY_SYMBOLS[selCurrency] || "$";
            const convertedPrice = Math.round(usdPrice * currencyRate);

            const card = document.createElement("div");
            card.className = `hotel-card ${idx === 0 ? 'active-calculator' : ''}`;
            card.innerHTML = `
                <div class="hotel-card-header">
                    <div class="hotel-title-row">
                        <h4 class="hotel-name">${escapeHtml(hotel.name)}</h4>
                        <span class="hotel-price">${currencySymbol}${convertedPrice.toLocaleString()}/nt</span>
                    </div>
                    <div class="hotel-meta-row">
                        <div class="hotel-stars"><i class="fa-solid fa-star"></i> ${escapeHtml(hotel.rating || "4.5/5")}</div>
                        <span><i class="fa-solid fa-train-subway"></i> ${escapeHtml(hotel.nearest_transport || "Transit nearby")}</span>
                    </div>
                </div>
                
                <div class="hotel-body">
                    <p class="hotel-reason">${escapeHtml(hotel.reason)}</p>
                    
                    <ul class="detail-list">
                        <li><i class="fa-solid fa-location-arrow"></i> <span><strong>Nearby:</strong> ${escapeHtml((hotel.nearby_places || []).join(", "))}</span></li>
                    </ul>
                    
                    <div class="pros-cons-grid">
                        <div class="pros-box">
                            <span>Pros</span>
                            <ul>
                                ${(hotel.pros || []).map(p => `<li><i class="fa-solid fa-check"></i> ${escapeHtml(p)}</li>`).join("")}
                            </ul>
                        </div>
                        <div class="cons-box">
                            <span>Cons</span>
                            <ul>
                                ${(hotel.cons || []).map(c => `<li><i class="fa-solid fa-xmark"></i> ${escapeHtml(c)}</li>`).join("")}
                            </ul>
                        </div>
                    </div>

                    <div class="reviews-section-wrapper">
                        <h4>Guest Diary Entries</h4>
                        ${reviewsHtml || '<p class="text-muted" style="font-size:0.7rem; font-style:italic;">No reviews posted yet.</p>'}
                    </div>
                </div>
                
                <div class="hotel-footer">
                    <button class="btn btn-secondary btn-small btn-map-focus"><i class="fa-solid fa-location-crosshairs"></i> Map</button>
                    <a href="${bookingSearchUrl}" target="_blank" class="btn btn-primary btn-small text-center" style="text-decoration:none;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Book</a>
                </div>
            `;
            
            // Map focus listener
            card.querySelector(".btn-map-focus").addEventListener("click", (e) => {
                e.stopPropagation();
                focusHotelOnMap(hotel);
            });

            // Card click listener for matrix comparison & cost calculator focusing
            card.addEventListener("click", () => {
                // Focus this hotel in cost calculator
                activeHotel = hotel;
                document.querySelectorAll(".hotel-card").forEach(el => el.classList.remove("active-calculator"));
                card.classList.add("active-calculator");
                recalculateCost();

                toggleHotelForComparison(hotel, card);
            });
            
            hotelsContainer.appendChild(card);
        });

        // Setup tips container
        tipsContainer.innerHTML = "";
        const tips = stay.travel_tips || [];
        if (tips.length === 0) {
            tipsContainer.innerHTML = "<li><i class='fa-solid fa-circle-info'></i> Check travel regulations before flying.</li>";
        } else {
            tips.forEach(tip => {
                const li = document.createElement("li");
                li.innerHTML = `<i class="fa-solid fa-compass"></i> <span>${escapeHtml(tip)}</span>`;
                tipsContainer.appendChild(li);
            });
        }

        // Initialize Map & Markers
        initMapForDestination(stay.destination, stay.hotels);

        // Show Results
        resultsPanel.classList.remove("hidden");
        resultsPanel.scrollIntoView({ behavior: "smooth" });
    }

    /* ==========================================================================
       Currency Converter Widget Implementation
       ========================================================================== */
    const convertAmountInput = document.getElementById("convertAmount");
    const convertFromSelect = document.getElementById("convertFrom");
    const convertToSelect = document.getElementById("convertTo");
    const convertResultDiv = document.getElementById("convertResult");

    function runCurrencyConverter() {
        if (!convertAmountInput || !convertFromSelect || !convertToSelect || !convertResultDiv) return;

        const amount = parseFloat(convertAmountInput.value) || 0;
        const from = convertFromSelect.value;
        const to = convertToSelect.value;

        if (amount <= 0) {
            convertResultDiv.textContent = "Enter positive amount";
            return;
        }

        const rateFrom = EXCHANGE_RATES[from] || 1.0;
        const rateTo = EXCHANGE_RATES[to] || 1.0;

        // Convert base to USD first, then to target
        const amountInUSD = amount / rateFrom;
        const converted = amountInUSD * rateTo;

        const fromSym = CURRENCY_SYMBOLS[from] || from;
        const toSym = CURRENCY_SYMBOLS[to] || to;

        convertResultDiv.textContent = `${fromSym}${amount.toLocaleString()} = ${toSym}${converted.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    convertAmountInput.addEventListener("input", runCurrencyConverter);
    convertFromSelect.addEventListener("change", runCurrencyConverter);
    convertToSelect.addEventListener("change", runCurrencyConverter);
    runCurrencyConverter(); // Initial call

    function updateDisplayedPrices() {
        if (!currentStay) return;
        recalculateCost();

        const selCurrency = preferredCurrencySelect.value;
        const rate = EXCHANGE_RATES[selCurrency] || 1.0;
        const symbol = CURRENCY_SYMBOLS[selCurrency] || "$";

        const cards = hotelsContainer.querySelectorAll(".hotel-card");
        if (cards.length === currentStay.hotels.length) {
            currentStay.hotels.forEach((hotel, idx) => {
                const card = cards[idx];
                const priceSpan = card.querySelector(".hotel-price");
                if (priceSpan) {
                    const usdPrice = parseInt(hotel.price_per_night.replace(/[^0-9]/g, "")) || 100;
                    const convertedPrice = Math.round(usdPrice * rate);
                    priceSpan.textContent = `${symbol}${convertedPrice.toLocaleString()}/nt`;
                }
            });
        }
        renderComparisonMatrix();
    }

    /* ==========================================================================
       Cost Calculator recalculations
       ========================================================================== */
    function recalculateCost() {
        if (!currentStay) return;
        
        // Calculate number of nights
        const checkinDate = new Date(currentStay.checkin);
        const checkoutDate = new Date(currentStay.checkout);
        const nights = Math.max(1, Math.round((checkoutDate - checkinDate) / (1000 * 60 * 60 * 24)));
        
        // Extract hotel price
        let hotelPrice = 100;
        if (activeHotel && activeHotel.price_per_night) {
            hotelPrice = parseInt(activeHotel.price_per_night.replace(/[^0-9]/g, "")) || 100;
        } else if (currentStay.hotels && currentStay.hotels.length > 0) {
            hotelPrice = parseInt(currentStay.hotels[0].price_per_night.replace(/[^0-9]/g, "")) || 100;
        }
        
        const lodgingCost = hotelPrice * nights;
        
        // Sliders
        const diningVal = parseInt(sliderDining.value);
        const transitVal = parseInt(sliderTransit.value);
        const activitiesVal = parseInt(sliderActivities.value);
        
        const diningLabels = ["Low-cost / Street", "Standard / Cafes", "Fine Dining / Luxe"];
        const transitLabels = ["Walking / Bus", "Metro Subway", "Taxi / Car Rental"];
        const activitiesLabels = ["Free sights", "Moderate tours", "Premium events"];
        
        valDining.textContent = diningLabels[diningVal - 1];
        valTransit.textContent = transitLabels[transitVal - 1];
        valActivities.textContent = activitiesLabels[activitiesVal - 1];
        
        // Dining cost per guest per day
        const diningPerDayPerGuest = diningVal === 1 ? 15 : (diningVal === 3 ? 100 : 40);
        const diningCost = diningPerDayPerGuest * currentStay.guests * nights;
        
        // Transit cost per day
        const transitPerDay = transitVal === 1 ? 5 : (transitVal === 3 ? 50 : 15);
        const transitCost = transitPerDay * currentStay.guests * nights;
        
        // Activities cost per guest per day
        const activitiesPerDayPerGuest = activitiesVal === 1 ? 0 : (activitiesVal === 3 ? 80 : 25);
        const activitiesCost = activitiesPerDayPerGuest * currentStay.guests * nights;
        
        const usdTotal = lodgingCost + diningCost + transitCost + activitiesCost;
        
        // Convert to preferred currency
        const selCurrency = preferredCurrencySelect.value;
        const rate = EXCHANGE_RATES[selCurrency] || 1.0;
        const symbol = CURRENCY_SYMBOLS[selCurrency] || "$";
        const convertedTotal = Math.round(usdTotal * rate);

        resTotalCost.textContent = `${symbol}${convertedTotal.toLocaleString()}`;
    }
    
    function resetCostCalculator() {
        sliderDining.value = 2;
        sliderTransit.value = 2;
        sliderActivities.value = 2;
        recalculateCost();
    }

    sliderDining.addEventListener("input", recalculateCost);
    sliderTransit.addEventListener("input", recalculateCost);
    sliderActivities.addEventListener("input", recalculateCost);

    /* ==========================================================================
       Weather & Climate Generator helper
       ========================================================================== */
    function renderWeatherDetails(destination, dateStr) {
        const weatherDisplay = document.getElementById("weatherDisplay");
        const weatherNote = document.getElementById("weatherNote");
        if (!weatherDisplay) return;

        const date = new Date(dateStr);
        const month = date.getMonth(); // 0-11
        
        // Deterministic temperatures based on months and region keywords
        let temp = 22;
        let condition = "Sunny";
        let icon = "fa-sun";

        const lowerDest = destination.toLowerCase();
        if (lowerDest.includes("tokyo") || lowerDest.includes("japan")) {
            const temps = [6, 7, 10, 15, 20, 23, 27, 28, 24, 19, 13, 8];
            temp = temps[month];
            condition = month >= 5 && month <= 8 ? "Humid / Rainy" : "Clear Sky";
            icon = month >= 5 && month <= 8 ? "fa-cloud-showers-heavy" : "fa-sun";
        } else if (lowerDest.includes("paris") || lowerDest.includes("france") || lowerDest.includes("london") || lowerDest.includes("uk")) {
            const temps = [5, 6, 9, 12, 16, 19, 21, 21, 18, 13, 9, 6];
            temp = temps[month];
            condition = month >= 9 || month <= 2 ? "Chilly / Overcast" : "Mild Breezes";
            icon = month >= 9 || month <= 2 ? "fa-cloud" : "fa-cloud-sun";
        } else if (lowerDest.includes("phuket") || lowerDest.includes("thailand") || lowerDest.includes("bangkok")) {
            temp = 29;
            condition = month >= 5 && month <= 10 ? "Monsoon / Rainy" : "Tropical Warmth";
            icon = month >= 5 && month <= 10 ? "fa-cloud-showers-water" : "fa-sun";
        } else if (lowerDest.includes("new york") || lowerDest.includes("newyork") || lowerDest.includes("usa")) {
            const temps = [2, 3, 7, 13, 18, 23, 26, 25, 21, 15, 9, 4];
            temp = temps[month];
            condition = month >= 11 || month <= 2 ? "Cold / Snow Risk" : "Sunny days";
            icon = month >= 11 || month <= 2 ? "fa-snowflake" : "fa-sun";
        }

        weatherDisplay.innerHTML = `
            <span class="weather-temp">${temp}°C</span>
            <span class="weather-cond"><i class="fa-solid ${icon} weather-icon"></i> ${condition}</span>
        `;
        weatherNote.textContent = `Typical climate stats for ${destination} during ${date.toLocaleString('en-US', { month: 'long' })}.`;
    }

    /* ==========================================================================
       Packing Checklist generator
       ========================================================================== */
    function renderPackingChecklist(style) {
        const container = document.getElementById("packingContainer");
        if (!container) return;

        container.innerHTML = "";
        
        const styleItems = {
            Adventure: ["Hiking boots", "Quick-dry towel", "Hydration backpack", "Rainproof jacket", "Polarized sunglasses", "Heavy-duty power bank"],
            Luxury: ["Designer sunglasses", "Fine dinner attire", "Luxury swim apparel", "Scented travel kit", "Leather travel journal", "Noise-cancelling headphones"],
            Family: ["Emergency first-aid pack", "Kids snack bars", "Antibacterial wet wipes", "Multi-port USB charger", "Compact travel boardgames", "Family insurance cards"],
            Relaxation: ["Beach sandals", "Sunscreen (SPF 50+)", "Breathable linen shorts", "E-reader/Novel", "Double-insulated water flask", "Floppy sunhat"]
        };

        const list = styleItems[style] || styleItems["Adventure"];
        list.forEach((item, index) => {
            const li = document.createElement("li");
            const id = `pack_${index}`;
            li.innerHTML = `
                <input type="checkbox" id="${id}">
                <label for="${id}"><span>${escapeHtml(item)}</span></label>
            `;
            
            const checkbox = li.querySelector("input");
            checkbox.addEventListener("change", () => {
                if (checkbox.checked) {
                    li.classList.add("checked");
                } else {
                    li.classList.remove("checked");
                }
            });
            
            container.appendChild(li);
        });
    }

    /* ==========================================================================
       Ticket Visual Sync helpers
       ========================================================================== */
    function updateTicketVisuals() {
        const destInput = document.getElementById("destination").value.trim();
        const ticketDestDisplay = document.getElementById("ticketDestDisplay");
        const ticketStyleDisplay = document.getElementById("ticketStyleDisplay");
        const ticketMetaDisplay = document.getElementById("ticketMetaDisplay");
        const ticketDestCode = document.getElementById("ticketDestCode");
        const budgetSelect = document.getElementById("budget");
        
        if (ticketDestDisplay) {
            ticketDestDisplay.textContent = destInput ? `STAY: ${destInput.toUpperCase()}` : "STAY: PENDING";
        }
        
        if (ticketDestCode) {
            if (destInput) {
                const cleanDest = destInput.replace(/[^a-zA-Z]/g, "");
                ticketDestCode.textContent = cleanDest.substring(0, 3).toUpperCase();
            } else {
                ticketDestCode.textContent = "ARR";
            }
        }
        
        if (ticketStyleDisplay) {
            ticketStyleDisplay.textContent = activeTravelStyle.toUpperCase();
        }
        
        if (ticketMetaDisplay) {
            const guests = guestsInput.value;
            const budgetText = budgetSelect.options[budgetSelect.selectedIndex]?.text || "MID-RANGE";
            const budgetClean = budgetText.split(" ")[0].toUpperCase();
            const curr = preferredCurrencySelect.value;
            ticketMetaDisplay.textContent = `GUESTS: ${guests} | BUDGET: ${budgetClean} | CURR: ${curr}`;
        }
    }

    /* ==========================================================================
       Explorer Map & Coordinates Handler
       ========================================================================== */
    function initMapForDestination(destination, hotels) {
        const mapContainer = document.getElementById("map");
        if (!mapContainer) return;

        // Clear existing map instance
        if (map) {
            map.remove();
            map = null;
            mapMarkers = [];
        }

        // Initialize standard map centering coordinates (Default Paris)
        let lat = 48.8566;
        let lon = 2.3522;
        let zoom = 13;

        // Leaflet geocode lookup logic based on text matches
        const lowerDest = destination.toLowerCase();
        if (lowerDest.includes("tokyo") || lowerDest.includes("japan")) {
            lat = 35.6762; lon = 139.6503;
        } else if (lowerDest.includes("london") || lowerDest.includes("uk") || lowerDest.includes("united kingdom")) {
            lat = 51.5074; lon = -0.1278;
        } else if (lowerDest.includes("phuket") || lowerDest.includes("thailand")) {
            lat = 7.8804; lon = 98.3923; zoom = 11;
        } else if (lowerDest.includes("new york") || lowerDest.includes("newyork") || lowerDest.includes("usa")) {
            lat = 40.7128; lon = -74.0060;
        }

        // Initialize Map
        map = L.map('map').setView([lat, lon], zoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; OpenStreetMap contributors'
        }).addTo(map);

        // Add pins for recommended hotels offset slightly for visibility
        (hotels || []).forEach((hotel, idx) => {
            const offsetLat = lat + (Math.sin(idx * 2) * 0.006);
            const offsetLon = lon + (Math.cos(idx * 2) * 0.006);
            hotel.lat = offsetLat; // Save coordinates for centering focuses
            hotel.lon = offsetLon;

            const marker = L.marker([offsetLat, offsetLon]).addTo(map);
            marker.bindPopup(`<strong>${escapeHtml(hotel.name)}</strong><br>${escapeHtml(hotel.price_per_night)}/night`);
            
            mapMarkers.push(marker);
        });
    }

    function focusHotelOnMap(hotel) {
        if (map && hotel.lat && hotel.lon) {
            map.setView([hotel.lat, hotel.lon], 15);
            // Find marker to open its popup
            mapMarkers.forEach(marker => {
                const pos = marker.getLatLng();
                if (Math.abs(pos.lat - hotel.lat) < 0.0001 && Math.abs(pos.lng - hotel.lon) < 0.0001) {
                    marker.openPopup();
                }
            });
        }
    }

    /* ==========================================================================
       Comparison Matrix Operations
       ========================================================================== */
    function toggleHotelForComparison(hotel, cardElement) {
        const index = selectedHotelsForCompare.findIndex(h => h.name === hotel.name);
        
        if (index > -1) {
            selectedHotelsForCompare.splice(index, 1);
            cardElement.classList.remove("selected-compare");
        } else {
            if (selectedHotelsForCompare.length >= 3) {
                alert("You can select up to 3 hotels for side-by-side comparison.");
                return;
            }
            selectedHotelsForCompare.push(hotel);
            cardElement.classList.add("selected-compare");
        }

        renderComparisonMatrix();
    }

    function renderComparisonMatrix() {
        if (selectedHotelsForCompare.length === 0) {
            comparisonSection.classList.add("hidden");
            return;
        }

        comparisonSection.classList.remove("hidden");
        comparisonTable.innerHTML = "";

        // Build side by side comparison rows
        let headers = `<tr><th>Specifications</th>`;
        selectedHotelsForCompare.forEach(hotel => {
            headers += `<th>${escapeHtml(hotel.name)}</th>`;
        });
        headers += `</tr>`;

        let priceRow = `<tr><td><strong>Price / Night</strong></td>`;
        selectedHotelsForCompare.forEach(hotel => {
            const usdPrice = parseInt(hotel.price_per_night.replace(/[^0-9]/g, "")) || 100;
            const selCurrency = preferredCurrencySelect.value;
            const currencyRate = EXCHANGE_RATES[selCurrency] || 1.0;
            const currencySymbol = CURRENCY_SYMBOLS[selCurrency] || "$";
            const convertedPrice = Math.round(usdPrice * currencyRate);
            priceRow += `<td><span class='hotel-price'>${currencySymbol}${convertedPrice.toLocaleString()}</span></td>`;
        });
        priceRow += `</tr>`;

        let ratingRow = `<tr><td><strong>Rating Score</strong></td>`;
        selectedHotelsForCompare.forEach(hotel => {
            ratingRow += `<td><i class='fa-solid fa-star text-warning'></i> ${escapeHtml(hotel.rating || "4.5/5")}</td>`;
        });
        ratingRow += `</tr>`;

        let transportRow = `<tr><td><strong>Nearest Transport</strong></td>`;
        selectedHotelsForCompare.forEach(hotel => {
            transportRow += `<td>${escapeHtml(hotel.nearest_transport || "Walkable subway")}</td>`;
        });
        transportRow += `</tr>`;

        let prosRow = `<tr><td><strong>Top Pro</strong></td>`;
        selectedHotelsForCompare.forEach(hotel => {
            const topPro = hotel.pros && hotel.pros.length > 0 ? hotel.pros[0] : "Location";
            prosRow += `<td style='color:#38b000;'><i class='fa-solid fa-check'></i> ${escapeHtml(topPro)}</td>`;
        });
        prosRow += `</tr>`;

        let consRow = `<tr><td><strong>Main Con</strong></td>`;
        selectedHotelsForCompare.forEach(hotel => {
            const mainCon = hotel.cons && hotel.cons.length > 0 ? hotel.cons[0] : "Parking";
            consRow += `<td style='color:#d00000;'><i class='fa-solid fa-xmark'></i> ${escapeHtml(mainCon)}</td>`;
        });
        consRow += `</tr>`;

        comparisonTable.innerHTML = headers + priceRow + ratingRow + transportRow + prosRow + consRow;
    }

    /* ==========================================================================
       Notes, Star Ratings & Bookmarks CRUD Updates
       ========================================================================== */
    notesToggleBtn.addEventListener("click", () => {
        notesPanel.classList.toggle("hidden");
        notesToggleBtn.classList.toggle("active");
    });

    saveNotesBtn.addEventListener("click", async () => {
        if (!currentStay) return;
        const notes = personalNotesInput.value.trim();

        try {
            const res = await fetch(`${API_BASE}/stays/${currentStay.id}/notes`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ notes })
            });

            if (!res.ok) throw new Error("Could not update notes.");
            
            currentStay.notes = notes;
            alert("Travel journal notes saved!");
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        }
    });

    function renderStarRating(rating) {
        const stars = starRatingInput.querySelectorAll("i");
        stars.forEach(star => {
            const r = parseInt(star.getAttribute("data-rating"));
            if (r <= rating) {
                star.className = "fa-solid fa-star";
            } else {
                star.className = "fa-regular fa-star";
            }
        });
    }

    // Bind rating click listeners
    starRatingInput.querySelectorAll("i").forEach(star => {
        star.addEventListener("click", async () => {
            if (!currentStay) return;
            const rating = parseInt(star.getAttribute("data-rating"));

            try {
                const res = await fetch(`${API_BASE}/stays/${currentStay.id}/rating`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ rating })
                });

                if (!res.ok) throw new Error("Could not update rating score.");
                
                currentStay.rating = rating;
                renderStarRating(rating);
                loadHistory(); // Refresh sidebar list ratings
            } catch (err) {
                console.error(err);
                alert("Error: " + err.message);
            }
        });
    });

    bookmarkBtn.addEventListener("click", async () => {
        if (!currentStay) return;

        try {
            const res = await fetch(`${API_BASE}/stays/${currentStay.id}/bookmark`, {
                method: "POST"
            });

            if (!res.ok) throw new Error("Could not toggle favorite status.");
            
            const data = await res.json();
            currentStay.is_bookmarked = data.is_bookmarked;
            updateBookmarkIcon(data.is_bookmarked);
            loadHistory(); // Sync changes to sidebar lists
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        }
    });

    function updateBookmarkIcon(isBookmarked) {
        if (isBookmarked) {
            bookmarkBtn.innerHTML = `<i class="fa-solid fa-bookmark"></i>`;
            bookmarkBtn.classList.add("active");
        } else {
            bookmarkBtn.innerHTML = `<i class="fa-regular fa-bookmark"></i>`;
            bookmarkBtn.classList.remove("active");
        }
    }

    deletePlanBtn.addEventListener("click", async () => {
        if (!currentStay) return;
        if (!confirm("Are you sure you want to delete this stay plan from your travel logbook?")) return;

        try {
            const res = await fetch(`${API_BASE}/stays/${currentStay.id}`, {
                method: "DELETE"
            });

            if (!res.ok) throw new Error("Could not delete the stay.");

            resultsPanel.classList.add("hidden");
            comparisonSection.classList.add("hidden");
            currentStay = null;
            loadHistory();
            alert("Stay deleted successfully.");
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        }
    });

    // Export JSON
    exportBtn.addEventListener("click", () => {
        if (!currentStay) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentStay, null, 2));
        const dlAnchorElem = document.createElement('a');
        dlAnchorElem.setAttribute("href", dataStr);
        dlAnchorElem.setAttribute("download", `stay_${currentStay.destination.replace(/[^a-zA-Z0-9]/g, "_")}.json`);
        dlAnchorElem.click();
    });

    /* ==========================================================================
       Passport Analytics Dashboard modal dialog
       ========================================================================== */
    showStatsBtn.addEventListener("click", async () => {
        try {
            const res = await fetch(`${API_BASE}/statistics`);
            if (!res.ok) throw new Error("Failed to load planner metrics.");

            const data = await res.json();
            
            statTotalPlanned.textContent = data.total_stays || 0;
            statBookmarked.textContent = data.total_bookmarked || 0;
            statAvgRating.textContent = (data.average_rating || 0).toFixed(1);

            popularDestinationsList.innerHTML = "";
            const dests = data.popular_destinations || [];
            if (dests.length === 0) {
                popularDestinationsList.innerHTML = `<li class="empty-list">No trips planned yet.</li>`;
            } else {
                dests.forEach(item => {
                    const li = document.createElement("li");
                    li.innerHTML = `<span>${escapeHtml(item.destination)}</span> <span class="badge badge-primary">${item.count} stays</span>`;
                    popularDestinationsList.appendChild(li);
                });
            }

            statsModal.classList.remove("hidden");
        } catch (err) {
            console.error(err);
            alert("Error: " + err.message);
        }
    });

    closeStatsBtn.addEventListener("click", () => {
        statsModal.classList.add("hidden");
    });

    /* ==========================================================================
       Global Utility Helper Functions
       ========================================================================= */
    function escapeHtml(str) {
        if (typeof str !== "string") return str;
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /* ==========================================================================
       App Initialization
       ========================================================================= */
    loadHistory(); // Load history sidebar on startup
    updateTicketVisuals(); // Initialize ticket text values on page load
});