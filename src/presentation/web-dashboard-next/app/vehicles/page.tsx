"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Search, Plus, Eye, Edit, Trash2 } from "lucide-react"

export default function VehiclesPage() {
  const [searchTerm, setSearchTerm] = useState("")

  // Mock data for demonstration
  const vehicles = [
    {
      id: 1,
      vin: "1HGBH41JXMN109186",
      manufacturer: "Toyota",
      model: "Camry",
      year: 2022,
      type: "Sedan",
      decodedAt: "2023-05-15",
    },
    {
      id: 2,
      vin: "2T1BURHE5JC012345",
      manufacturer: "Toyota",
      model: "Prius",
      year: 2018,
      type: "Hatchback",
      decodedAt: "2023-05-14",
    },
    {
      id: 3,
      vin: "1FTEW1E84JKD00001",
      manufacturer: "Ford",
      model: "F-150",
      year: 2020,
      type: "Pickup",
      decodedAt: "2023-05-12",
    },
    {
      id: 4,
      vin: "WBAVA33598NL67890",
      manufacturer: "BMW",
      model: "X5",
      year: 2019,
      type: "SUV",
      decodedAt: "2023-05-10",
    },
    {
      id: 5,
      vin: "JH4NA21691T000012",
      manufacturer: "Honda",
      model: "Accord",
      year: 2021,
      type: "Sedan",
      decodedAt: "2023-05-08",
    },
  ]

  const filteredVehicles = vehicles.filter(
    (vehicle) =>
      vehicle.vin.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.model.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Vehicles</h1>
          <p className="text-muted-foreground">
            Manage your decoded vehicles
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Vehicle
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle>All Vehicles</CardTitle>
              <CardDescription>Manage your vehicle database</CardDescription>
            </div>
            <div className="relative w-full md:w-64">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search vehicles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
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
                <TableHead>Decoded At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVehicles.map((vehicle) => (
                <TableRow key={vehicle.id}>
                  <TableCell className="font-mono">{vehicle.vin}</TableCell>
                  <TableCell>{vehicle.manufacturer}</TableCell>
                  <TableCell>{vehicle.model}</TableCell>
                  <TableCell>{vehicle.year}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{vehicle.type}</Badge>
                  </TableCell>
                  <TableCell>{vehicle.decodedAt}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="destructive" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}