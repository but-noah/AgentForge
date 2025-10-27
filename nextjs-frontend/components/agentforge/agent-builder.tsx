"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Sparkles, Zap, Database, Globe, Brain } from "lucide-react"
import { toast } from "@/hooks/use-toast"

interface AgentBuilderProps {
  workspaceId: string
  onAgentCreated?: (agent: any) => void
}

export function AgentBuilder({ workspaceId, onAgentCreated }: AgentBuilderProps) {
  const [prompt, setPrompt] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [suggestedTools, setSuggestedTools] = useState<string[]>([])

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: "Error",
        description: "Please describe your agent first",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    setProgress(0)

    try {
      // Simulate AI analysis
      setProgress(33)
      await new Promise(resolve => setTimeout(resolve, 500))

      setSuggestedTools(["Vector Search", "HTTP API", "MCP Server"])
      setProgress(66)
      await new Promise(resolve => setTimeout(resolve, 500))

      // Call API to create agent
      const response = await fetch("/api/agents/create-from-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_id: workspaceId, prompt }),
      })

      if (!response.ok) throw new Error("Failed to create agent")

      const agent = await response.json()
      setProgress(100)

      toast({
        title: "Agent Created!",
        description: `${agent.name} is ready to use`,
      })

      onAgentCreated?.(agent)
      setPrompt("")
      setSuggestedTools([])
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create agent. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
      setProgress(0)
    }
  }

  return (
    <Card className="border-2 border-dashed border-primary/20 hover:border-primary/40 transition-all">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-mesh">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <CardTitle>Create Agent with AI</CardTitle>
            <CardDescription>
              Describe your agent in natural language and let AI build it for you
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <Textarea
          placeholder="Example: Create a customer support agent that can search our knowledge base and create support tickets..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="min-h-[120px] resize-none"
          disabled={isGenerating}
        />

        {isGenerating && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Analyzing your request...</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {suggestedTools.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Suggested Tools</label>
            <div className="flex flex-wrap gap-2">
              {suggestedTools.map((tool, idx) => (
                <Badge key={idx} variant="secondary" className="flex items-center gap-1">
                  {tool === "Vector Search" && <Database className="h-3 w-3" />}
                  {tool === "HTTP API" && <Globe className="h-3 w-3" />}
                  {tool === "MCP Server" && <Zap className="h-3 w-3" />}
                  {tool}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
          <div className="flex items-start gap-2">
            <Brain className="h-4 w-4 text-primary mt-0.5" />
            <div className="text-sm">
              <div className="font-medium">Smart Analysis</div>
              <div className="text-muted-foreground text-xs">AI-powered configuration</div>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <Zap className="h-4 w-4 text-primary mt-0.5" />
            <div className="text-sm">
              <div className="font-medium">Instant Setup</div>
              <div className="text-muted-foreground text-xs">Ready in seconds</div>
            </div>
          </div>
        </div>
      </CardContent>

      <CardFooter>
        <Button
          onClick={handleGenerate}
          disabled={!prompt.trim() || isGenerating}
          className="w-full gradient-indigo text-white"
          size="lg"
        >
          {isGenerating ? (
            <>
              <Sparkles className="mr-2 h-4 w-4 animate-pulse" />
              Generating Agent...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-4 w-4" />
              Generate Agent
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}
