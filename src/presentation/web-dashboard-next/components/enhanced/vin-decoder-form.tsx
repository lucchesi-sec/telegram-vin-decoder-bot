"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"
import { Car, Search } from "lucide-react"

interface VinDecoderFormProps {
  onDecode: (vin: string) => Promise<void>
  isLoading: boolean
}

export function VinDecoderForm({ onDecode, isLoading }: VinDecoderFormProps) {
  const [vinInput, setVinInput] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (vinInput.length !== 17) {
      setError("VIN must be exactly 17 characters")
      return
    }
    
    setError("")
    await onDecode(vinInput.toUpperCase())
    setVinInput("")
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Car className="h-5 w-5" />
            Decode New VIN
          </CardTitle>
          <CardDescription>
            Enter a 17-character Vehicle Identification Number to decode
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Enter VIN (17 characters)"
                value={vinInput}
                onChange={(e) => setVinInput(e.target.value.toUpperCase())}
                maxLength={17}
                className="pl-10"
              />
            </div>
            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading || vinInput.length !== 17}>
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Decoding...
                </div>
              ) : (
                "Decode VIN"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  )
}