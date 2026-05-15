import { APP_NAME } from '@/constants/strings'

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-border bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 py-6 text-center text-xs text-muted-foreground space-y-1">
        <p className="font-medium">Not financial advice.</p>
        <p>
          {APP_NAME} is a research tool, not a source of investment recommendations. Nothing on this site
          constitutes a recommendation to buy or sell any security. Options trading involves significant risk
          and is not suitable for all investors. Always conduct your own due diligence and consult a qualified
          financial professional before making any investment decisions.
        </p>
      </div>
    </footer>
  )
}
