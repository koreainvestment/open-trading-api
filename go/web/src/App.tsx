import { useState } from "react";
import { Dashboard } from "./views/Dashboard";
import { ReportsList } from "./views/ReportsList";

function App() {
  const [currentTab, setCurrentTab] = useState<"dashboard" | "reports">(
    "dashboard"
  );

  return (
    <div className="container">
      <header>
        <h1>DART Reports</h1>
        <p className="subtitle">Financial Reports Dashboard</p>
      </header>

      <main>
        <div className="tabs">
          <button
            className={`tab-btn ${currentTab === "dashboard" ? "active" : ""}`}
            onClick={() => setCurrentTab("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={`tab-btn ${currentTab === "reports" ? "active" : ""}`}
            onClick={() => setCurrentTab("reports")}
          >
            Reports List
          </button>
        </div>

        {currentTab === "dashboard" ? <Dashboard /> : <ReportsList />}
      </main>
    </div>
  );
}

export default App;
