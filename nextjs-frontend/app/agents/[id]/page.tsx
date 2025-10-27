"use client"

import { useState, useEffect } from "react"
import { use } from "react"
import { ArrowLeft, Settings, Play, Code, Database } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { AgentChat } from "@/components/agentforge"

interface AgentDetailPageProps {
  params: Promise<{ id: string }>
}

export default function AgentDetailPage({ params }: AgentDetailPageProps) {
  const { id } = use(params)
  const [agent, setAgent] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAgent()
  }, [id])

  const fetchAgent = async () => {
    try {
      const response = await fetch(`/api/agents/${id}`)
      if (response.ok) {
        const data = await response.json()
        setAgent(data)
      }
    } catch (error) {
      console.error("Failed to fetch agent:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Agent not found</p>
            <Link href="/agents">
              <Button className="mt-4">Back to Agents</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/agents">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold">{agent.name}</h1>
              {agent.is_active && (
                <Badge className="bg-green-100 text-green-800 border-green-200">
                  Active
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground mt-1">
              {agent.description || "No description"}
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Settings className="mr-2 h-4 w-4" />
          Configure
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="chat" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chat">
            <Play className="mr-2 h-4 w-4" />
            Test Chat
          </TabsTrigger>
          <TabsTrigger value="tools">
            <Code className="mr-2 h-4 w-4" />
            Tools
          </TabsTrigger>
          <TabsTrigger value="knowledge">
            <Database className="mr-2 h-4 w-4" />
            Knowledge Base
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat">
          <AgentChat agentId={agent.id} agentName={agent.name} />
        </TabsContent>

        <TabsContent value="tools">
          <Card>
            <CardHeader>
              <CardTitle>Connected Tools</CardTitle>
              <CardDescription>
                Tools and integrations available to this agent
              </CardDescription>
            </CardHeader>
            <CardContent>
              {agent.tools && agent.tools.length > 0 ? (
                <div className="space-y-4">
                  {agent.tools.map((tool: any, idx: number) => (
                    <Card key={idx}>
                      <CardHeader>
                        <CardTitle className="text-base">{tool.name || tool.type}</CardTitle>
                        <CardDescription>{tool.description || "No description"}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <Badge variant="outline">{tool.type}</Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  No tools configured yet
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="knowledge">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base</CardTitle>
              <CardDescription>
                Documents and data the agent can access
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-center py-8">
                Knowledge base management coming soon
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Agent Configuration</CardTitle>
              <CardDescription>
                Manage agent settings and parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">System Prompt</label>
                <pre className="mt-2 p-4 bg-muted rounded-lg text-sm overflow-x-auto">
                  {agent.system_prompt}
                </pre>
              </div>
              <div>
                <label className="text-sm font-medium">Settings</label>
                <pre className="mt-2 p-4 bg-muted rounded-lg text-sm overflow-x-auto">
                  {JSON.stringify(agent.settings, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
