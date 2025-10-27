"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Bot, Zap, Settings, LayoutDashboard, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Integrations", href: "/integrations", icon: Zap },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="flex flex-col h-full border-r bg-muted/30">
      {/* Logo */}
      <div className="p-6 border-b">
        <Link href="/agents" className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-mesh">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-azure-500 bg-clip-text text-transparent">
              AgentForge
            </span>
            <p className="text-xs text-muted-foreground">AI Agent Builder</p>
          </div>
        </Link>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`)
          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  isActive && "bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary"
                )}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.name}
              </Button>
            </Link>
          )
        })}
      </div>

      {/* Footer */}
      <div className="p-4 border-t">
        <div className="text-xs text-muted-foreground text-center">
          <p>AgentForge v1.0</p>
          <p className="mt-1">Built with Next.js & FastAPI</p>
        </div>
      </div>
    </nav>
  )
}
