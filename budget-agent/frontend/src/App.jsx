import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8080";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [interests, setInterests] = useState("");
  const [mustInclude, setMustInclude] = useState("");
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeDay, setActiveDay] = useState(0);

  // States for Editing Activities
  const [editingActivityIndex, setEditingActivityIndex] = useState(null);
  const [editingActivityText, setEditingActivityText] = useState("");
  const [newActivityText, setNewActivityText] = useState("");
  const [isAddingActivity, setIsAddingActivity] = useState(false);

  // States for Editing/Regenerating Itinerary Metadata
  const [isEditingMetadata, setIsEditingMetadata] = useState(false);
  const [editDestination, setEditDestination] = useState("");
  const [editDays, setEditDays] = useState("");
  const [editInterests, setEditInterests] = useState("");
  const [editMustInclude, setEditMustInclude] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Recommendations States
  const [recommendations, setRecommendations] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [recsError, setRecsError] = useState(null);

  // Fetch saved trips on component mount
  useEffect(() => {
    fetchTrips();
  }, []);

  // Sync edit form with selected trip and fetch recommendations
  useEffect(() => {
    if (selectedTrip) {
      setEditDestination(selectedTrip.destination || "");
      setEditDays(selectedTrip.days || "");
      setEditInterests(selectedTrip.interests || "");
      setEditMustInclude(selectedTrip.must_include || "");
      setIsEditingMetadata(false);
      setEditingActivityIndex(null);
      setIsAddingActivity(false);
      fetchRecommendations(selectedTrip.id);
    } else {
      setRecommendations([]);
    }
  }, [selectedTrip?.id]);

  async function fetchRecommendations(tripId) {
    setRecsLoading(true);
    setRecsError(null);
    try {
      const res = await axios.get(`${API_BASE}/trips/${tripId}/recommendations`);
      setRecommendations(res.data.recommendations || []);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setRecsError("Could not load local recommendations.");
    } finally {
      setRecsLoading(false);
    }
  }

  async function handleAddRecommendationToDay(rec, dayIndex) {
    const updatedTrip = { ...selectedTrip };
    const itinerary = getDaysList();
    const dayPlan = itinerary[dayIndex];
    if (dayPlan) {
      if (!Array.isArray(dayPlan.activities)) {
        dayPlan.activities = [];
      }
      dayPlan.activities.push(`${rec.name} (${rec.tag}) - ${rec.description}`);
    }

    if (Array.isArray(updatedTrip.plan)) {
      updatedTrip.plan = itinerary;
    } else if (updatedTrip.plan.plan) {
      updatedTrip.plan.plan = itinerary;
    } else if (updatedTrip.plan.itinerary) {
      updatedTrip.plan.itinerary = itinerary;
    }

    try {
      await axios.put(`${API_BASE}/trips/${selectedTrip.id}`, {
        destination: updatedTrip.destination,
        days: updatedTrip.days,
        interests: updatedTrip.interests,
        must_include: updatedTrip.must_include || "",
        plan: updatedTrip.plan
      });
      setSelectedTrip(updatedTrip);
      await fetchTrips();
    } catch (err) {
      console.error("Error adding recommendation to day:", err);
      setError("Failed to add recommendation to day.");
    }
  }

  async function fetchTrips() {
    try {
      const res = await axios.get(`${API_BASE}/trips`);
      setTrips(res.data);
      // If we don't have a selected trip and there are trips, show the latest one
      if (res.data.length > 0 && !selectedTrip) {
        setSelectedTrip(res.data[0]);
        setActiveDay(0);
      }
    } catch (err) {
      console.error("Error fetching trips:", err);
    }
  }

  async function generatePlan(e) {
    e.preventDefault();
    if (!destination.trim() || !days || !interests.trim()) {
      setError("Please fill out all fields.");
      return;
    }
    
    setLoading(true);
    setError(null);
    setSelectedTrip(null);

    try {
      const res = await axios.post(`${API_BASE}/plan`, {
        destination,
        days: Number(days),
        interests,
        must_include: mustInclude
      });
      // The API returns the saved trip including ID
      setSelectedTrip(res.data);
      setActiveDay(0);
      
      // Clear inputs
      setDestination("");
      setDays("");
      setInterests("");
      setMustInclude("");
      
      // Refresh sidebar list
      await fetchTrips();
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || err.message || "An error occurred";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  }

  // --- Plan Editing and Custom Place Additions ---
  async function handleSaveActivityEdit(activityIndex) {
    if (!editingActivityText.trim()) return;

    const updatedTrip = { ...selectedTrip };
    const itinerary = getDaysList();
    const dayPlan = itinerary[activeDay];
    if (dayPlan && Array.isArray(dayPlan.activities)) {
      dayPlan.activities[activityIndex] = editingActivityText.trim();
    }

    if (Array.isArray(updatedTrip.plan)) {
      updatedTrip.plan = itinerary;
    } else if (updatedTrip.plan.plan) {
      updatedTrip.plan.plan = itinerary;
    } else if (updatedTrip.plan.itinerary) {
      updatedTrip.plan.itinerary = itinerary;
    }

    try {
      await axios.put(`${API_BASE}/trips/${selectedTrip.id}`, {
        destination: updatedTrip.destination,
        days: updatedTrip.days,
        interests: updatedTrip.interests,
        must_include: updatedTrip.must_include || "",
        plan: updatedTrip.plan
      });
      setSelectedTrip(updatedTrip);
      setEditingActivityIndex(null);
      setEditingActivityText("");
      await fetchTrips();
    } catch (err) {
      console.error("Error updating activity:", err);
      setError("Failed to update activity.");
    }
  }

  async function handleDeleteActivity(activityIndex) {
    if (!window.confirm("Are you sure you want to delete this activity?")) return;

    const updatedTrip = { ...selectedTrip };
    const itinerary = getDaysList();
    const dayPlan = itinerary[activeDay];
    if (dayPlan && Array.isArray(dayPlan.activities)) {
      dayPlan.activities.splice(activityIndex, 1);
    }

    if (Array.isArray(updatedTrip.plan)) {
      updatedTrip.plan = itinerary;
    } else if (updatedTrip.plan.plan) {
      updatedTrip.plan.plan = itinerary;
    } else if (updatedTrip.plan.itinerary) {
      updatedTrip.plan.itinerary = itinerary;
    }

    try {
      await axios.put(`${API_BASE}/trips/${selectedTrip.id}`, {
        destination: updatedTrip.destination,
        days: updatedTrip.days,
        interests: updatedTrip.interests,
        must_include: updatedTrip.must_include || "",
        plan: updatedTrip.plan
      });
      setSelectedTrip(updatedTrip);
      setEditingActivityIndex(null);
      await fetchTrips();
    } catch (err) {
      console.error("Error deleting activity:", err);
      setError("Failed to delete activity.");
    }
  }

  async function handleAddCustomActivity() {
    if (!newActivityText.trim()) return;

    const updatedTrip = { ...selectedTrip };
    const itinerary = getDaysList();
    const dayPlan = itinerary[activeDay];
    if (dayPlan) {
      if (!Array.isArray(dayPlan.activities)) {
        dayPlan.activities = [];
      }
      dayPlan.activities.push(newActivityText.trim());
    }

    if (Array.isArray(updatedTrip.plan)) {
      updatedTrip.plan = itinerary;
    } else if (updatedTrip.plan.plan) {
      updatedTrip.plan.plan = itinerary;
    } else if (updatedTrip.plan.itinerary) {
      updatedTrip.plan.itinerary = itinerary;
    }

    try {
      await axios.put(`${API_BASE}/trips/${selectedTrip.id}`, {
        destination: updatedTrip.destination,
        days: updatedTrip.days,
        interests: updatedTrip.interests,
        must_include: updatedTrip.must_include || "",
        plan: updatedTrip.plan
      });
      setSelectedTrip(updatedTrip);
      setNewActivityText("");
      setIsAddingActivity(false);
      await fetchTrips();
    } catch (err) {
      console.error("Error adding activity:", err);
      setError("Failed to add custom activity.");
    }
  }

  async function handleSaveMetadata() {
    if (!editDestination.trim() || !editDays || !editInterests.trim()) {
      setError("Please fill out all fields.");
      return;
    }

    const updatedTrip = {
      ...selectedTrip,
      destination: editDestination,
      days: Number(editDays),
      interests: editInterests,
      must_include: editMustInclude
    };

    try {
      await axios.put(`${API_BASE}/trips/${selectedTrip.id}`, {
        destination: updatedTrip.destination,
        days: updatedTrip.days,
        interests: updatedTrip.interests,
        must_include: updatedTrip.must_include || "",
        plan: updatedTrip.plan
      });
      setSelectedTrip(updatedTrip);
      setIsEditingMetadata(false);
      await fetchTrips();
    } catch (err) {
      console.error("Error saving details:", err);
      setError("Failed to update trip details.");
    }
  }

  async function handleRegeneratePlan() {
    if (!editDestination.trim() || !editDays || !editInterests.trim()) {
      setError("Please fill out all fields before regenerating.");
      return;
    }

    setIsRegenerating(true);
    setError(null);

    try {
      const res = await axios.post(`${API_BASE}/trips/${selectedTrip.id}/regenerate`, {
        destination: editDestination,
        days: Number(editDays),
        interests: editInterests,
        must_include: editMustInclude
      });
      setSelectedTrip(res.data);
      setActiveDay(0);
      setIsEditingMetadata(false);
      await fetchTrips();
    } catch (err) {
      console.error("Error regenerating trip:", err);
      const errMsg = err.response?.data?.detail || err.message || "Failed to regenerate trip";
      setError(errMsg);
    } finally {
      setIsRegenerating(false);
    }
  }

  async function handleDelete(id, e) {
    e.stopPropagation(); // Prevent selecting the trip when clicking delete
    if (!window.confirm("Are you sure you want to delete this trip?")) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/trips/${id}`);
      if (selectedTrip && selectedTrip.id === id) {
        setSelectedTrip(null);
      }
      fetchTrips();
    } catch (err) {
      console.error("Error deleting trip:", err);
      setError("Failed to delete trip.");
    }
  }

  const filteredTrips = trips.filter(trip =>
    trip.destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.interests.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Safely extract day-by-day plan list
  const getDaysList = () => {
    if (!selectedTrip || !selectedTrip.plan) return [];
    const itinerary = selectedTrip.plan;
    return Array.isArray(itinerary) ? itinerary : (itinerary.plan || itinerary.itinerary || []);
  };

  const daysList = getDaysList();
  const activeDayPlan = daysList[activeDay];

  return (
    <div className="app-container">
      {/* Sidebar for History */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>🎒 TripVerse</h2>
          <p className="sidebar-subtitle">Your AI Travel Journal</p>
        </div>
        
        <div className="search-bar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input
            type="text"
            placeholder="Search past trips..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="saved-trips-list">
          {filteredTrips.length === 0 ? (
            <p className="empty-message">No trips found</p>
          ) : (
            filteredTrips.map((trip) => (
              <div
                key={trip.id}
                className={`trip-item-card ${selectedTrip && selectedTrip.id === trip.id ? "active" : ""}`}
                onClick={() => {
                  setSelectedTrip(trip);
                  setActiveDay(0);
                }}
              >
                <div className="trip-item-info">
                  <span className="trip-item-dest">✈️ {trip.destination}</span>
                  <span className="trip-item-days">{trip.days} Days • {trip.interests.slice(0, 20)}{trip.interests.length > 20 ? "..." : ""}</span>
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => handleDelete(trip.id, e)}
                  title="Delete Itinerary"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="main-content">
        {/* Form area */}
        <section className="form-card-container">
          <div className="glass-card plan-form-card">
            <h1 className="main-title">Create a New Journey</h1>
            <p className="main-desc">Let AI curate your perfect travel schedule in seconds.</p>
            
            <form onSubmit={generatePlan} className="plan-form">
              <div className="input-group">
                <label>Where to?</label>
                <div className="input-wrapper">
                  <span className="input-icon">📍</span>
                  <input
                    type="text"
                    placeholder="e.g. Kyoto, Japan"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="input-group-row">
                <div className="input-group flex-1">
                  <label>Duration (Days)</label>
                  <div className="input-wrapper">
                    <span className="input-icon">📅</span>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      placeholder="e.g. 5"
                      value={days}
                      onChange={(e) => setDays(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="input-group flex-2">
                  <label>Interests / Travel Style</label>
                  <div className="input-wrapper">
                    <span className="input-icon">✨</span>
                    <input
                      type="text"
                      placeholder="e.g. Food, temples, nature, photography"
                      value={interests}
                      onChange={(e) => setInterests(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="input-group">
                <label>Specific Places to Include (optional)</label>
                <div className="input-wrapper">
                  <span className="input-icon">🏙️</span>
                  <input
                    type="text"
                    placeholder="e.g. Fushimi Inari Shrine, Kinkaku-ji, Gion"
                    value={mustInclude}
                    onChange={(e) => setMustInclude(e.target.value)}
                  />
                </div>
              </div>

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? (
                  <span className="loading-spinner-wrapper">
                    <span className="spinner"></span> Mapping adventure...
                  </span>
                ) : (
                  <>🪄 Generate Itinerary</>
                )}
              </button>
            </form>

            {error && (
              <div className="error-alert">
                <span>⚠️ {error}</span>
              </div>
            )}
          </div>
        </section>

        {/* Display Active Itinerary */}
        <section className="itinerary-display-area">
          {loading ? (
            <div className="loading-card glass-card">
              <div className="compass-animation">🧭</div>
              <h3>Assembling your customized plan...</h3>
              <p>Consulting Gemini AI to find the best spots, routes, and experiences based on your interests.</p>
            </div>
          ) : selectedTrip ? (
            <div className="glass-card itinerary-card animate-fade-in">
              <div className="itinerary-header">
                <div className="header-badge-row">
                  <div className="header-badge">🚀 Active Itinerary</div>
                  <button 
                    className="edit-meta-btn"
                    onClick={() => setIsEditingMetadata(!isEditingMetadata)}
                  >
                    ⚙️ Edit / Regenerate
                  </button>
                </div>
                <h2>Explore {selectedTrip.destination}</h2>
                <div className="itinerary-meta">
                  <span>⏱️ <strong>{selectedTrip.days}</strong> Days</span>
                  <span>🎨 Interests: <strong>{selectedTrip.interests}</strong></span>
                  {selectedTrip.must_include && (
                    <span>🏙️ Include: <strong>{selectedTrip.must_include}</strong></span>
                  )}
                </div>
              </div>

              {isEditingMetadata && (
                <div className="metadata-edit-form animate-slide-up">
                  <h3>⚙️ Edit Journey Details</h3>
                  <div className="input-group">
                    <label>Destination</label>
                    <input 
                      type="text" 
                      value={editDestination} 
                      onChange={(e) => setEditDestination(e.target.value)} 
                    />
                  </div>
                  <div className="input-group-row">
                    <div className="input-group flex-1">
                      <label>Duration (Days)</label>
                      <input 
                        type="number" 
                        min="1"
                        max="30"
                        value={editDays} 
                        onChange={(e) => setEditDays(e.target.value)} 
                      />
                    </div>
                    <div className="input-group flex-2">
                      <label>Interests</label>
                      <input 
                        type="text" 
                        value={editInterests} 
                        onChange={(e) => setEditInterests(e.target.value)} 
                      />
                    </div>
                  </div>
                  <div className="input-group">
                    <label>Specific Places to Include</label>
                    <input 
                      type="text" 
                      value={editMustInclude} 
                      placeholder="e.g. Specific temples, parks, cafes"
                      onChange={(e) => setEditMustInclude(e.target.value)} 
                    />
                  </div>
                  <div className="edit-form-actions">
                    <button 
                      onClick={handleSaveMetadata}
                      className="save-meta-btn"
                      disabled={isRegenerating}
                    >
                      💾 Save Details Only
                    </button>
                    <button 
                      onClick={handleRegeneratePlan}
                      className="regenerate-btn"
                      disabled={isRegenerating}
                    >
                      {isRegenerating ? (
                        <>🧭 Regenerating Itinerary...</>
                      ) : (
                        <>🪄 Regenerate Itinerary</>
                      )}
                    </button>
                    <button 
                      onClick={() => setIsEditingMetadata(false)} 
                      className="cancel-meta-btn"
                      disabled={isRegenerating}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {daysList.length > 0 ? (
                <div className="itinerary-body">
                  {/* Day tabs */}
                  <div className="day-tabs">
                    {daysList.map((d, index) => (
                      <button
                        key={index}
                        className={`day-tab-btn ${activeDay === index ? "active" : ""}`}
                        onClick={() => {
                          setActiveDay(index);
                          setEditingActivityIndex(null);
                          setIsAddingActivity(false);
                        }}
                      >
                        Day {d.day || index + 1}
                      </button>
                    ))}
                  </div>

                  <div className="itinerary-content-split">
                    {/* Selected Day Content (Left Column) */}
                    {activeDayPlan && (
                      <div className="day-plan-details itinerary-left-col animate-slide-up">
                        <div className="day-plan-title-bar">
                          <h3>Day {activeDayPlan.day || activeDay + 1}: {activeDayPlan.city || selectedTrip.destination}</h3>
                        </div>
                        
                        <div className="activities-timeline">
                          {Array.isArray(activeDayPlan.activities) && activeDayPlan.activities.length > 0 ? (
                            activeDayPlan.activities.map((activity, aIndex) => {
                              const actText = typeof activity === "string" ? activity : JSON.stringify(activity);
                              const isEditingThisActivity = editingActivityIndex === aIndex;
                              return (
                                <div key={aIndex} className="activity-card-wrapper">
                                  <div className="timeline-node">
                                    <div className="node-dot"></div>
                                    {(aIndex < activeDayPlan.activities.length - 1 || isAddingActivity) && <div className="node-line"></div>}
                                  </div>
                                  <div className="activity-card">
                                    <div className="activity-card-header">
                                      <span className="activity-number">Activity {aIndex + 1}</span>
                                      {!isEditingThisActivity && (
                                        <div className="activity-actions">
                                          <button
                                            onClick={() => {
                                              setEditingActivityIndex(aIndex);
                                              setEditingActivityText(actText);
                                            }}
                                            className="edit-act-btn"
                                            title="Edit Activity"
                                          >
                                            ✏️
                                          </button>
                                          <button
                                            onClick={() => handleDeleteActivity(aIndex)}
                                            className="delete-act-btn"
                                            title="Delete Activity"
                                          >
                                            🗑️
                                          </button>
                                        </div>
                                      )}
                                    </div>
                                    
                                    {isEditingThisActivity ? (
                                      <div className="activity-edit-pane">
                                        <textarea
                                          value={editingActivityText}
                                          onChange={(e) => setEditingActivityText(e.target.value)}
                                          rows="2"
                                          className="activity-edit-input"
                                        />
                                        <div className="activity-edit-buttons">
                                          <button
                                            onClick={() => handleSaveActivityEdit(aIndex)}
                                            className="save-act-btn"
                                          >
                                            Save
                                          </button>
                                          <button
                                            onClick={() => {
                                              setEditingActivityIndex(null);
                                              setEditingActivityText("");
                                            }}
                                            className="cancel-act-btn"
                                          >
                                            Cancel
                                          </button>
                                        </div>
                                      </div>
                                    ) : (
                                      <p>{actText}</p>
                                    )}
                                  </div>
                                </div>
                              );
                            })
                          ) : (
                            <p className="no-activities">Relax and explore the city at your own leisure today!</p>
                          )}

                          {/* Inline Adding Activity Form */}
                          {isAddingActivity ? (
                            <div className="activity-card-wrapper add-activity-wrapper">
                              <div className="timeline-node">
                                <div className="node-dot new-node-dot">📍</div>
                              </div>
                              <div className="activity-card add-activity-card">
                                <span className="activity-number">New Custom Activity</span>
                                <textarea
                                  placeholder="E.g. Visit Kinkaku-ji golden temple, then walk to nearby zen garden"
                                  value={newActivityText}
                                  onChange={(e) => setNewActivityText(e.target.value)}
                                  rows="2"
                                  className="activity-edit-input"
                                />
                                <div className="activity-edit-buttons">
                                  <button onClick={handleAddCustomActivity} className="save-act-btn">
                                    Add Activity
                                  </button>
                                  <button onClick={() => { setIsAddingActivity(false); setNewActivityText(""); }} className="cancel-act-btn">
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <button
                              onClick={() => setIsAddingActivity(true)}
                              className="add-activity-trigger-btn"
                            >
                              ➕ Add Custom Place or Activity
                            </button>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Recommendations Panel (Right Column) */}
                    <div className="itinerary-right-col">
                      <div className="recommendations-container">
                        <h3>🏙️ Explore Local Highlights</h3>
                        <p className="recs-subtitle">Curated places matching "{selectedTrip.interests}"</p>
                        
                        {recsLoading ? (
                          <div className="recs-loading">
                            <span className="recs-spinner"></span>
                            <p>Scouting local spots...</p>
                          </div>
                        ) : recsError ? (
                          <div className="recs-error">
                            <p>⚠️ {recsError}</p>
                            <button onClick={() => fetchRecommendations(selectedTrip.id)} className="retry-btn">Retry</button>
                          </div>
                        ) : recommendations.length === 0 ? (
                          <p className="empty-message">No recommendations available for this destination.</p>
                        ) : (
                          <div className="recs-list">
                            {recommendations.map((rec, rIdx) => (
                              <div key={rIdx} className="rec-card animate-slide-up" style={{ animationDelay: `${rIdx * 0.05}s` }}>
                                <div className="rec-card-header">
                                  <h4>{rec.name}</h4>
                                  <span className="rec-tag">{rec.tag}</span>
                                </div>
                                <p className="rec-desc">{rec.description}</p>
                                
                                <div className="rec-add-section">
                                  <label>➕ Add to day:</label>
                                  <div className="rec-day-selector">
                                    {daysList.map((d, dIdx) => (
                                      <button
                                        key={dIdx}
                                        onClick={() => handleAddRecommendationToDay(rec, dIdx)}
                                        className="rec-day-btn"
                                        title={`Add to Day ${dIdx + 1}`}
                                      >
                                        Day {d.day || dIdx + 1}
                                      </button>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="malformed-warning">
                  <p>⚠️ The generated plan could not be displayed day-by-day. Showing raw details:</p>
                  <pre>{JSON.stringify(selectedTrip.plan, null, 2)}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="welcome-card glass-card">
              <div className="welcome-icon">🌍</div>
              <h2>Where will you go next?</h2>
              <p>Enter a destination above or select a past trip from your sidebar history to view and manage your travel itineraries.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;