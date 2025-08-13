"use client"

import { useState } from "react"
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
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Search, Eye, Trash2 } from "lucide-react"

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

interface EnhancedVehicleTableProps {
  vehicles: Vehicle[]
  searchTerm: string
  onSearchChange: (term: string) => void
  onViewVehicle: (vehicle: Vehicle) => void
  onDeleteVehicle: (id: number) => void
}

export function EnhancedVehicleTable({
  vehicles,
  searchTerm,
  onSearchChange,
  onViewVehicle,
  onDeleteVehicle
}: EnhancedVehicleTableProps) {
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const handleView = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle)
    setIsDialogOpen(true)
    onViewVehicle(vehicle)
  }

  return (
    <div className="rounded-md border">
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by VIN, manufacturer, or model..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>VIN</TableHead>
            <TableHead>Manufacturer</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Year</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Decoded At</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {vehicles.length > 0 ? (
            vehicles.map((vehicle) => (
              <TableRow key={vehicle.id} className="hover:bg-muted/50">
                <TableCell className="font-mono text-sm">{vehicle.vin}</TableCell>
                <TableCell>{vehicle.manufacturer}</TableCell>
                <TableCell>{vehicle.model}</TableCell>
                <TableCell>{vehicle.year}</TableCell>
                <TableCell>
                  <Badge variant="secondary">{vehicle.vehicle_type}</Badge>
                </TableCell>
                <TableCell>
                  {new Date(vehicle.decoded_at).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleView(vehicle)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => onDeleteVehicle(vehicle.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                No vehicles found
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Vehicle Details</DialogTitle>
            <DialogDescription>
              Complete information for VIN: {selectedVehicle?.vin}
            </DialogDescription>
          </DialogHeader>
          {selectedVehicle && (
            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basic">Basic Info</TabsTrigger>
                <TabsTrigger value="technical">Technical</TabsTrigger>
                <TabsTrigger value="raw">Raw Data</TabsTrigger>
              </TabsList>
              <TabsContent value="basic" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">VIN</p>
                    <p className="font-mono">{selectedVehicle.vin}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Manufacturer</p>
                    <p>{selectedVehicle.manufacturer}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Model</p>
                    <p>{selectedVehicle.model}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Year</p>
                    <p>{selectedVehicle.year.toString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Type</p>
                    <p>{selectedVehicle.vehicle_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Decoded At</p>
                    <p>{new Date(selectedVehicle.decoded_at).toLocaleString()}</p>
                  </div>
                </div>
              </TabsContent>
              <TabsContent value="technical" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Engine Info</p>
                    <p>{selectedVehicle.engine_info || "Not available"}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Fuel Type</p>
                    <p>{selectedVehicle.fuel_type || "Not available"}</p>
                  </div>
                </div>
              </TabsContent>
              <TabsContent value="raw">
                <pre className="overflow-auto rounded-md bg-muted p-4 text-sm max-h-96">
                  {JSON.stringify(selectedVehicle.raw_data, null, 2)}
                </pre>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}