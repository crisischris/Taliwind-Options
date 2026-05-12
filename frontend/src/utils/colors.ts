export const gainCls   = (v: number)  => v >= 0 ? 'text-gain' : 'text-loss'
export const beCls     = (p: number)  => p < 25 ? 'text-gain' : p < 50 ? 'text-caution' : 'text-loss'
export const ivCls     = (iv: number) => iv < 1.0 ? 'text-gain' : iv < 1.5 ? 'text-caution' : 'text-loss'
export const probCls   = (p: number)  => p < 0.10 ? 'text-muted-foreground' : p < 0.25 ? 'text-caution' : 'text-gain'
