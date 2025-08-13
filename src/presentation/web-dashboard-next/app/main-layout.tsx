"use client"

import { useState } from "react"
import { Sidebar } from "@/components/ui/sidebar"
import EnhancedDashboard from "./enhanced-dashboard"
import AnalyticsPage from "./analytics/page"
import VehiclesPage from "./vehicles/page"
import SettingsPage from "./settings/page"
import HelpPage from "./help/page"

export default function MainLayout() {
  const [activePage, setActivePage] = useState("dashboard")

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return <EnhancedDashboard />
      case "analytics":
        return <AnalyticsPage />
      case "vehicles":
        return <VehiclesPage />
      case "settings":
        return <SettingsPage />
      case "help":
        return <HelpPage />
      default:
        return <EnhancedDashboard />
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar activePage={activePage} onPageChange={setActivePage} />
      <main className="flex-1 md:ml-64">
        {renderPage()}
      </main>
    </div>
  )
}