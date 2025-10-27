"use client"

import { useState } from "react"
import { Zap, Globe, Plus } from "lucide-react"
import { PageHeader, EmptyState } from "@/components/agentforge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export default function IntegrationsPage() {
  const [mcpServers, setMcpServers] = useState<any[]>([])
  const [httpEndpoints, setHttpEndpoints] = useState<any[]>([])

  return (
    <div className="container mx-auto py-8 space-y-8">
      <PageHeader
        icon={Zap}
        title="Integrations"
        description="Connect MCP servers and HTTP endpoints to extend your agents"
      />

      <Tabs defaultValue="mcp" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="mcp">
            <Zap className="mr-2 h-4 w-4" />
            MCP Servers
          </TabsTrigger>
          <TabsTrigger value="http">
            <Globe className="mr-2 h-4 w-4" />
            HTTP Endpoints
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mcp" className="space-y-6">
          {mcpServers.length === 0 ? (
            <EmptyState
              icon={Zap}
              title="No MCP servers connected"
              description="Connect to Model Context Protocol servers to give your agents access to external tools and capabilities"
              action={{
                label: "Connect MCP Server",
                onClick: () => {
                  // TODO: Open dialog
                },
              }}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mcpServers.map((server, idx) => (
                <Card key={idx}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>{server.name}</CardTitle>
                      <Badge>Active</Badge>
                    </div>
                    <CardDescription>{server.url}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground">
                      {server.capabilities?.length || 0} capabilities
                    </div>
                  </CardContent>
                  <CardFooter className="gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      View Tools
                    </Button>
                    <Button variant="ghost" size="sm" className="text-destructive">
                      Disconnect
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="http" className="space-y-6">
          {httpEndpoints.length === 0 ? (
            <EmptyState
              icon={Globe}
              title="No HTTP endpoints configured"
              description="Create HTTP endpoint configurations with variable substitution to connect to any REST API"
              action={{
                label: "Add HTTP Endpoint",
                onClick: () => {
                  // TODO: Open dialog
                },
              }}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {httpEndpoints.map((endpoint, idx) => (
                <Card key={idx}>
                  <CardHeader>
                    <CardTitle>{endpoint.name}</CardTitle>
                    <CardDescription>{endpoint.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{endpoint.method}</Badge>
                      <span className="text-sm font-mono truncate">{endpoint.url}</span>
                    </div>
                  </CardContent>
                  <CardFooter className="gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Test
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      Edit
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
