"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { 
  MessageCircle,
  Mail,
  FileText,
  Youtube,
  BookOpen,
  HelpCircle
} from "lucide-react"

export default function HelpPage() {
  const faqs = [
    {
      question: "How do I decode a VIN?",
      answer: "To decode a VIN, navigate to the dashboard and click the 'Decode New VIN' button. Enter the 17-character VIN and click 'Decode'. The system will process the VIN and display the vehicle information."
    },
    {
      question: "What information can I get from a VIN?",
      answer: "A VIN can provide detailed information about a vehicle including the manufacturer, model, year, engine type, fuel type, and other technical specifications. Our system extracts all available data from the VIN."
    },
    {
      question: "How accurate is the VIN decoding?",
      answer: "Our VIN decoding system has a 98.5% accuracy rate. We use multiple data sources and cross-reference information to ensure the highest possible accuracy for vehicle data."
    },
    {
      question: "Can I export my vehicle data?",
      answer: "Yes, you can export your vehicle data in CSV or JSON format. Navigate to the Vehicles page, select the vehicles you want to export, and click the 'Export' button."
    },
    {
      question: "How often is the vehicle database updated?",
      answer: "Our vehicle database is updated daily with new information from manufacturers and regulatory bodies. This ensures you have access to the most current vehicle data."
    }
  ]

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Help Center</h1>
        <p className="text-muted-foreground">
          Get help with VIN decoding and dashboard features
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>How can we help you?</CardTitle>
          <CardDescription>
            Search our help center or browse common topics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative w-full max-w-xl mx-auto">
            <Input 
              placeholder="Search help articles..." 
              className="pl-10 py-6 text-base"
            />
            <HelpCircle className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <MessageCircle className="h-8 w-8 mb-2 text-primary" />
            <h3 className="font-semibold mb-1">Contact Support</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Get in touch with our support team
            </p>
            <Button variant="outline" size="sm">Contact</Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <Mail className="h-8 w-8 mb-2 text-primary" />
            <h3 className="font-semibold mb-1">Email Us</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Send us an email for detailed inquiries
            </p>
            <Button variant="outline" size="sm">Email</Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <FileText className="h-8 w-8 mb-2 text-primary" />
            <h3 className="font-semibold mb-1">Documentation</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Read our comprehensive documentation
            </p>
            <Button variant="outline" size="sm">Docs</Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex flex-col items-center p-6 text-center">
            <Youtube className="h-8 w-8 mb-2 text-primary" />
            <h3 className="font-semibold mb-1">Video Tutorials</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Watch step-by-step video guides
            </p>
            <Button variant="outline" size="sm">Watch</Button>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
            <CardDescription>
              Find answers to common questions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible>
              {faqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`}>
                  <AccordionTrigger>{faq.question}</AccordionTrigger>
                  <AccordionContent>{faq.answer}</AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              Learn the basics of using the VIN decoder
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-primary font-semibold">1</span>
              </div>
              <div>
                <h3 className="font-medium">Create an Account</h3>
                <p className="text-sm text-muted-foreground">
                  Sign up for a free account to start decoding VINs
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-primary font-semibold">2</span>
              </div>
              <div>
                <h3 className="font-medium">Decode Your First VIN</h3>
                <p className="text-sm text-muted-foreground">
                  Enter a 17-character VIN in the decoder form
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-primary font-semibold">3</span>
              </div>
              <div>
                <h3 className="font-medium">View Vehicle Details</h3>
                <p className="text-sm text-muted-foreground">
                  Explore detailed information about the vehicle
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-primary font-semibold">4</span>
              </div>
              <div>
                <h3 className="font-medium">Manage Your Vehicles</h3>
                <p className="text-sm text-muted-foreground">
                  Organize and export your decoded vehicles
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}