import { LucideIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

interface PageHeaderProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
    icon?: LucideIcon
  }
}

export function PageHeader({ icon: Icon, title, description, action }: PageHeaderProps) {
  const ActionIcon = action?.icon

  return (
    <div className="flex items-center justify-between pb-6 border-b">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-gradient-mesh">
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          <p className="text-muted-foreground mt-1">{description}</p>
        </div>
      </div>
      {action && (
        <Button onClick={action.onClick} size="lg" className="gradient-indigo">
          {ActionIcon && <ActionIcon className="mr-2 h-4 w-4" />}
          {action.label}
        </Button>
      )}
    </div>
  )
}
