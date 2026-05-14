import * as React from "react"
import { cn } from "@/lib/utils"

const Table = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => {
    const wrapRef = React.useRef<HTMLDivElement>(null)
    const [showFade, setShowFade] = React.useState(false)

    function update() {
      const el = wrapRef.current
      if (!el) return
      const scrollable = el.scrollWidth > el.clientWidth
      const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 4
      setShowFade(scrollable && !atEnd)
    }

    React.useEffect(() => {
      update()
      window.addEventListener('resize', update)
      return () => window.removeEventListener('resize', update)
    }, [])

    return (
      <div className="relative w-full">
        <div ref={wrapRef} className="overflow-x-auto" onScroll={update}>
          <table ref={ref} className={cn("w-full caption-bottom text-sm", className)} {...props} />
        </div>
        {showFade && (
          <div className="absolute right-0 top-0 bottom-0 w-16 pointer-events-none bg-gradient-to-l from-card to-transparent" />
        )}
      </div>
    )
  }
)
Table.displayName = "Table"

const TableHeader = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <thead ref={ref} className={cn("[&_tr]:border-b", className)} {...props} />
  )
)
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <tbody ref={ref} className={cn("[&_tr:last-child]:border-0", className)} {...props} />
  )
)
TableBody.displayName = "TableBody"

const TableRow = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr ref={ref} className={cn("border-b transition-colors hover:bg-muted/50", className)} {...props} />
  )
)
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<HTMLTableCellElement, React.ThHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <th ref={ref} className={cn("h-10 px-3 text-left align-middle font-medium text-muted-foreground whitespace-nowrap", className)} {...props} />
  )
)
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<HTMLTableCellElement, React.TdHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <td ref={ref} className={cn("px-3 py-2 align-middle", className)} {...props} />
  )
)
TableCell.displayName = "TableCell"

export { Table, TableHeader, TableBody, TableRow, TableHead, TableCell }
