import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Bot, Sparkles, Zap, Globe } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="absolute inset-0 -z-10 gradient-mesh opacity-10"></div>

      <div className="text-center max-w-4xl space-y-8">
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="p-4 rounded-2xl bg-gradient-mesh">
              <Sparkles className="h-12 w-12 text-white" />
            </div>
          </div>
          <h1 className="text-6xl font-bold bg-gradient-to-r from-indigo-600 via-azure-500 to-indigo-600 bg-clip-text text-transparent">
            AgentForge
          </h1>
          <p className="text-2xl text-muted-foreground">
            Build intelligent AI agents with natural language
          </p>
        </div>

        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Create powerful AI agents by simply describing what you want. Connect to MCP servers,
          HTTP APIs, and vector databases to build agents that can do anything.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Bot className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-base">Natural Language</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Describe your agent in plain English and AI builds it for you
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Zap className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-base">MCP Integration</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Connect to Model Context Protocol servers for extended capabilities
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Globe className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-base">HTTP & APIs</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Configure HTTP endpoints with variable substitution
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <div className="flex gap-4 justify-center mt-8">
          <Link href="/agents">
            <Button size="lg" className="gradient-indigo text-lg px-8">
              <Sparkles className="mr-2 h-5 w-5" />
              Get Started
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline" className="text-lg px-8">
              View Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
