"use client"

import { useState, useEffect } from "react"
import { Bot, Plus } from "lucide-react"
import { PageHeader, AgentBuilder, AgentCard, EmptyState } from "@/components/agentforge"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"

interface Agent {
  id: string
  name: string
  description?: string
  tools?: any[]
  is_active?: boolean
  created_at: string
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [showBuilder, setShowBuilder] = useState(false)
  const workspaceId = "default-workspace" // TODO: Get from auth context

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch(`/api/agents?workspace_id=${workspaceId}`)
      if (response.ok) {
        const data = await response.json()
        setAgents(data)
      }
    } catch (error) {
      console.error("Failed to fetch agents:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleAgentCreated = (agent: Agent) => {
    setAgents(prev => [agent, ...prev])
    setShowBuilder(false)
    toast({
      title: "Success!",
      description: `Agent "${agent.name}" has been created`,
    })
  }

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm("Are you sure you want to delete this agent?")) return

    try {
      const response = await fetch(`/api/agents/${agentId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setAgents(prev => prev.filter(a => a.id !== agentId))
        toast({
          title: "Agent deleted",
          description: "The agent has been successfully removed",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete agent",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <PageHeader
        icon={Bot}
        title="AI Agents"
        description="Create, manage, and deploy intelligent AI agents"
        action={{
          label: "Create Agent",
          onClick: () => setShowBuilder(true),
          icon: Plus,
        }}
      />

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-64 rounded-lg" />
          ))}
        </div>
      ) : agents.length === 0 ? (
        <EmptyState
          icon={Bot}
          title="No agents yet"
          description="Create your first AI agent to get started. Describe what you want it to do in natural language."
          action={{
            label: "Create Your First Agent",
            onClick: () => setShowBuilder(true),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onDelete={() => handleDeleteAgent(agent.id)}
            />
          ))}
        </div>
      )}

      <Dialog open={showBuilder} onOpenChange={setShowBuilder}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Agent</DialogTitle>
            <DialogDescription>
              Describe your agent in natural language and we'll configure it for you
            </DialogDescription>
          </DialogHeader>
          <AgentBuilder
            workspaceId={workspaceId}
            onAgentCreated={handleAgentCreated}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
