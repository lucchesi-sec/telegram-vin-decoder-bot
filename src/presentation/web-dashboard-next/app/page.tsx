"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "react-hot-toast"
import { TextScramble } from "@/components/ui/text-scramble"

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

export default function Dashboard() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [stats, setStats] = useState<Stats>({
    total_vehicles: 0,
    unique_manufacturers: 0,
    recent_decodes: 0,
  })
  const [searchTerm, setSearchTerm] = useState("")
  const [vinInput, setVinInput] = useState("")
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null)
  const [isDecoding, setIsDecoding] = useState(false)
  const [decodeError, setDecodeError] = useState("")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchVehicles = useCallback(async () => {
    try {
      const response = await fetch(`/api/vehicles?page=${page}&limit=10`)
      const data = await response.json()
      setVehicles(data.vehicles || [])
      setTotalPages(data.total_pages || 1)
    } catch (error) {
      console.error("Error fetching vehicles:", error)
    }
  }, [page])

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`/api/stats`)
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error("Error fetching stats:", error)
    }
  }, [])

  useEffect(() => {
    fetchVehicles()
    fetchStats()
  }, [fetchVehicles, fetchStats])

  const handleDecode = async () => {
    if (vinInput.length !== 17) {
      setDecodeError("VIN must be exactly 17 characters")
      return
    }

    setIsDecoding(true)
    setDecodeError("")

    try {
      const response = await fetch(`/api/decode`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ vin: vinInput.toUpperCase() }),
      })

      const data: DecodeResponse = await response.json()

      if (response.ok && data.success) {
        setVinInput("")
        fetchVehicles()
        fetchStats()
        // Show success message with vehicle details
        if (data.vehicle) {
          toast.success(
            <div>
              <div>Successfully decoded:</div>
              <div className="font-mono">
                <TextScramble speed={20}>
                  {`${data.vehicle.year.toString()} ${data.vehicle.manufacturer} ${data.vehicle.model}`}
                </TextScramble>
              </div>
            </div>
          )
        } else {
          toast.success(
            <div>
              <div>VIN decoded successfully</div>
              <div className="font-mono">
                <TextScramble speed={20}>{vinInput.toUpperCase()}</TextScramble>
              </div>
            </div>
          )
        }
      } else {
        const errorMessage = data.vehicle ? "Failed to decode VIN" : (data as { message?: string }).message || "Failed to decode VIN"
        setDecodeError(errorMessage)
        toast.error(
          <div>
            <div>Decode failed:</div>
            <div>
              <TextScramble speed={20}>{errorMessage}</TextScramble>
            </div>
          </div>
        )
      }
    } catch (error: unknown) {
      const errorMessage = "Network error. Please try again."
      setDecodeError(errorMessage)
      toast.error(
        <div>
          <div>Network error:</div>
          <div>
            <TextScramble speed={20}>{errorMessage}</TextScramble>
          </div>
        </div>
      )
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
      }
    } catch (error) {
      console.error("Error deleting vehicle:", error)
    }
  }

  const filteredVehicles = vehicles.filter(
    (vehicle) =>
      vehicle.vin.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.model.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-500 p-4">
      <div className="mx-auto max-w-7xl space-y-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-3xl font-bold">🚗 VIN Decoder Dashboard</CardTitle>
              <CardDescription>Manage and decode vehicle identification numbers</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={fetchVehicles}>
                Refresh
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button>Decode New VIN</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Decode New VIN</DialogTitle>
                    <DialogDescription>
                      Enter a 17-character Vehicle Identification Number
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <Input
                      placeholder="Enter VIN (17 characters)"
                      value={vinInput}
                      onChange={(e) => setVinInput(e.target.value.toUpperCase())}
                      maxLength={17}
                    />
                    {decodeError && (
                      <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">
                        {decodeError}
                      </div>
                    )}
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setVinInput("")}>
                        Cancel
                      </Button>
                      <Button onClick={handleDecode} disabled={isDecoding}>
                        {isDecoding ? "Decoding..." : "Decode"}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl"><TextScramble speed={30}>{stats.total_vehicles.toString()}</TextScramble></CardTitle>
              <CardDescription>Total Vehicles</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl"><TextScramble speed={30}>{stats.unique_manufacturers.toString()}</TextScramble></CardTitle>
              <CardDescription>Manufacturers</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl"><TextScramble speed={30}>{stats.recent_decodes.toString()}</TextScramble></CardTitle>
              <CardDescription>Recent Decodes (24h)</CardDescription>
            </CardHeader>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <Input
              placeholder="Search by VIN, manufacturer, or model..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-md"
            />
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>VIN</TableHead>
                  <TableHead>Manufacturer</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Year</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Engine</TableHead>
                  <TableHead>Fuel Type</TableHead>
                  <TableHead>Decoded At</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                                {filteredVehicles.length > 0 ? (
                  filteredVehicles.map((vehicle) => (
                    <TableRow key={vehicle.id}>
                      <TableCell className="font-mono"><TextScramble speed={40}>{vehicle.vin}</TextScramble></TableCell>
                      <TableCell><TextScramble speed={40}>{vehicle.manufacturer}</TextScramble></TableCell>
                      <TableCell><TextScramble speed={40}>{vehicle.model}</TextScramble></TableCell>
                      <TableCell><TextScramble speed={40}>{vehicle.year.toString()}</TextScramble></TableCell>
                      <TableCell>
                        <Badge variant="secondary"><TextScramble speed={40}>{vehicle.vehicle_type}</TextScramble></Badge>
                      </TableCell>
                      <TableCell><TextScramble speed={40}>{vehicle.engine_info || "N/A"}</TextScramble></TableCell>
                      <TableCell><TextScramble speed={40}>{vehicle.fuel_type || "N/A"}</TextScramble></TableCell>
                      <TableCell>
                        <TextScramble speed={40}>{new Date(vehicle.decoded_at).toLocaleDateString()}</TextScramble>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setSelectedVehicle(vehicle)}
                              >
                                View
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-3xl">
                              <DialogHeader>
                                <DialogTitle>Vehicle Details</DialogTitle>
                                <DialogDescription>
                                  Complete information for VIN: <TextScramble speed={20}>{vehicle.vin}</TextScramble>
                                </DialogDescription>
                              </DialogHeader>
                              {selectedVehicle && selectedVehicle.id === vehicle.id && (
                                <Tabs defaultValue="basic" className="w-full">
                                  <TabsList className="grid w-full grid-cols-3">
                                    <TabsTrigger value="basic">Basic Info</TabsTrigger>
                                    <TabsTrigger value="technical">Technical</TabsTrigger>
                                    <TabsTrigger value="raw">Raw Data</TabsTrigger>
                                  </TabsList>
                                  <TabsContent value="basic" className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                      <div>
                                        <p className="text-sm text-muted-foreground">VIN</p>
                                        <p className="font-mono"><TextScramble speed={20}>{selectedVehicle.vin}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">
                                          Manufacturer
                                        </p>
                                        <p><TextScramble speed={20}>{selectedVehicle.manufacturer}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">Model</p>
                                        <p><TextScramble speed={20}>{selectedVehicle.model}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">Year</p>
                                        <p><TextScramble speed={20}>{selectedVehicle.year.toString()}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">Type</p>
                                        <p><TextScramble speed={20}>{selectedVehicle.vehicle_type}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">
                                          Decoded At
                                        </p>
                                        <p>
                                          <TextScramble speed={20}>{new Date(selectedVehicle.decoded_at).toLocaleString()}</TextScramble>
                                        </p>
                                      </div>
                                    </div>
                                  </TabsContent>
                                  <TabsContent value="technical" className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                      <div>
                                        <p className="text-sm text-muted-foreground">
                                          Engine Info
                                        </p>
                                        <p><TextScramble speed={20}>{selectedVehicle.engine_info || "Not available"}</TextScramble></p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-muted-foreground">Fuel Type</p>
                                        <p><TextScramble speed={20}>{selectedVehicle.fuel_type || "Not available"}</TextScramble></p>
                                      </div>
                                    </div>
                                  </TabsContent>
                                  <TabsContent value="raw">
                                    <pre className="overflow-auto rounded-md bg-muted p-4 text-sm">
                                      <TextScramble speed={10}>{JSON.stringify(selectedVehicle.raw_data, null, 2)}</TextScramble>
                                    </pre>
                                  </TabsContent>
                                </Tabs>
                              )}
                            </DialogContent>
                          </Dialog>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDelete(vehicle.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground">
                      No vehicles found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <div className="flex items-center justify-center gap-4">
          <Button
            variant="outline"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-white">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
