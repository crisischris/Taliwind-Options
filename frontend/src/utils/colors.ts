export const numCls  = (v: number)  => v >= 0 ? 'text-success' : 'text-error'
export const beCls   = (p: number)  => p < 25 ? 'text-success' : p < 50 ? 'text-warning' : 'text-error'
export const ivCls   = (iv: number) => iv < 1.0 ? 'text-success' : iv < 1.5 ? 'text-warning' : 'text-error'
export const probCls = (p: number)  => p < 0.10 ? 'text-base-content/50' : p < 0.25 ? 'text-warning' : 'text-success'
