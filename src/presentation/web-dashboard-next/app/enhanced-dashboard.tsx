"use client"

import { useState, useEffect, useCallback } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { toast } from "react-hot-toast"
import CanvasRevealEffectDemo from "@/components/canvas-reveal-effect-demo"
import { StatCard } from "@/components/enhanced/stat-card"
import { EnhancedVehicleTable } from "@/components/enhanced/vehicle-table"
import { VinDecoderForm } from "@/components/enhanced/vin-decoder-form"
import { DashboardHeader } from "@/components/enhanced/dashboard-header"
import {
  Car,
  Factory,
  Clock,
  TrendingUp,
  Calendar,
  Fuel,
  Zap,
  RefreshCw
} from "lucide-react"

interface Vehicle {
  id: number
  vin: string
  manufacturer: string
  model: string
  year: number
  vehicle_type: string
  engine_info: string
  fuel_type: string
  decoded_at: string
  user_id: number
  raw_data: Record<string, unknown>
}

interface Stats {
  total_vehicles: number
  unique_manufacturers: number
  recent_decodes: number
}

interface DecodeResponse {
  success: boolean
  vehicle?: Vehicle
}

export default function EnhancedDashboard() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [stats, setStats] = useState<Stats>({
    total_vehicles: 0,
    unique_manufacturers: 0,
    recent_decodes: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isDecoding, setIsDecoding] = useState(false)

  const fetchVehicles = useCallback(async () => {
    try {
      const response = await fetch(`/api/vehicles?page=${page}&limit=10`)
      if (!response.ok) {
        console.warn("Vehicles API unavailable, showing empty state")
        setVehicles([])
        setTotalPages(1)
        return
      }
      const data = await response.json()
      setVehicles(data.vehicles || [])
      setTotalPages(data.total_pages || 1)
    } catch (error) {
      console.error("Error fetching vehicles:", error)
      setVehicles([])
      setTotalPages(1)
    }
  }, [page])

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`/api/stats`)
      if (!response.ok) {
        console.warn("Stats API unavailable, using default values")
        return
      }
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error("Error fetching stats:", error)
      // Keep default values on error
    }
  }, [])

  useEffect(() => {
    setIsLoading(true)
    Promise.all([fetchVehicles(), fetchStats()]).finally(() => {
      setIsLoading(false)
    })
  }, [fetchVehicles, fetchStats])

  const handleDecode = async (vin: string) => {
    setIsDecoding(true)

    try {
      const response = await fetch(`/api/decode`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ vin }),
      })

      const data: DecodeResponse = await response.json()

      if (response.ok && data.success) {
        fetchVehicles()
        fetchStats()
        // Show success message with vehicle details
        if (data.vehicle) {
          toast.success(`Successfully decoded: ${data.vehicle.year} ${data.vehicle.manufacturer} ${data.vehicle.model}`)
        } else {
          toast.success(`VIN decoded successfully: ${vin}`)
        }
      } else {
        const errorMessage = data.vehicle ? "Failed to decode VIN" : (data as { message?: string }).message || "Failed to decode VIN"
        toast.error(`Decode failed: ${errorMessage}`)
      }
    } catch (error: unknown) {
      const errorMessage = "Network error. Please try again."
      toast.error(`Network error: ${errorMessage}`)
    } finally {
      setIsDecoding(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this vehicle?")) return

    try {
      const response = await fetch(`/api/vehicles/${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        fetchVehicles()
        fetchStats()
        toast.success("Vehicle deleted successfully")
      } else {
        toast.error("Failed to delete vehicle")
      }
    } catch (error) {
      console.error("Error deleting vehicle:", error)
      toast.error("Error deleting vehicle")
    }
  }

  const handleRefresh = () => {
    setIsLoading(true)
    Promise.all([fetchVehicles(), fetchStats()]).finally(() => {
      setIsLoading(false)
      toast.success("Data refreshed")
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <DashboardHeader />
      
      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Vehicles"
            value={stats.total_vehicles}
            description="Vehicles in database"
            icon={<Car className="h-6 w-6" />}
            trend={{ value: 12, label: "from last month" }}
          />
          <StatCard
            title="Manufacturers"
            value={stats.unique_manufacturers}
            description="Unique car brands"
            icon={<Factory className="h-6 w-6" />}
            trend={{ value: 5, label: "new this month" }}
          />
          <StatCard
            title="Recent Decodes"
            value={stats.recent_decodes}
            description="Last 24 hours"
            icon={<Clock className="h-6 w-6" />}
            trend={{ value: 18, label: "from yesterday" }}
          />
          <StatCard
            title="Success Rate"
            value="98.5%"
            description="Successful decodes"
            icon={<TrendingUp className="h-6 w-6" />}
            trend={{ value: 2.3, label: "improvement" }}
          />
        </div>
      </motion.div>

      {/* VIN Decoder Form */}
      <VinDecoderForm onDecode={handleDecode} isLoading={isDecoding} />

      {/* Canvas Effects */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Interactive Effects</CardTitle>
            <CardDescription>Hover over the cards to see animated backgrounds</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <CanvasRevealEffectDemo />
          </CardContent>
        </Card>
      </motion.div>

      {/* Vehicle Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Vehicles</CardTitle>
            <CardDescription>Manage your decoded vehicles</CardDescription>
          </CardHeader>
          <CardContent>
            <EnhancedVehicleTable
              vehicles={vehicles}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              onViewVehicle={() => {}}
              onDeleteVehicle={handleDelete}
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Pagination */}
      {totalPages > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
          className="flex items-center justify-center gap-4"
        >
          <Button
            variant="outline"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </motion.div>
      )}
    </div>
  )
}