"use client"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Bot, Play, Settings, Trash2, Sparkles } from "lucide-react"
import Link from "next/link"

interface AgentCardProps {
  agent: {
    id: string
    name: string
    description?: string
    tools?: any[]
    is_active?: boolean
    created_at: string
  }
  onExecute?: () => void
  onDelete?: () => void
}

export function AgentCard({ agent, onExecute, onDelete }: AgentCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-all duration-300 hover:border-primary/50">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-indigo text-white">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="group-hover:text-primary transition-colors">
                {agent.name}
              </CardTitle>
              <CardDescription className="mt-1">
                {agent.description || "No description provided"}
              </CardDescription>
            </div>
          </div>
          {agent.is_active && (
            <Badge className="bg-green-100 text-green-800 border-green-200">
              <Sparkles className="h-3 w-3 mr-1" />
              Active
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex flex-wrap gap-2">
          {agent.tools && agent.tools.length > 0 ? (
            agent.tools.slice(0, 3).map((tool, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {tool.name || tool.type}
              </Badge>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">No tools configured</span>
          )}
          {agent.tools && agent.tools.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{agent.tools.length - 3} more
            </Badge>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between gap-2">
        <Link href={`/agents/${agent.id}`} className="flex-1">
          <Button variant="outline" className="w-full" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </Button>
        </Link>
        <Button
          variant="default"
          size="sm"
          className="flex-1"
          onClick={onExecute}
        >
          <Play className="h-4 w-4 mr-2" />
          Run
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onDelete}
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  )
}
